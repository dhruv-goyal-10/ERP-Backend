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

  bool=False

  def get(self, request, format=None):
    serializer=SendOTPSerializer(data=request.data)
    serializer.is_valid(raise_exception=True) 
    userID = serializer.data.get('userID')
    email = serializer.data.get('email')
    try:
      user=User.objects.get(email=email)
      email = user.email
      self.bool=True
      self.post(email)
      self.bool=False
      return Response({'msg':'OTP SENT'}, status=status.HTTP_200_OK)
    except:
      return Response({'errors':{'non_field_errors':['UserID or Email is not Valid']}}, status=status.HTTP_404_NOT_FOUND)

  def post(self, email):
    if self.bool:
      send_otp_via_email(email)
    else:
      pass 