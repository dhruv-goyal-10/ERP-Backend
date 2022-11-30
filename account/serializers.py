from rest_framework import serializers
from rest_framework.serializers import ModelSerializer
from account.models import *


class UserLoginSerializer(serializers.Serializer):
    userID = serializers.IntegerField()
    password = serializers.CharField(min_length=8, max_length=255)


class EmailSerializer(serializers.Serializer):
    email = serializers.EmailField()


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
        fields = ['sex', 'DOB', 'picture', 'blood_group', 'pincode', 'address', 'city', 'state',
                  'student_phone', 'father_name', 'father_phone', 'mother_name', 'mother_phone', ]


class TeacherProfileSerializer(ModelSerializer):
    class Meta:
        model = Teacher
        fields = ['sex', 'DOB', 'picture', 'blood_group',
                  'pincode', 'address', 'city', 'state', 'teacher_phone']


class UpdateSectionSerializer(ModelSerializer):

    class Meta:
        model = Update
        fields = '__all__'


class AssignTimeSerializer(ModelSerializer):

    class Meta:
        model = AssignTime
        fields = ['period', 'day', 'assign']


class AssignClassSerializer(ModelSerializer):

    class Meta:
        model = AssignClass
        fields = '__all__'


class CreateAttendanceSerializer(serializers.Serializer):
    start_date = serializers.DateField()
    end_date = serializers.DateField()
    class_id = serializers.CharField(max_length=10)


class StudentAttendanceSerializer(ModelSerializer):
    class Meta:
        model = StudentAttendance
        fields = '__all__'


class AssignsSerializer(serializers.Serializer):
    class_id = serializers.CharField(max_length=10)
    subject_code = serializers.CharField()
    teacher_userID = serializers.IntegerField()


class TimeSlotSerializer(serializers.Serializer):
    period = serializers.ChoiceField(choices=TIME_SLOTS)
    day = serializers.ChoiceField(choices=DAYS)


def validate_file_extension(value):
    import os
    from django.core.exceptions import ValidationError
    ext = os.path.splitext(value.name)[1]  # [0] returns path+filename
    valid_extensions = ['.xlsx', '.xls', '.csv']
    if not ext.lower() in valid_extensions:
        raise ValidationError('Unsupported file extension.')


class TempSerializer(serializers.Serializer):
    field_name = serializers.FileField(validators=[validate_file_extension])


class DepartmentSerializer(ModelSerializer):

    class Meta:
        model = Department
        fields = '__all__'


class ClassSerializer(ModelSerializer):
    class Meta:
        model = Class
        fields = '__all__'


class SubjectSerializer(ModelSerializer):
    class Meta:
        model = Subject
        fields = '__all__'


class StudentSubjectAttendance(ModelSerializer):
    date = serializers.DateField(source='classattendance.date')
    day = serializers.CharField(source='classattendance.assign.day')
    period = serializers.CharField(source='classattendance.assign.period')

    class Meta:
        model = StudentAttendance
        fields = ['date', 'day', 'period', 'is_present']


class FeedbackSerializer(ModelSerializer):
    class Meta:
        model = TeacherFeedback
        fields = '__all__'


class TeacherList(ModelSerializer):
    class Meta:
        model = Teacher
        fields = ['userID', 'name']


class StudentList(ModelSerializer):
    class Meta:
        model = Student
        fields = ['userID', 'name']


class StudentFeedbackSerializer(ModelSerializer):
    studentname = serializers.CharField(source = 'student.name')
    class Meta:
        model = StudentFeedback
        fields = ['studentname', 'feed']


class AttendanceObjectsSerializer(ModelSerializer):
    period = serializers.CharField(source = 'assign.period')
    class_id = serializers.CharField(source = 'assign.class_id.id')
    subject_name = serializers.CharField(source = 'assign.assign.subject.name')
    subject_code = serializers.CharField(source = 'assign.assign.subject.code')
    teacher_userID = serializers.CharField(source = 'assign.assign.teacher.userID')
    class Meta:
        model = ClassAttendance
        fields = ['date', 'period', 'class_id', 'subject_name', 'subject_code', 'teacher_userID', 'status']