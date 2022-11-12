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


def return_user(request):
    token = request.META.get('HTTP_AUTHORIZATION', " ").split(' ')[1]
    tokenset = jwt.decode(token, settings.SECRET_KEY, algorithms=['HS256'])
    userID = tokenset['userID']
    user = User.objects.filter(userID=userID)
    if user.exists():
        return user[0]


class TProfileDetails(APIView):

    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = return_user(request)
        teacher = get_object_or_404(Teacher, user=user)
        serializer = TeacherProfileSerializer(teacher, many=False)
        eserializer = EmailSerializer(user, many=False)
        return Response(serializer.data | eserializer.data)

    def put(self, request):
        user = return_user(request)
        teacher = get_object_or_404(Teacher, user=user)
        serializer = TeacherProfileSerializer(teacher, data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        # Updating the name in User Model
        name = serializer.validated_data.get('name')
        user.name = name
        user.save()
        return Response(serializer.data, status=status.HTTP_202_ACCEPTED)


class StudentInClass(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated, IsTeacherorIsAdmin]

    def get(self, request, classid, feedback='defaultvalue'):
        user = return_user(request)
        clas = get_object_or_404(Class, id=classid)
        classdetails = {'department': clas.department.name,
                        'year': clas.year, 'section': clas.section}
        students = Student.objects.all()
        if feedback == 'feedback':
            teacher = get_object_or_404(Teacher, user=user)
        feedbacks = {}
        dict = {}
        for student in students:
            if (student.class_id.id) == classid:
                dict[student.userID] = student.name
            if feedback == 'feedback':
                feed = StudentFeedback.objects.filter(
                    teacher=teacher, student=student)
                if feed.exists():
                    feed = feed[0]
                    feedbacks[feed.student.userID] = {
                        feed.student.name: feed.feed}
        if feedback == 'feedback':
            response = {"feeds": feedbacks}
        else:
            response = {"classdetails": classdetails, "students": dict}
        return Response(response, status=status.HTTP_200_OK)


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


class ClassOfTeacher(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated, IsTeacherorIsAdmin]

    def get(self, request, teacherid):
        teacher = get_object_or_404(Teacher, userID=teacherid)
        assignedclasses = AssignClass.objects.all().filter(teacher=teacher)
        arr = []
        for assignedclass in assignedclasses:
            arr += [assignedclass.class_id.id]
        arr = set(arr)
        response = {"classes": arr}
        return Response(response, status=status.HTTP_200_OK)


class SubjectsInDepartments(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated, IsAdmin]

    def get(self, request, departmentid):
        dept = get_object_or_404(Department, id=departmentid)
        subjects = Subject.objects.filter(department__id=departmentid)
        serializer = SubjectSectionSerializer(subjects, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class TeachersInDepartments(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated, IsTeacherorIsAdmin]

    def get(self, request, departmentid):
        dept = get_object_or_404(Department, id=departmentid)
        teachers = Teacher.objects.filter(department__id=departmentid)
        departmentdet = dict()
        departmentdet["department details"] = {dept.id : dept.name}
        response = {}
        if teachers.exists():
            for teacher in teachers:
                response[teacher.userID]=teacher.name
        response = {'teachers' : response}
        return Response(departmentdet | response, status=status.HTTP_200_OK)


class StudentFeedbackView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def put(self, request):
        user = return_user(request)
        teacher = get_object_or_404(Teacher, user=user)
        serializer = FeedbackSerizer(data=request.data)
        serializer.is_valid(raise_exception=True)
        userID = serializer.data.get('userID')
        feed = serializer.data.get('feed')
        student = get_object_or_404(Student, userID=userID)
        feedback = StudentFeedback.objects.filter(
            teacher=teacher, student=student)
        if feedback.exists():
            feedback = feedback[0]
            feedback.feed = feed
            feedback.save()
            return Response({'msg': 'Feedback Modified Successfully !!'}, status=status.HTTP_200_OK)
        StudentFeedback(teacher=teacher, student=student, feed=feed).save()
        return Response({'msg': 'Feedback Submitted Successfully !!'}, status=status.HTTP_200_OK)


TIME_SLOTS = ['8:30 - 9:20','9:20 - 10:10', '11:00 - 11:50', '11:50 - 12:40', '1:30 - 2:20']
DAYS = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday']


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


class ClassAttendanceObjects(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated, IsTeacherorIsAdmin]

    def get(self, request):
        userID = return_user(request).userID
        objects= ClassAttendance.objects.filter(assign__assign__teacher__userID= userID
        )
        
        # print(objects)
        list = []
        for object in objects:
            # print(object.date)
            dict = {"date": object.date,
                    "time": object.assign.period,
                    "class_id": object.assign.class_id.id,
                    "subject_name": object.assign.assign.subject.name,
                    "subject_code": object.assign.assign.subject.code,
                    "teacher_userID": object.assign.assign.teacher.userID
                    }
            list.append(dict)
        return Response(list, status=status.HTTP_200_OK)


class StudentsinClassAttendance(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated, IsTeacherorIsAdmin]

    def get(self, request, date, class_id, period):
        classattendance = get_object_or_404(
            ClassAttendance, assign__period=period, date=date, assign__class_id=class_id)
        students = StudentAttendance.objects.filter(
            classattendance=classattendance)
        list = [{"marked" : classattendance.status}]
        for student in students:
            dict = {"name": student.student.name,
                    "userID": student.student.userID,
                    "is_present": student.is_present}
            list.append(dict)
        return Response(list, status=status.HTTP_200_OK)

    def put(self, request, date, class_id, period):
        data = request.data
        for i in range(len(data)):
            if i == 0:
                date = data[i]['date']
                period = data[i]['period']
                class_id = data[i]['class_id']
            else:
                student = StudentAttendance.objects.get(student__userID=data[i]['userID'],
                                                        classattendance__assign__class_id=class_id,
                                                        classattendance__date=date)
                student.is_present = data[i]['is_present']
                student.save()
                classatt = ClassAttendance.objects.get(date=date,
                                                       assign__class_id=class_id,
                                                       assign__period=period)
                classatt.status = True
                classatt.save()
        return Response({"msg": "Class Attendance Updated Successfully"}, status=status.HTTP_200_OK)
