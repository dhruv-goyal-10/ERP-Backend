from rest_framework import serializers
from account.models import User 


class UserLoginSerializer(serializers.ModelSerializer):
  userID = serializers.IntegerField()
  class Meta:
    model = User
    fields = ['userID','password']


class SendOTPSerializer(serializers.Serializer):
  email = serializers.EmailField(max_length=255)


class VerifyOTPSerializer(serializers.Serializer):
  email = serializers.EmailField(max_length=255)
  otp = serializers.CharField(min_length=4, max_length=4)


class ChangePasswordSerializer(serializers.Serializer):
  email = serializers.EmailField(max_length=255)
  otp = serializers.CharField(min_length=4, max_length=4)
  password = serializers.CharField(min_length=8, max_length=255)
  confirmpassword = serializers.CharField(min_length=8, max_length=255)
