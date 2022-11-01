from rest_framework import serializers
from account.models import User 


class UserLoginSerializer(serializers.Serializer):
  userID = serializers.IntegerField()
  password = serializers.CharField(min_length=8, max_length=255)


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


class AddStudentSerializer(serializers.Serializer):
  email = serializers.EmailField(max_length=255)
  name = serializers.CharField(max_length=200)
  DOB = serializers.DateField()


class AddTeacherSerializer(serializers.Serializer):
  email = serializers.EmailField(max_length=255)
  name = serializers.CharField(max_length=200)
  DOB = serializers.DateField()


class UpdatePasswordSerializer(serializers.Serializer):
  prevpassword = serializers.CharField(min_length=8, max_length=255)
  newpassword = serializers.CharField(min_length=8, max_length=255)
  confirmpassword = serializers.CharField(min_length=8, max_length=255)