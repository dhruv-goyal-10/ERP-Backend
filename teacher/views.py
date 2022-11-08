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

    def get(self, request, classid):
        try:
            clas = Class.objects.get(id=classid)
        except:
            return Response({'msg': 'Class does not exist'}, status=status.HTTP_400_BAD_REQUEST)
        classdetails = {'department': clas.department.name,
                        'year': clas.year, 'section': clas.section}
        students = Student.objects.all()
        dict = {}
        for student in students:
            if (student.class_id.id) == classid:
                dict[student.userID] = student.name
        response = {"classdetails": classdetails, "students": dict}
        return Response(response, status=status.HTTP_200_OK)


class TeacherOfClass(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request, classid):
        try:
            clas = Class.objects.get(id=classid)
        except:
            return Response({'msg': 'Class does not exist'}, status=status.HTTP_400_BAD_REQUEST)
        classdetails = {'department': clas.department.name,
                        'year': clas.year, 'section': clas.section}
        assignedclasses = AssignClass.objects.all().filter(class_id = classid)
        arr=[]
        for assignedclass in assignedclasses:
            arr+=[assignedclass.teacher.name]
        arr=set(arr)
        response = {"classdetails": classdetails, "teachers": arr}
        return Response(response, status=status.HTTP_200_OK)

class ClassOfTeacher(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated, IsTeacherorIsAdmin]

    def get(self, request, teacherid):
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

    def get(self, request,pk):
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

    def get(self, request,pk):
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


    def put(self, request, student):
        teacher = check_if_teacher_and_return_userID(request)
        if not teacher:
            return Response({'msg': 'NOT ALLOWED'},  status=status.HTTP_400_BAD_REQUEST)
        try:
            student = Student.objects.get(userID=student)
        except:
            return Response({'msg': 'student does not exist'},  status=status.HTTP_400_BAD_REQUEST)
        feed = request.data.get('feed')
        if feed is None:
            feed = 3
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
    
    
class TimeTable(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        pk = check_if_teacher_and_return_userID(request)
        if(pk is False):
            return Response({'msg': 'Invalid credentials'},  status=status.HTTP_200_OK)
        pk=pk.userID
        classes = AssignClass.objects.filter(teacher__userID = pk)
        list = []
        for klass in classes:
            dict={}
            dict= {"class" : klass.class_id.id, "subject" : klass.subject.name, "teacher" : klass.teacher.name}
            times = AssignTime.objects.filter(assign__id=klass.id)
            for time in times:
                ndict=dict.copy()
                if time.assign.id == klass.id:
                    ndict|= {"period" : time.period, "day" : time.day}
                    list.append(ndict)
        return Response(list,  status=status.HTTP_200_OK)
