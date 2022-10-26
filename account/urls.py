
from django.contrib import admin
from django.urls import path, include
from account.views import *

urlpatterns = [ 
    path('login/',UserLoginView.as_view(), name='login'),
    path('sendotp/',SendOTPView.as_view(), name='sendotp'),
    path('verifyotp/',VerifyOTPView.as_view(), name='verifyotp'),
    path('changepassword/',ChangePasswordView.as_view(), name='changepassword')
]
