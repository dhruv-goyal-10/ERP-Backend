from rest_framework.response import Response
from rest_framework import status
from rest_framework.views import APIView
from django.contrib.auth import authenticate
from account.serializers import *
from account.models import User, Student
from rest_framework_simplejwt.tokens import RefreshToken
from . emails import *
from datetime import timedelta
from django.utils import timezone

def get_tokens_for_user(user):
    refresh = RefreshToken.for_user(user)
    return {
        'refresh': str(refresh),
        'access': str(refresh.access_token),
    }
    
class UserLoginView(APIView):
  def post(self, request, format=None):
    serializer = UserLoginSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    userID = serializer.data.get('userID')
    password = serializer.data.get('password')
    IN = userID//100000
    print(IN)
    user = authenticate(userID=userID, password=password)
    # print(user.id)
    if user is not None:
        token = get_tokens_for_user(user)
        # token= 'kjdfkljdsq;lkfnkla'
        if IN == 2:
            return Response({'token': token,'msg':'Login Success - Student'}, status=status.HTTP_200_OK)
        elif IN == 1:
            return Response({'token': token,'msg':'Login Success - Teacher'}, status=status.HTTP_200_OK)
        elif IN == 9:
            return Response({'token': token,'msg':'Login Success - Admin'}, status=status.HTTP_200_OK)
    else:
      return Response({'errors':{'non_field_errors':['Email or Password is not Valid']}}, status=status.HTTP_404_NOT_FOUND)


class SendOTPView(APIView):

  def post(self, request):
    serializer=SendOTPSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    email = serializer.data.get('email')
    email=email.lower()
    try:
      user=User.objects.get(email=email)
    except:
      return Response({'msg':'YOU ARE NOT REGISTERED'}, status=status.HTTP_404_NOT_FOUND)
    try:
      print(user)
      if user.otp_created_at + timedelta(minutes=1) < timezone.now():
        EMAIL.send_otp_via_email(email)
        return Response({'msg':'OTP SENT! CHECK YOUR MAIL'}, status=status.HTTP_200_OK)
      else:
        return Response({'msg':'WAIT FOR 1 minute before resending OTP'}, status=status.HTTP_404_NOT_FOUND)
    except:
      return Response({'msg':'FAILED! TRY AGAIN'}, status=status.HTTP_404_NOT_FOUND)


def matchotp(enteredOTP,generatedOTP,generatedTIME):
  try:
    int(enteredOTP)
    if enteredOTP==generatedOTP:
      if generatedTIME + timedelta(minutes=5) > timezone.now():
        return 'matched'
      else:
        return 'expired'
    else:
      return 'notmatched'
  except ValueError :
    return 'invalid'


class VerifyOTPView(APIView):
  
  def post(self, request):
    serializer=VerifyOTPSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    enteredOTP = serializer.data.get('otp')
    email = serializer.data.get('email')
    email=email.lower()
    user=User.objects.get(email=email)
    generatedOTP = (user).otp
    generatedTIME = user.otp_created_at
    otpstatus=matchotp(enteredOTP,generatedOTP,generatedTIME)
    if otpstatus=='matched':
      return Response({'msg':'OTP Verification Successful !!'}, status=status.HTTP_200_OK)
    elif otpstatus=='notmatched':
      return Response({'msg':'Wrong OTP Entered'}, status=status.HTTP_404_NOT_FOUND)
    elif otpstatus=='expired':
      user.otp = "****"
      user.save()
      return Response({'msg':'OTP Expired'}, status=status.HTTP_404_NOT_FOUND)
    else:
      return Response({'msg':'Enter a valid OTP'}, status=status.HTTP_404_NOT_FOUND)


class ChangePasswordView(APIView):
    
  def post(self, request):
    serializer = ChangePasswordSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    enteredOTP = serializer.data.get('otp')
    email = serializer.data.get('email')
    password = serializer.data.get('password')
    confirmpassword = serializer.data.get('confirmpassword')

    email=email.lower()
    user=User.objects.get(email = email)

    special_char= ['@', '#', '$', '%', '*', '&']
    isSpecial_present = any(char in special_char for char in password)
    isLower_present = any(char.islower() for char in password)
    isUpper_present = any(char.isupper() for char in password)
    isDigit_present = any(char.isdigit() for char in password)
    isLength_ok = True if len(password)>=6 and len(password)<=20 else False

    if not isSpecial_present:
      context = {'msg':"Your Password doesn't contain any Special Character"}
      return Response(context, status.HTTP_400_BAD_REQUEST)

    if not isLower_present:
      context = {'msg':"Your Password doesn't contain any Lowercase Letter"}
      return Response(context, status.HTTP_400_BAD_REQUEST)
    
    if not isDigit_present:
      context = {'msg':"Your Password doesn't contain any Numeric Digit"}
      return Response(context, status.HTTP_400_BAD_REQUEST)
    
    if not isUpper_present:
      context = {'msg':"Your Password doesn't contain any Uppercase Letter"}
      return Response(context, status.HTTP_400_BAD_REQUEST)

    if not isLength_ok:
      context = {'msg':"Your Password doesn't meet the length requirements"}
      return Response(context, status.HTTP_400_BAD_REQUEST)
    
    generatedOTP = user.otp
    generatedTIME = user.otp_created_at
    otpstatus=matchotp(enteredOTP,generatedOTP,generatedTIME)
    if otpstatus=='matched':
      if password==confirmpassword:

        checkUser = authenticate(userID=user.userID, password=password)
        if checkUser is not None:
          context = {'msg':'Password entered is same as old one'}
          return Response(context, status.HTTP_400_BAD_REQUEST)

        user.set_password(password)
        user.otp="****"
        user.save()
        return Response({'msg':'Password has been changed Successfuly !!'}, status=status.HTTP_200_OK)
      else:
        return Response({'msg':"Password and Confirm Password doesn't match"}, status=status.HTTP_400_BAD_REQUEST)
    elif otpstatus=='expired':
      user.otp="****"
      user.save()
      return Response({'msg':'RESET PASSWORD TIMEOUT, GENERATE ANOTHER OTP'}, status=status.HTTP_200_OK)
    else:
      return Response({'msg':'AUTHORISATION FAILED !!'}, status=status.HTTP_200_OK)


class AddStudent(APIView):
    
  def post(self, request):
    serializer = AddStudentSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    email = serializer.data.get('email')
    userID = serializer.data.get('userID')
    name = serializer.data.get('name')
    DOB = serializer.data.get('DOB')

    # Default Password --> first_name in lowercase + @ + DOB(YYYYMMDD)
    password=name.split(" ")[0].lower() + '@' + DOB.replace("-","")

    user = User.objects.create_user(
            email=email,
            userID=userID,
            name=name,
        )
    user.set_password(password)
    user.is_stu=True
    user.save()

    Student(
            userID=userID,
            name=name,
            DOB=DOB,
        ).save()

    return Response({'msg':'Student Created Successfully'}, status=status.HTTP_200_OK)