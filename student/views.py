from rest_framework.response import Response
from rest_framework import status
from rest_framework.views import APIView
from account.serializers import *
from account.models import *
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import get_object_or_404
from teacher.views import return_user


class SProfileDetails(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = return_user(request)
        student = get_object_or_404(Student, user=user)
        serializer = StudentProfileSerializer(student, many=False)
        eserializer = EmailSerializer(user, many=False)
        return Response(serializer.data | eserializer.data)

    def put(self, request):
        user = return_user(request)
        student = get_object_or_404(Student, user=user)
        serializer = StudentProfileSerializer(student, data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        # Updating the name in User Model
        name = serializer.validated_data.get('name')
        user.name = name
        user.save()
        return Response(serializer.data, status=status.HTTP_202_ACCEPTED)


class TeacherFeedbackView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def put(self, request):
        user = return_user(request)
        student = get_object_or_404(Student, user=user)
        serializer = FeedbackSerizer(data=request.data)
        serializer.is_valid(raise_exception=True)
        userID = serializer.data.get('userID')
        feed = serializer.data.get('feed')
        teacher = get_object_or_404(Teacher, userID=userID)
        feedback = TeacherFeedback.objects.filter(
            teacher=teacher, student=student)
        if feedback.exists():
            feedback = feedback[0]
            feedback.feed = feed
            feedback.save()
            return Response({'msg': 'Feedback Modified Successfully !!'}, status=status.HTTP_200_OK)
        TeacherFeedback(teacher=teacher, student=student, feed=feed).save()
        return Response({'msg': 'Feedback Submitted Successfully !!'}, status=status.HTTP_200_OK)


TIME_SLOTS = ['8:30 - 9:20', '9:20 - 10:10',
              '11:00 - 11:50', '11:50 - 12:40', '1:30 - 2:20']
DAYS = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday']


class TimeTable(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = return_user(request)
        student = get_object_or_404(Student, user=user)
        pk = student.class_id.id
        list = []
        for i in TIME_SLOTS:
            for j in DAYS:
                time = AssignTime.objects.filter(
                    period=i, day=j, assign__class_id=pk)

                if time.exists():
                    time = time[0]
                    dict = {}
                    dict = {"class": time.assign.class_id.id, "subject": time.assign.subject.name,
                            "teacher": time.assign.teacher.name, "period": i, "day": j}
                else:
                    dict = {}
                    dict = {"class": pk, "subject": "",
                            "teacher": "", "period": i, "day": j}
                list.append(dict)
        return Response(list,  status=status.HTTP_200_OK)


class StudentOverallAttendance(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = return_user(request)
        student = get_object_or_404(Student, user=user)
        class_id = student.class_id
        subjects = AssignClass.objects.filter(class_id=class_id)
        list = []
        for subject in subjects:
            subject_name = subject.subject.name
            subject_code = subject.subject.code
            total_classes = ClassAttendance.objects.filter(assign__class_id=class_id,
                                                           assign__assign__subject__code=subject_code,
                                                           status=True
                                                           ).count()
            attended_classes = StudentAttendance.objects.filter(classattendance__assign__class_id=class_id,
                                                                subject__code=subject_code,
                                                                classattendance__status=True,
                                                                student__userID=student.userID,
                                                                is_present=True).count()
            if total_classes == 0:
                attendance_percent = 0
            else:
                attendance_percent = round(
                    attended_classes / total_classes * 100, 1)
            dict = {}
            dict = {
                "subject_code": subject_code,
                "subject_name": subject_name,
                "attended_classes": attended_classes,
                "total_classes": total_classes,
                "attendance_percent": attendance_percent
            }
            list.append(dict)
            # print(total_classes, attended_classes, attendance_percent)
        return Response(list, status=status.HTTP_200_OK)


class StudentSubjectAttendance(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = return_user(request)
        student = get_object_or_404(Student, user=user)
        userID = student.userID
        class_id = student.class_id
        serializer = StudentSubjectAttendanceSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        subject_code = serializer.data.get('subject_code')
        month = serializer.data.get('month')
        attendances = StudentAttendance.objects.filter(subject__code=subject_code,
                                                       student=student,
                                                       classattendance__date__month=month)
        list = []
        for attendance in attendances:
            dict = {}
            dict = {
                "date": attendance.classattendance.date,
                "day": attendance.classattendance.assign.day,
                "period": attendance.classattendance.assign.period,
                "is_present": attendance.is_present
            }
            list.append(dict)
        return Response(list, status=status.HTTP_200_OK)
