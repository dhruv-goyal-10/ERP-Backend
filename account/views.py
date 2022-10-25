from rest_framework.response import Response
from rest_framework import status
from rest_framework.views import APIView
from django.contrib.auth import authenticate
from account.serializers import *
from account.models import User
from . emails import *

# Create your views here.
class UserLoginView(APIView):
  def post(self, request, format=None):
    serializer = UserLoginSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    userID = serializer.data.get('userID')
    password = serializer.data.get('password')
    user = authenticate(userID=userID, password=password)
    if user is not None:
      return Response({'msg':'Login Success'}, status=status.HTTP_200_OK)
    else:
      return Response({'errors':{'non_field_errors':['Email or Password is not Valid']}}, status=status.HTTP_404_NOT_FOUND)


class SendOTPView(APIView):

  def post(self, request, format=None):
    serializer=SendOTPSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    email = serializer.data.get('email')
    try:
      email=User.objects.get(email=email)
    except:
      return Response({'msg':'YOU ARE NOT REGISTERED'}, status=status.HTTP_404_NOT_FOUND)
    try:
      EMAIL.send_otp_via_email(email)
      return Response({'msg':'OTP SENT TO USER '+str(email.userID)}, status=status.HTTP_200_OK)
    except:
      return Response({'msg':'FAILED! TRY AGAIN'}, status=status.HTTP_404_NOT_FOUND)


class VerifyOTPView(APIView):
  
  def post(self, request, ID):
    serializer=VerifyOTPSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    enteredOTP = serializer.data.get('otp')
    user=User.objects.get(userID=ID)
    generatedOTP = (user).otp
    try:
      int(enteredOTP)
      if enteredOTP==generatedOTP:
        user.otp="0000"
        user.save()
        return Response({'msg':'OTP Verification Successful !!'}, status=status.HTTP_200_OK)
      else:
        return Response({'msg':'Wrong OTP Entered'}, status=status.HTTP_404_NOT_FOUND)
    except:
        return Response({'msg':'Enter a valid OTP'}, status=status.HTTP_404_NOT_FOUND)