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
from . custom_permissions import *
import re
from django.shortcuts import get_object_or_404
from teacher.views import return_user
from django.contrib.postgres.search import SearchHeadline, TrigramWordSimilarity
from django.db.models.functions import Greatest
from rest_framework.generics import *


class UserLoginView(APIView):

    def post(self, request):
        serializer = UserLoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        try:
            data = serializer.save()
            return Response(data)
        
        except ValidationError as e:
            if  e.code == "invalid":
                return Response({'Msg' : "Login Unsuccessful" , 
                                'Error': 'UserID or Password is not Valid'}, 
                                 status=status.HTTP_404_NOT_FOUND)
            else:
                return Response({'Msg' : "Some error occured from our side. Please try after some time!",
                                 'Error' : ''},
                                 status=status.HTTP_404_NOT_FOUND)


class SendOTPView(APIView):

    def post(self, request):
        serializer = SendOTPSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        try:
            serializer.save()
        except ValidationError as e:
            
            if e.code == "wait":
                return Response({'msg': 'WAIT FOR 1 minute before resending OTP'}, status=status.HTTP_404_NOT_FOUND)
            elif e.code == "fail":
                return Response({'msg': 'FAILED! TRY AGAIN'}, status=status.HTTP_404_NOT_FOUND)
            
        return Response({'msg': 'OTP SENT! CHECK YOUR MAIL'}, status=status.HTTP_200_OK)

class VerifyOTPView(APIView):

    def post(self, request):
        serializer = VerifyOTPSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        try:
            serializer.save()
        except ValidationError as e:
            if e.code == "expired":
                return Response({'msg': 'OTP Expired'}, status=status.HTTP_200_OK)
            elif e.code == "notmatched":
                return Response({'msg': "Wrong OTP entered"}, status=status.HTTP_200_OK)

        return Response({'msg': 'OTP Verification Successful !!'}, status=status.HTTP_200_OK)
    
class ForgotPasswordView(APIView):

    def patch(self, request):
        serializer = ForgotPasswordSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        try:
            serializer.save()
            return Response({'msg': 'Password has been changed Successfuly !!'}, status=status.HTTP_200_OK)
        except ValidationError: 
            return Response({'msg': 'Password entered is same as old one'}, status.HTTP_400_BAD_REQUEST)
        
class UpdatePasswordView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def patch(self, request):
        userID = return_user(request).userID
        serializer = UpdatePasswordSerializer(data=request.data, context={'userID': userID})
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response({'msg': 'Password has been changed Successfuly !!'}, status=status.HTTP_200_OK)


# class UpdateEmail(APIView):
#     authentication_classes = [JWTAuthentication]
#     permission_classes = [IsAuthenticated]

#     def post(self, request):
#         loginuser = return_user(request)
#         serializer = EmailSerializer(data=request.data)
#         serializer.is_valid(raise_exception=True)
#         newemail = serializer.data.get('email')
#         newemail = newemail.lower()
#         user = User.objects.filter(email=newemail)
#         if user.exists():
#             if loginuser.email == newemail:
#                 return Response({'msg': 'Previous Email entered'}, status=status.HTTP_400_BAD_REQUEST)
#             return Response({'msg': 'User with this email already existsss'}, status=status.HTTP_400_BAD_REQUEST)
#         elif checkemail(newemail):
#             return Response({'msg': 'Domain not allowed'}, status=status.HTTP_400_BAD_REQUEST)
#         else:
#             EMAIL.send_otp_for_email_verification(loginuser, newemail)
#             return Response({'msg': 'OTP has been sent successfully to your new Mail'}, status=status.HTTP_200_OK)

#     def put(self, request):
#         user = return_user(request)

#         serializer = VerifyOTPSerializer(data=request.data)
#         serializer.is_valid(raise_exception=True)
#         enteredOTP = serializer.data.get('otp')
#         newemail = serializer.data.get('email')

#         otpstatus = matchotp(enteredOTP, user)
#         if otpstatus == 'matched':
#             user.email = newemail
#             user.save()
#             otprelation = OTP.objects.get(user=user)
#             otprelation.isexpired = True
#             otprelation.save()
#             return Response({'msg': 'OTP Verification Successful !!'}, status=status.HTTP_200_OK)
#         elif otpstatus == 'notmatched':
#             return Response({'msg': 'Wrong OTP Entered'}, status=status.HTTP_404_NOT_FOUND)
#         elif otpstatus == 'expired':
#             return Response({'msg': 'OTP Expired'}, status=status.HTTP_404_NOT_FOUND)
#         else:
#             return Response({'msg': 'Enter a valid OTP'}, status=status.HTTP_404_NOT_FOUND)


class UpdateSectionView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated, IsAdmin_but_get_allowed_to_all]

    def get(self, request, pk):
        userID = return_user(request).userID
        who = userID//100000
        if who == 1:
            updates = Update.objects.filter(
                showto=3) | Update.objects.filter(showto=2)
        elif who == 2:
            updates = Update.objects.filter(
                showto=3) | Update.objects.filter(showto=1)
        else:
            updates = Update.objects.all()
        search = request.GET.get('search') or ''
        if search:
            SerializerData = []
            updates = updates.annotate(similarity=Greatest(TrigramWordSimilarity(search, 'description'), TrigramWordSimilarity(
                search, 'title'))).filter(similarity__gt=0.3).order_by('-similarity')
            updates = updates.annotate(titleheadline=SearchHeadline('title', search, highlight_all=True),
                                       descriptionheadline=SearchHeadline('description', search, highlight_all=True))
            for update in updates:
                SerializerData += [[update.titleheadline,
                                    update.descriptionheadline]]
        else:
            serializer = UpdateSectionSerializer(updates, many=True)
            SerializerData = [serializer.data]
        return Response(SerializerData)

    def post(self, request, pk):
        serializer = UpdateSectionSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        if serializer.is_valid():
            serializer.save()
        return Response({'msg': 'UPDATE ADDED'},  status=status.HTTP_200_OK)

    def put(self, request, pk):
        pk = request.data.get("id")
        update = Update.objects.get(id=pk)
        serializer = UpdateSectionSerializer(
            instance=update, data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response({'msg': 'UPDATE is modified'},  status=status.HTTP_200_OK)

    def delete(self, request, pk):
        update = get_object_or_404(Update, id=pk)
        update.delete()
        return Response({'msg': 'UPDATE is deleted'},  status=status.HTTP_200_OK)

from django.shortcuts import HttpResponse
from .tasks import test_funciton
def test(request):
    test_funciton.delay()
    return HttpResponse("DONE")