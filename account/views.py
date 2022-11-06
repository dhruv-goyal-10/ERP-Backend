from rest_framework.response import Response
from rest_framework import status
from rest_framework.views import APIView
from django.contrib.auth import authenticate
from account.serializers import *
from account.models import *
from rest_framework_simplejwt.tokens import RefreshToken
from . emails import *
from datetime import timedelta
from django.utils import timezone
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.permissions import IsAuthenticated
import jwt
from rest_framework.permissions import BasePermission


class IsAdmin(BasePermission):
    def has_permission(self, request, view):
        if not request.method =='GET':
            token = request.META.get('HTTP_AUTHORIZATION', " ").split(' ')[1]
            tokenset = jwt.decode(token, settings.SECRET_KEY, algorithms=['HS256'])
            userID = tokenset['userID']
            user = User.objects.get(userID=userID)
            return user.is_admin
        return True

def get_tokens_for_user(user):
    refresh = RefreshToken.for_user(user)
    refresh['userID'] = user.userID
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
        user = authenticate(userID=userID, password=password)
        if user is not None:
            token = get_tokens_for_user(user)
            if user.is_stu:
                return Response({'token': token, 'msg': 'Login Success - Student'}, status=status.HTTP_200_OK)
            elif user.is_tea:
                return Response({'token': token, 'msg': 'Login Success - Teacher'}, status=status.HTTP_200_OK)
            elif user.is_admin:
                return Response({'token': token, 'msg': 'Login Success - Admin'}, status=status.HTTP_200_OK)
        else:
            return Response({'errors': {'non_field_errors': ['UserID or Password is not Valid']}}, status=status.HTTP_404_NOT_FOUND)


class SendOTPView(APIView):

    def post(self, request):
        serializer = SendOTPSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        email = serializer.data.get('email')
        email = email.lower()
        try:
            user = User.objects.get(email=email)
        except:
            return Response({'msg': 'YOU ARE NOT REGISTERED'}, status=status.HTTP_404_NOT_FOUND)
        try:
            if user.otp_created_at + timedelta(minutes=1) < timezone.now():
                EMAIL.send_otp_via_email(email)
                return Response({'msg': 'OTP SENT! CHECK YOUR MAIL'}, status=status.HTTP_200_OK)
            else:
                return Response({'msg': 'WAIT FOR 1 minute before resending OTP'}, status=status.HTTP_404_NOT_FOUND)
        except:
            return Response({'msg': 'FAILED! TRY AGAIN'}, status=status.HTTP_404_NOT_FOUND)


def matchotp(enteredOTP, generatedOTP, generatedTIME):
    try:
        int(enteredOTP)
        if enteredOTP == generatedOTP:
            if generatedTIME + timedelta(minutes=5) > timezone.now():
                return 'matched'
            else:
                return 'expired'
        else:
            return 'notmatched'
    except ValueError:
        return 'invalid'


def checkpassword(password, confirmpassword):
    if password != confirmpassword:
        return 'different'
    special_char = ['@', '#', '$', '%', '*', '&']
    isSpecial_present = any(char in special_char for char in password)
    isLower_present = any(char.islower() for char in password)
    isUpper_present = any(char.isupper() for char in password)
    isDigit_present = any(char.isdigit() for char in password)
    isLength_ok = True if len(password) >= 6 and len(password) <= 20 else False
    if not (isSpecial_present and isLower_present and isDigit_present and isUpper_present and isLength_ok):
        return 'conditions not fulfilled'


class VerifyOTPView(APIView):

    def post(self, request):
        serializer = VerifyOTPSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        enteredOTP = serializer.data.get('otp')
        email = serializer.data.get('email')
        email = email.lower()
        user = User.objects.get(email=email)
        generatedOTP = (user).otp
        generatedTIME = user.otp_created_at
        otpstatus = matchotp(enteredOTP, generatedOTP, generatedTIME)
        if otpstatus == 'matched':
            return Response({'msg': 'OTP Verification Successful !!'}, status=status.HTTP_200_OK)
        elif otpstatus == 'notmatched':
            return Response({'msg': 'Wrong OTP Entered'}, status=status.HTTP_404_NOT_FOUND)
        elif otpstatus == 'expired':
            user.otp = "****"
            user.save()
            return Response({'msg': 'OTP Expired'}, status=status.HTTP_404_NOT_FOUND)
        else:
            return Response({'msg': 'Enter a valid OTP'}, status=status.HTTP_404_NOT_FOUND)


class ChangePasswordView(APIView):

    def post(self, request):
        serializer = ChangePasswordSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        enteredOTP = serializer.data.get('otp')
        email = serializer.data.get('email')
        password = serializer.data.get('password')
        confirmpassword = serializer.data.get('confirmpassword')

        email = email.lower()
        user = User.objects.get(email=email)

        passwordstatus = checkpassword(password, confirmpassword)
        if passwordstatus == 'conditions not fulfilled':
            context = {'msg': "Your Password must satisfy given conditions"}
            return Response(context, status.HTTP_400_BAD_REQUEST)
        elif passwordstatus == 'different':
            return Response({'msg': "Password and Confirm Password doesn't match"}, status=status.HTTP_400_BAD_REQUEST)

        generatedOTP = user.otp
        generatedTIME = user.otp_created_at
        otpstatus = matchotp(enteredOTP, generatedOTP, generatedTIME)
        if otpstatus == 'matched':
            checkUser = authenticate(userID=user.userID, password=password)
            if checkUser is not None:
                context = {'msg': 'Password entered is same as old one'}
                return Response(context, status.HTTP_400_BAD_REQUEST)

            user.set_password(password)
            user.otp = "****"
            user.save()
            return Response({'msg': 'Password has been changed Successfuly !!'}, status=status.HTTP_200_OK)
        elif otpstatus == 'expired':
            user.otp = "****"
            user.save()
            return Response({'msg': 'RESET PASSWORD TIMEOUT, GENERATE ANOTHER OTP'}, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response({'msg': 'AUTHORISATION FAILED !!'}, status=status.HTTP_400_BAD_REQUEST)


class UpdatePasswordView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def post(self, request):
        token = request.META.get('HTTP_AUTHORIZATION', " ").split(' ')[1]
        tokenset = jwt.decode(token, settings.SECRET_KEY, algorithms=['HS256'])
        userID = tokenset['userID']

        serializer = UpdatePasswordSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        prevpassword = serializer.data.get('prevpassword')
        newpassword = serializer.data.get('newpassword')
        confirmpassword = serializer.data.get('confirmpassword')
        user = User.objects.get(userID=userID)

        check = authenticate(userID=userID, password=prevpassword)
        if check is None:
            context = {'msg': "Previous Password is incorrect"}
            return Response(context, status.HTTP_400_BAD_REQUEST)

        passwordstatus = checkpassword(newpassword, confirmpassword)
        if passwordstatus == 'conditions not fulfilled':
            context = {'msg': "Your Password must satisfy given conditions"}
            return Response(context, status.HTTP_400_BAD_REQUEST)
        elif passwordstatus == 'different':
            return Response({'msg': "Password and Confirm Password doesn't match"}, status=status.HTTP_400_BAD_REQUEST)

        if newpassword == prevpassword:
            context = {'msg': "Your password is same as old one"}
            return Response(context, status.HTTP_400_BAD_REQUEST)

        user.set_password(newpassword)
        user.save()
        return Response({'msg': 'Password has been changed Successfuly !!'}, status=status.HTTP_200_OK)


class UpdateEmail(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def post(self, request):
        token = request.META.get('HTTP_AUTHORIZATION', " ").split(' ')[1]
        tokenset = jwt.decode(token, settings.SECRET_KEY, algorithms=['HS256'])
        userID = tokenset['userID']
        serializer = EmailSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        newemail = serializer.data.get('email')
        newemail = newemail.lower()
        try:
            user = User.objects.get(email=newemail)
            return Response({'msg': 'User with this email already exists'}, status=status.HTTP_400_BAD_REQUEST)
        except:
            EMAIL.send_otp_for_email_verification(userID, newemail)
            return Response({'msg': 'OTP has been sent successfully to your new Mail'}, status=status.HTTP_200_OK)

    def put(self, request):
        token = request.META.get('HTTP_AUTHORIZATION', " ").split(' ')[1]
        tokenset = jwt.decode(token, settings.SECRET_KEY, algorithms=['HS256'])
        userID = tokenset['userID']
        user = User.objects.get(userID=userID)

        serializer = VerifyOTPSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        enteredOTP = serializer.data.get('otp')
        newemail = serializer.data.get('email')

        generatedOTP = (user).otp
        generatedTIME = user.otp_created_at
        otpstatus = matchotp(enteredOTP, generatedOTP, generatedTIME)
        if otpstatus == 'matched':
            user.email = newemail
            user.otp = "****"
            user.save()
            return Response({'msg': 'OTP Verification Successful !!'}, status=status.HTTP_200_OK)
        elif otpstatus == 'notmatched':
            return Response({'msg': 'Wrong OTP Entered'}, status=status.HTTP_404_NOT_FOUND)
        elif otpstatus == 'expired':
            user.otp = "****"
            user.save()
            return Response({'msg': 'OTP Expired'}, status=status.HTTP_404_NOT_FOUND)
        else:
            return Response({'msg': 'Enter a valid OTP'}, status=status.HTTP_404_NOT_FOUND)


class UpdateSectionView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated, IsAdmin]

    def get(self, request, pk):
        token = request.META.get('HTTP_AUTHORIZATION', " ").split(' ')[1]
        tokenset = jwt.decode(token, settings.SECRET_KEY, algorithms=['HS256'])
        userID = tokenset['userID']
        who = userID//100000
        if who == 2:
            updates = Update.objects.filter(showto=3).values(
            ) | Update.objects.filter(showto=1).values()
        elif who == 1:
            updates = Update.objects.filter(showto=3).values(
            ) | Update.objects.filter(showto=2).values()
        else:
            updates = Update.objects.all()
        serializer = UpdateSectionSerializer(updates, many=True)
        SerializerData = [serializer.data]
        return Response(SerializerData)

    def post(self, request, pk):
        # token = request.META.get('HTTP_AUTHORIZATION', " ").split(' ')[1]
        # tokenset = jwt.decode(token, settings.SECRET_KEY, algorithms=['HS256'])
        # userID = tokenset['userID']
        # user = User.objects.get(userID=userID)
        # if not user.is_admin:
        #     return Response({'msg': 'NOT ALLOWED!'}, status=status.HTTP_400_BAD_REQUEST)

        serializer = UpdateSectionSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        if serializer.is_valid():
            serializer.save()
        return Response({'msg': 'UPDATE ADDED'},  status=status.HTTP_200_OK)

    def put(self, request, pk):
        update = Update.objects.get(id=pk)
        serializer = UpdateSectionSerializer(
            instance=update, data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response({'msg': 'UPDATE is modified'},  status=status.HTTP_200_OK)

    def delete(self, request, pk):
        # token = request.META.get('HTTP_AUTHORIZATION', " ").split(' ')[1]
        # tokenset = jwt.decode(token, settings.SECRET_KEY, algorithms=['HS256'])
        # userID = tokenset['userID']
        # user = User.objects.get(userID=userID)
        # if not user.is_admin:
        #     return Response({'msg': 'NOT ALLOWED!'}, status=status.HTTP_400_BAD_REQUEST)
        update = Update.objects.get(id=pk)
        update.delete()
        return Response({'msg': 'UPDATE is deleted'},  status=status.HTTP_200_OK)
