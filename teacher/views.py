from rest_framework.response import Response
from rest_framework import status
from rest_framework.views import APIView
from account.serializers import *
from account.models import *
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.permissions import IsAuthenticated
from account.emails import *
from .permissions import *


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
    permission_classes = [IsAuthenticated, IsTeacherorIsAdmin]

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
    
    
class TimeTable(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]
    
    def get(self, request, pk):
        times = AssignTime.objects.filter(assign__class_id=pk)
        # print(times)
        classes = AssignClass.objects.filter(class_id=pk)
        list = []
        # print("hello")
        for klass in classes:
            dict={}
            dict= {"class" : klass.class_id.id, "subject" : klass.subject.name, "teacher" : klass.teacher.name}
            for time in times:
                ndict={}
                ndict=dict
                if time.assign.id == klass.id:
                    ndict|= {"period" : time.period, "day" : time.day}
                    print(ndict)
                    list.append(ndict)
            list.append(dict)
        return Response(list,  status=status.HTTP_200_OK)
