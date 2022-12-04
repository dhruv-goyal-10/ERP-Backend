from rest_framework.serializers import *
from account.serializers import return_user
from account.models import *
from django.shortcuts import get_object_or_404


class StudentProfileSerializer(ModelSerializer):
    class Meta:
        model = Student
        exclude = ['user', 'class_id','userID', 'name']


class TeacherFeedbackInstanceSerializer(ModelSerializer):
    userID = IntegerField(source = 'teacher.userID')
    class Meta:
        model = TeacherFeedback
        fields = ['userID', 'feed']


class TeacherFeedbackListSerializer(ListSerializer):
    child = TeacherFeedbackInstanceSerializer()

    def create(self, validated_data):
        student = get_object_or_404(Student, user = return_user(self.context.get('request'))) 
        queryset = TeacherFeedback.objects.filter(student = student)
        response = []
        for data in validated_data:
            data['teacher'] = get_object_or_404(Teacher, userID = data['teacher']['userID'])
            data['student'] = student
            feedback = queryset.filter(teacher = data['teacher'])
            if feedback.exists():
                response.append(self.child.update(feedback[0], data))
            else:
                response.append(self.child.create(data))
        return response


class StudentSubjectAttendance(ModelSerializer):
    date = DateField(source='classattendance.date')
    day = CharField(source='classattendance.assign.day')
    period = CharField(source='classattendance.assign.period')

    class Meta:
        model = StudentAttendance
        fields = ['date', 'day', 'period', 'is_present']