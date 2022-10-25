
from django.contrib import admin
from django.urls import path, include
from account.views import *

urlpatterns = [ 
    path('login/',UserLoginView.as_view(), name='login'),
    path('resetpassword/',SendOTPView.as_view(), name='resetpassword'),
    path('verifyotp/<str:ID>/',VerifyOTPView.as_view(), name='verifyotp')
]
