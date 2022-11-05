from rest_framework import serializers
from rest_framework.serializers import ModelSerializer
from account.models import *


class UserLoginSerializer(serializers.Serializer):
  userID = serializers.IntegerField()
  password = serializers.CharField(min_length=8, max_length=255)


class EmailSerializer(ModelSerializer):
    class Meta:
        model = User
        fields = ['email']


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


class AddTeacherSerializer(serializers.Serializer):
  email = serializers.EmailField(max_length=255)
  name = serializers.CharField(max_length=255)
  DOB = serializers.DateField()
  department = serializers.CharField(max_length=255)
  sex = serializers.CharField(max_length=1)

class AddStudentSerializer(serializers.Serializer):
  email = serializers.EmailField(max_length=255)
  name = serializers.CharField(max_length=255)
  DOB = serializers.DateField()
  assignedclass = serializers.CharField(max_length=10)
  sex = serializers.CharField(max_length=1)

class UpdatePasswordSerializer(serializers.Serializer):
  prevpassword = serializers.CharField(min_length=8, max_length=255)
  newpassword = serializers.CharField(min_length=8, max_length=255)
  confirmpassword = serializers.CharField(min_length=8, max_length=255)

class StudentProfileSerializer(ModelSerializer):
    class Meta:
        model = Student
        fields = ['name', 'sex', 'DOB', 'userID', 'picture', 'blood_group', 'pincode', 'address', 'city', 'state',
                  'student_phone', 'father_name', 'father_phone', 'mother_name', 'mother_phone',]


class UpdateSectionSerializer(ModelSerializer):

  class Meta:
    model = Update
    fields = '__all__'