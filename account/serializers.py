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


class AddStudentSerializer(ModelSerializer):
    email = serializers.EmailField(max_length=255)

    class Meta:
        model = Student
        fields = ['name', 'class_id', 'email', 'DOB']


class AddTeacherSerializer(ModelSerializer):
    email = serializers.EmailField(max_length=255)

    class Meta:
        model = Teacher
        fields = ['name', 'department', 'email', 'DOB']


class UpdatePasswordSerializer(serializers.Serializer):
    prevpassword = serializers.CharField(min_length=8, max_length=255)
    newpassword = serializers.CharField(min_length=8, max_length=255)
    confirmpassword = serializers.CharField(min_length=8, max_length=255)


class StudentProfileSerializer(ModelSerializer):
    class Meta:
        model = Student
        fields = ['name', 'sex', 'DOB', 'picture', 'blood_group', 'pincode', 'address', 'city', 'state',
                  'student_phone', 'father_name', 'father_phone', 'mother_name', 'mother_phone', ]


class TeacherProfileSerializer(ModelSerializer):
    class Meta:
        model = Teacher
        fields = ['name', 'sex', 'DOB', 'picture', 'blood_group',
                  'pincode', 'address', 'city', 'state', 'teacher_phone']


class UpdateSectionSerializer(ModelSerializer):

    class Meta:
        model = Update
        fields = '__all__'


class SubjectSectionSerializer(ModelSerializer):

    class Meta:
        model = Subject
        fields = '__all__'


class TeacherSectionSerializer(ModelSerializer):

    class Meta:
        model = Teacher
        fields = '__all__'


class AssignTimeSerializer(ModelSerializer):

    class Meta:
        model = AssignTime
        fields = ['period', 'day', 'assign']


class AssignClassSerializer(ModelSerializer):

    class Meta:
        model = AssignClass
        fields = '__all__'
