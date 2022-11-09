from rest_framework.response import Response
from rest_framework import status
from rest_framework.views import APIView
from account.serializers import *
from account.models import *
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.permissions import IsAuthenticated
from account.emails import *
from .permissions import *

def check_if_teacher_and_return_userID(request):
    token = request.META.get('HTTP_AUTHORIZATION', " ").split(' ')[1]
    tokenset = jwt.decode(token, settings.SECRET_KEY, algorithms=['HS256'])
    userID = tokenset['userID']
    try:
        teacher = Teacher.objects.get(userID=userID)
        return teacher
    except:
        return False

class TProfileDetails(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request):
        userID = check_if_teacher_and_return_userID(request).userID

        teacher = Teacher.objects.get(userID=userID)
        serializer = TeacherProfileSerializer(teacher, many=False)

        user = User.objects.get(userID=userID)
        eserializer = EmailSerializer(user, many=False)

        return Response(serializer.data | eserializer.data)

    def put(self, request):
        userID = check_if_teacher_and_return_userID(request).userID
        teacher = Teacher.objects.get(userID=userID)
        serializer = TeacherProfileSerializer(teacher, data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        # Updating the name in User Model
        name = serializer.validated_data.get('name')
        user = User.objects.get(userID=userID)
        user.name = name
        user.save()

        return Response(serializer.data, status=status.HTTP_202_ACCEPTED)


class StudentInClass(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated, IsTeacherorIsAdmin]

    def get(self, request, feedback='defaultvalue'):
        classid = request.data.get("id")
        token = request.META.get('HTTP_AUTHORIZATION', " ").split(' ')[1]
        tokenset = jwt.decode(token, settings.SECRET_KEY, algorithms=['HS256'])
        userID = tokenset['userID']
        try:
            clas = Class.objects.get(id=classid)
        except:
            return Response({'msg': 'Class does not exist'}, status=status.HTTP_400_BAD_REQUEST)
        classdetails = {'department': clas.department.name,
                        'year': clas.year, 'section': clas.section}
        students = Student.objects.all()
        teacher = Teacher.objects.get(userID=userID)
        feedbacks = {}
        dict = {}
        for student in students:
            if (student.class_id.id) == classid:
                dict[student.userID] = student.name
            if feedback=='feedback':
                try:
                    feed = StudentFeedback.objects.get(teacher = teacher, student = student)
                except:
                    continue
                feedbacks[feed.student.userID] = {feed.student.name :feed.feed}
        if feedback == 'feedback':
            response = {"feeds":feedbacks}
        else:
            response = {"classdetails": classdetails, "students": dict}
        return Response(response, status=status.HTTP_200_OK)


class TeacherOfClass(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request, feedback='defaultvalue'):
        classid = request.data.get("id")
        token = request.META.get('HTTP_AUTHORIZATION', " ").split(' ')[1]
        tokenset = jwt.decode(token, settings.SECRET_KEY, algorithms=['HS256'])
        userID = tokenset['userID']
        try:
            clas = Class.objects.get(id=classid)
        except:
            return Response({'msg': 'Class does not exist'}, status=status.HTTP_400_BAD_REQUEST)
        classdetails = {'department': clas.department.name,
                        'year': clas.year, 'section': clas.section}
        assignedclasses = AssignClass.objects.all().filter(class_id = classid)
        student = Student.objects.get(userID=userID)
        feedbacks = {}
        arr=[]
        for assignedclass in assignedclasses:
            arr+=[assignedclass.teacher.name]
            if feedback == 'feedback':
                try:
                    feed = TeacherFeedback.objects.get(student=student, teacher=assignedclass.teacher)
                except:
                    continue
                feedbacks[feed.teacher.userID] = {feed.teacher.name :feed.feed}
        if feedback == 'feedback':
            response = {"feeds":feedbacks}
        else:
            arr=set(arr)
            response = {"classdetails": classdetails, "teachers": arr}
        return Response(response, status=status.HTTP_200_OK)

class ClassOfTeacher(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated, IsTeacherorIsAdmin]

    def get(self, request):
        teacherid = request.data.get("id")
        try:
            teacher = Teacher.objects.get(userID=teacherid)
        except:
            return Response({'msg': 'Teacher does not exist'}, status=status.HTTP_400_BAD_REQUEST)
        assignedclasses = AssignClass.objects.all().filter(teacher = teacher)
        arr=[]
        for assignedclass in assignedclasses:
            arr+=[assignedclass.class_id.id]
        arr=set(arr)
        response = {"classes":arr}
        return Response(response, status=status.HTTP_200_OK)

class SubjectsInDepartments(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated, IsTeacherorIsAdmin]

    def get(self, request):
        pk = request.data.get("id")
        try:
            dept = Department.objects.get(id=pk)
        except:
            return Response({'msg': 'Department does not exist'}, status=status.HTTP_400_BAD_REQUEST)
        subjects = Subject.objects.filter(department__id=pk)
        serializer = SubjectSectionSerializer(subjects, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
class TeachersInDepartments(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated, IsTeacherorIsAdmin]

    def get(self, request):
        pk = request.data.get("id")
        try:
            dept = Department.objects.get(id=pk)
        except:
            return Response({'msg': 'Department does not exist'}, status=status.HTTP_400_BAD_REQUEST)
        teachers =Teacher.objects.filter(department__id=pk)
        serializer =TeacherSectionSerializer(teachers, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

class StudentFeedbackView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]


    def put(self, request):
        teacher = check_if_teacher_and_return_userID(request)
        if not teacher:
            return Response({'msg': 'NOT ALLOWED'},  status=status.HTTP_400_BAD_REQUEST)
        serializer = FeedbackSerizer(data = request.data)
        serializer.is_valid(raise_exception=True)
        userID = serializer.data.get('userID')
        feed = request.data.get('feed')
        try:
            student = Student.objects.get(userID=userID)
        except:
            return Response({'msg': 'student does not exist'},  status=status.HTTP_400_BAD_REQUEST)
        try:
            feedback = StudentFeedback.objects.get(teacher=teacher, student = student)
            feedback.feed=feed
            feedback.save()
            return Response({'msg': 'Feedback Modified Successfully !!'}, status=status.HTTP_200_OK)
        except:
            StudentFeedback(
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
        pk = check_if_teacher_and_return_userID(request)
        if(pk is False):
            return Response({'msg': 'Invalid credentials'},  status=status.HTTP_200_OK)
        
        classes = AssignClass.objects.filter(teacher__userID = pk.userID)
        list = []
        for i in TIME_SLOTS:
            for j in DAYS:
                time=AssignTime.objects.filter(period=i, day=j,assign__teacher__userID = pk.userID )
                
                if time.exists():
                    time=time[0]
                    
                    dict={}
                    dict= {"class" : time.assign.class_id.id, "subject" : time.assign.subject.name, "teacher" : time.assign.teacher.name, "period" : i, "day" : j}
                else:
                    dict={}
                    dict= {"class" : "", "subject" : "", "teacher" : pk.name, "period" : i, "day" : j}
                list.append(dict)            
        return Response(list,  status=status.HTTP_200_OK)
