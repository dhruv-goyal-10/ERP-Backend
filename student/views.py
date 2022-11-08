from rest_framework.response import Response
from rest_framework import status
from rest_framework.views import APIView
from account.serializers import *
from account.models import *
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.permissions import IsAuthenticated
import jwt
from django.conf import settings


def check_if_student_and_return_userID(request):
    token = request.META.get('HTTP_AUTHORIZATION', " ").split(' ')[1]
    tokenset = jwt.decode(token, settings.SECRET_KEY, algorithms=['HS256'])
    userID = tokenset['userID']
    try:
        student = Student.objects.get(userID=userID)
        return student
    except:
        return False
    
class SProfileDetails(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request):
        userID = check_if_student_and_return_userID(request).userID

        student = Student.objects.get(userID=userID)
        serializer = StudentProfileSerializer(student, many=False)

        user = User.objects.get(userID=userID)
        eserializer = EmailSerializer(user, many=False)

        return Response(serializer.data | eserializer.data)

    def put(self, request):
        userID = check_if_student_and_return_userID(request).userID
        student = Student.objects.get(userID=userID)
        serializer = StudentProfileSerializer(student, data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        # Updating the name in User Model
        name = serializer.validated_data.get('name')
        user = User.objects.get(userID=userID)
        user.name = name
        user.save()

        return Response(serializer.data, status=status.HTTP_202_ACCEPTED)

class TeacherFeedbackView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]


    def put(self, request, teacher):
        student = check_if_student_and_return_userID(request)
        if not student:
            return Response({'msg': 'NOT ALLOWED'},  status=status.HTTP_400_BAD_REQUEST)
        try:
            teacher = Teacher.objects.get(userID=teacher)
        except:
            return Response({'msg': 'teacher does not exist'},  status=status.HTTP_400_BAD_REQUEST)
        feed = request.data.get('feed')
        if feed is None:
            feed = 3
        try:
            feedback = TeacherFeedback.objects.get(teacher=teacher, student = student)
            feedback.feed=feed
            feedback.save()
            return Response({'msg': 'Feedback Modified Successfully !!'}, status=status.HTTP_200_OK)
        except:
            TeacherFeedback(
                teacher = teacher,
                student = student,
                feed = feed
            ).save()
            return Response({'msg': 'Feedback Submitted Successfully !!'}, status=status.HTTP_200_OK)
    
class TimeTable(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        
        pk = check_if_student_and_return_userID(request).class_id.id
        times = AssignTime.objects.filter(assign__class_id=pk)
        classes = AssignClass.objects.filter(class_id=pk)
        list = []
        for klass in classes:
            dict={}
            dict= {"class" : klass.class_id.id, "subject" : klass.subject.name, "teacher" : klass.teacher.name}
            for time in times:
                ndict=dict
                if time.assign.id == klass.id:
                    ndict|= {"period" : time.period, "day" : time.day}
                    list.append(ndict)
        return Response(list,  status=status.HTTP_200_OK)

