from rest_framework.response import Response
from rest_framework import status
from rest_framework.views import APIView
from account.serializers import *
from account.models import *
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.permissions import IsAuthenticated
from account.emails import *
from adminpanel.permissions import *
from .permissions import *

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