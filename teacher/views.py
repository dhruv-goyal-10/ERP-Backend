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


class StudentInClass(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated, (IsAdmin or IsTeacher)]

    def post(self, request):
        serializer = ClassIdSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        classid = serializer.data.get('id')
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
