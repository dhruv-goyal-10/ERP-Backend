from rest_framework.response import Response
from rest_framework import status
from rest_framework.views import APIView
from account.serializers import *
from account.models import *
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.permissions import IsAuthenticated
from account.emails import *
from account.custom_permissions import *
from django.shortcuts import get_object_or_404
from datetime import date
from django.db.utils import IntegrityError
from .custompaginations import PaginationHandlerMixin
from rest_framework.pagination import PageNumberPagination
from rest_framework.generics import *


# This function fetches the user from its Access Token

def return_user(request):
    token = request.META.get('HTTP_AUTHORIZATION', " ").split(' ')[1]
    tokenset = jwt.decode(token, settings.SECRET_KEY, algorithms=['HS256'])
    userID = tokenset['userID']
    user = User.objects.filter(userID=userID)
    if user.exists():
        return user[0]


# 1- API for viewing the own profile (Teacher profile)

class TProfileDetails(RetrieveUpdateAPIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]
    serializer_class = TeacherProfileSerializer

    def get_object(self):
        return get_object_or_404(Teacher, user=return_user(self.request))


# 2- API for getting the list of students in a particular class

class StudentInClass(ListAPIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated, IsTeacherorIsAdmin]
    serializer_class = StudentList

    def get_queryset(self):
        return Student.objects.filter(class_id__id = self.kwargs['classid'])


class StudentInClassFeedback(ListAPIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated, IsTeacherorIsAdmin]
    serializer_class = StudentFeedbackSerializer

    def get_queryset(self):
        teacher = get_object_or_404(Teacher, user=return_user(self.request))
        return StudentFeedback.objects.filter(teacher=teacher, student__class_id__id = self.kwargs['classid'])


# 3- API for getting the list of teachers assigned to a  particular class

class TeacherOfClass(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request, classid, feedback='defaultvalue'):
        user = return_user(request)
        clas = get_object_or_404(Class, id=classid)
        classdetails = {'department': clas.department.name,
                        'year': clas.year, 'section': clas.section}
        assignedclasses = AssignClass.objects.all().filter(class_id=classid)
        if feedback == 'feedback':
            student = get_object_or_404(Student, user=user)
            print('student')
        feedbacks = {}
        arr = []
        for assignedclass in assignedclasses:
            arr += [assignedclass.teacher.name]
            if feedback == 'feedback':
                feed = TeacherFeedback.objects.filter(
                    student=student, teacher=assignedclass.teacher)
                if feed.exists():
                    feed = feed[0]
                    feedbacks[feed.teacher.userID] = {
                        feed.teacher.name: feed.feed}
        if feedback == 'feedback':
            response = {"feeds": feedbacks}
        else:
            arr = set(arr)
            response = {"classdetails": classdetails, "teachers": arr}
        return Response(response, status=status.HTTP_200_OK)


# 4- API for getting the list of classes assigned to a particular teacher

class ClassOfTeacher(ListAPIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated, IsTeacherorIsAdmin]
    serializer_class = AssignClassSerializer

    def get_queryset(self):
        teacher = get_object_or_404(Teacher, userID=self.kwargs['pk'])
        return AssignClass.objects.filter(teacher=teacher)


# 5- API for getting the list of subjects in a particular department

class SubjectsInDepartments(ListAPIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated, IsAdmin]
    serializer_class = SubjectSerializer

    def get_queryset(self):
        return Subject.objects.filter(department__id=self.kwargs['departmentid'])


# 6- API for getting the list of teachers in a particular department

class TeachersInDepartments(ListAPIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated, IsTeacherorIsAdmin]
    serializer_class = TeacherList

    def get_queryset(self):
        return Teacher.objects.filter(department__id=self.kwargs['departmentid'])


# 7- API for giving feedback to a particular student

class StudentFeedbackView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def put(self, request):
        user = return_user(request)
        teacher = get_object_or_404(Teacher, user=user)
        feedbacks = request.data
        for feedback in feedbacks:
            student = get_object_or_404(Student, userID=feedback["userID"])
            thisfeedback = StudentFeedback.objects.filter(
                teacher=teacher, student=student)
            if thisfeedback.exists():
                thisfeedback = thisfeedback[0]
                thisfeedback.feed = feedback["feed"]
                thisfeedback.save()
            else:
                StudentFeedback(teacher=teacher, student=student,
                                feed=feedback["feed"]).save()
        return Response({'msg': 'Feedback Submitted Successfully !!'}, status=status.HTTP_200_OK)


TIME_SLOTS = ['8:30 - 9:20', '9:20 - 10:10',
              '11:00 - 11:50', '11:50 - 12:40', '1:30 - 2:20']
DAYS = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday']


# 8- API for viewing TimeTable (Teacher side)

class TimeTable(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated, IsTeacherorIsAdmin]

    def get(self, request):
        user = return_user(request)
        list = []
        for i in TIME_SLOTS:
            for j in DAYS:
                time = AssignTime.objects.filter(
                    period=i, day=j, assign__teacher__userID=user.userID)
                if time.exists():
                    time = time[0]
                    dict = {"class": time.assign.class_id.id, "subject": time.assign.subject.name,
                            "teacher": time.assign.teacher.name, "period": i, "day": j}
                else:
                    dict = {"class": "",
                            "subject": "",
                            "teacher": user.name,
                            "period": i,
                            "day": j}
                list.append(dict)
        return Response(list,  status=status.HTTP_200_OK)


# 9- API for getting the list of all the schedules of assigned classes with their attendance status

class ClassAttendanceObjects(ListAPIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated, IsTeacherorIsAdmin]
    serializer_class = AttendanceObjectsSerializer

    def get_queryset(self):
        return ClassAttendance.objects.order_by('-date').filter(
            assign__assign__teacher__userID=return_user(self.request).userID)

# 10- API for taking the attendance of the students of particular ClassAttendance Object

class TakeStudentsAttendance(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated, IsTeacherorIsAdmin]

    def get(self, request, date, class_id, period):
        classattendance = get_object_or_404(
            ClassAttendance, assign__period=period, date=date, assign__class_id=class_id)
        students = StudentAttendance.objects.filter(
            classattendance=classattendance)
        list = [{"marked": classattendance.status}]
        for student in students:
            dict = {"name": student.student.name,
                    "userID": student.student.userID,
                    "is_present": student.is_present}
            list.append(dict)
        return Response(list, status=status.HTTP_200_OK)

    def put(self, request, date, class_id, period):
        data = request.data
        for i in range(len(data)):
            classatt = ClassAttendance.objects.get(date=date,
                                                   assign__class_id=class_id,
                                                   assign__period=period)
            student = StudentAttendance.objects.get(student__userID=data[i]['userID'],
                                                    classattendance=classatt)

            student.is_present = data[i]['is_present']
            student.save()

            classatt.status = True
            classatt.save()
        return Response({"msg": "Class Attendance Updated Successfully"}, status=status.HTTP_200_OK)


# 11- API for creating only today's ClassAttendance Objects for all the classes assigned to the teacher

class CreateTodayAttendance(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated, IsTeacherorIsAdmin]

    def post(self, request):
        user = return_user(request)
        teacher = get_object_or_404(Teacher, user=user)
        curdate = date.today()
        curdate = curdate + timedelta(days=1)
        days = {1: 'Monday', 2: 'Tuesday', 3: 'Wednesday',
                4: 'Thursday', 5: 'Friday', 6: 'Saturday', 0: 'Sunday'}
        curday = days[int(curdate.strftime('%w'))]
        assignedclasses = AssignClass.objects.filter(teacher=teacher)
        for assignedclass in assignedclasses:
            curclass = assignedclass.class_id
            assignedtimes = AssignTime.objects.filter(
                day=curday, class_id=curclass, teacher=teacher)
            for assignedtime in assignedtimes:
                try:
                    ca = ClassAttendance.objects.create(
                        date=curdate, assign=assignedtime)
                    students = Student.objects.filter(class_id=curclass)
                    for student in students:
                        StudentAttendance.objects.create(
                            student=student, classattendance=ca, subject=assignedtime.assign.subject)
                except IntegrityError:
                    continue

        return Response({'msg': 'Attendance Objects added successfully'},  status=status.HTTP_200_OK)


# ClassAttendanceObjects API (with Pagination)

# class Basic_pagination(PageNumberPagination):
#     page_size= 5
#     # page_size_query_param = 'limit'

# class ClassAttendanceObjects(APIView, PaginationHandlerMixin):
#     authentication_classes = [JWTAuthentication]
#     permission_classes = [IsAuthenticated, IsTeacherorIsAdmin]
#     pagination_class = Basic_pagination

#     def get(self, request):
#         userID = return_user(request).userID
#         allobjects= ClassAttendance.objects.order_by('-date').filter(assign__assign__teacher__userID= userID
#         )

#         list = []
#         for object in allobjects:
#             dict = {"date": object.date,
#                     "time": object.assign.period,
#                     "class_id": object.assign.class_id.id,
#                     "subject_name": object.assign.assign.subject.name,
#                     "subject_code": object.assign.assign.subject.code,
#                     "teacher_userID": object.assign.assign.teacher.userID,
#                     "status": object.status
#                     }
#             list.append(dict)
#         page = self.paginate_queryset(list)
#         return self.get_paginated_response(page)
