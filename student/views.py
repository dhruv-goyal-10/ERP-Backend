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


    def put(self, request):
        student = check_if_student_and_return_userID(request)
        if not student:
            return Response({'msg': 'NOT ALLOWED'},  status=status.HTTP_400_BAD_REQUEST)
        serializer = FeedbackSerizer(data = request.data)
        serializer.is_valid(raise_exception=True)
        userID = serializer.data.get('userID')
        feed = request.data.get('feed')
        try:
            teacher = Teacher.objects.get(userID=userID)
        except:
            return Response({'msg': 'teacher does not exist'},  status=status.HTTP_400_BAD_REQUEST)
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
    
TIME_SLOTS = ['8:30 - 9:20','9:20 - 10:10', '11:00 - 11:50', '11:50 - 12:40', '1:30 - 2:20']

DAYS = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday']
    
class TimeTable(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        pk = check_if_student_and_return_userID(request)
        if(pk is False):
            return Response({'msg': 'Invalid credentials'},  status=status.HTTP_200_OK)
        pk = pk.class_id.id
        
        list = []
        for i in TIME_SLOTS:
            for j in DAYS:
                time=AssignTime.objects.filter(period=i, day=j, assign__class_id= pk)
                
                if time.exists():
                    time=time[0]
                    dict={}
                    dict= {"class" : time.assign.class_id.id, "subject" : time.assign.subject.name, "teacher" : time.assign.teacher.name, "period" : i, "day" : j}
                else:
                    dict={}
                    dict= {"class" : pk, "subject" : "", "teacher" : "", "period" : i, "day" : j}
                list.append(dict)            
        return Response(list,  status=status.HTTP_200_OK) 
    
    
class StudentOverallAttendance(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        student = check_if_student_and_return_userID(request)
        userID= student.userID
        class_id= student.class_id
        subjects= AssignClass.objects.filter(class_id=class_id)
        list=[]
        for subject in subjects:
            subject = subject.subject
            subject_name= subject.name
            subject_code= subject.code
            total_classes = ClassAttendance.objects.filter(assign__class_id=class_id, 
                                                            assign__assign__subject__code = subject_code,
                                                            status=True
                                                            ).count()     
            attended_classes = StudentAttendance.objects.filter(classattendance__assign__class_id=class_id, 
                                                            subject__code = subject_code,
                                                            classattendance__status=True,
                                                            student__userID=userID,
                                                            is_present=True).count()
            if total_classes == 0:
                attendance_percent = 0
            else:
                attendance_percent = round(attended_classes / total_classes * 100, 1)
            dict={}
            dict={
                "subject_code": subject_code,
                "subject_name": subject_name,
                "attended_classes": attended_classes,
                "total_classes": total_classes,
                "attendance_percent": attendance_percent
            }
            list.append(dict)
            # print(total_classes, attended_classes, attendance_percent)
        return Response(list, status=status.HTTP_200_OK)
        
