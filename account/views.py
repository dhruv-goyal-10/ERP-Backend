from rest_framework.response import Response
from rest_framework import status
from rest_framework.views import APIView
from django.contrib.auth import authenticate
from account.serializers import *
from account.models import User
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
    user = authenticate(userID=userID, password=password)
    if user is not None:
        token = get_tokens_for_user(user)
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
      email=User.objects.get(email=email)
    except:
      return Response({'msg':'YOU ARE NOT REGISTERED'}, status=status.HTTP_404_NOT_FOUND)
    try:
      EMAIL.send_otp_via_email(email)
      return Response({'msg':'OTP SENT! CHECK YOUR MAIL'}, status=status.HTTP_200_OK)
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
      return Response({'msg':'OTP Expired'}, status=status.HTTP_404_NOT_FOUND)
    else:
      return Response({'msg':'Enter a valid OTP'}, status=status.HTTP_404_NOT_FOUND)


class ChangePasswordView(APIView):
    
  def post(self, request):
    serializer = ChangePasswordSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    enteredOTP = serializer.data.get('otp')
    email = serializer.data.get('email')
    email=email.lower()
    user=User.objects.get(email = email)
    password = serializer.data.get('password')
    confirmpassword = serializer.data.get('confirmpassword')
    generatedOTP = user.otp
    generatedTIME = user.otp_created_at
    otpstatus=matchotp(enteredOTP,generatedOTP,generatedTIME)
    if otpstatus=='matched':
      if password==confirmpassword:
          user.set_password(password)
          user.otp="****"
          user.save()
          return Response({'msg':'Password has been changed Successfuly !!'}, status=status.HTTP_200_OK)
    elif otpstatus=='expired':
      return Response({'msg':'RESET PASSWORD TIMEOUT, GENERATE ANOTHER OTP'}, status=status.HTTP_200_OK)
    else:
      return Response({'msg':'AUTHORISATION FAILED !!'}, status=status.HTTP_200_OK)