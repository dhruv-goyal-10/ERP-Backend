
from django.contrib import admin
from django.urls import path, include
from account.views import *
from rest_framework_simplejwt.views import (
    TokenRefreshView,
)

urlpatterns = [ 
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('login/',UserLoginView.as_view(), name='login'),
    path('sendotp/',SendOTPView.as_view(), name='sendotp'),
    path('verifyotp/',VerifyOTPView.as_view(), name='verifyotp'),
    path('changepassword/',ChangePasswordView.as_view(), name='changepassword'),
    path('addstudent/',AddStudent.as_view(), name='addStudent'),
    path('addteacher/',AddTeacher.as_view(), name='addTeacher'),
    path('updatepassword/',UpdatePasswordView.as_view(), name='updatepassword'),
    path('profiledetails/<str:userID>',ProfileDetails.as_view(), name='profiledetails'),
]
