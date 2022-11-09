from django.contrib import admin
from django.urls import path
from account.views import *
from rest_framework_simplejwt.views import (
    TokenRefreshView,
)

urlpatterns = [
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('login/', UserLoginView.as_view(), name='login'),
    path('sendotp/', SendOTPView.as_view(), name='sendotp'),
    path('verifyotp/', VerifyOTPView.as_view(), name='verifyotp'),
    path('changepassword/', ChangePasswordView.as_view(), name='changepassword'),
    path('updatepassword/', UpdatePasswordView.as_view(), name='updatepassword'),
    path('updateemail/', UpdateEmail.as_view(), name='updateemail'),
    path('updatesection/',UpdateSectionView.as_view(), name='updatesection'),
]
