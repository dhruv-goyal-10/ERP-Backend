
from django.contrib import admin
from django.urls import path, include
from account.views import UserLoginView

urlpatterns = [ 
    path('login/',UserLoginView.as_view(), name='login'),
]
