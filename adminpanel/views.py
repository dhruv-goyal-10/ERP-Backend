from rest_framework.response import Response
from rest_framework import status
from rest_framework.views import APIView
from account.serializers import *
from account.models import *
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.permissions import IsAuthenticated
import jwt
from account.emails import *


class AddStudent(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def post(self, request):
        token = request.META.get('HTTP_AUTHORIZATION', " ").split(' ')[1]
        tokenset = jwt.decode(token, settings.SECRET_KEY, algorithms=['HS256'])
        userID = tokenset['userID']
        user = User.objects.get(userID=userID)
        if not user.is_admin:
            return Response({'msg': 'NOT ALLOWED!'}, status=status.HTTP_400_BAD_REQUEST)

        serializer = AddStudentSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        email = serializer.data.get('email')
        name = serializer.data.get('name')
        DOB = serializer.data.get('DOB')

        students = Student.objects.all()
        try:
            userID = int(list(students)[-1].userID)+1
        except:
            userID = 200000

        # Default Password --> first_name in lowercase + @ + DOB(YYYYMMDD)
        password = name.split(" ")[0].lower() + '@' + DOB.replace("-", "")
        password = password[0].upper()+password[1:]

        try:
            user = User.objects.get(email=email)
            return Response({'msg': 'User with this email already exists'}, status=status.HTTP_400_BAD_REQUEST)
        except:
            pass

        try:
            EMAIL.send_credentials_via_email(
                userID, password, name, email, 'student')
            user = User.objects.create_user(
                email=email,
                userID=userID,
                name=name,
            )
            user.set_password(password)
            user.is_stu = True
            user.save()

            Student(
                user=user,
                userID=userID,
                name=name,
                DOB=DOB,
            ).save()
            return Response({'msg': 'Student Created Successfully'}, status=status.HTTP_200_OK)
        except:
            return Response({'msg': 'Some error occured! Please try again'}, status=status.HTTP_400_BAD_REQUEST)


class AddTeacher(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def post(self, request):
        token = request.META.get('HTTP_AUTHORIZATION', " ").split(' ')[1]
        tokenset = jwt.decode(token, settings.SECRET_KEY, algorithms=['HS256'])
        userID = tokenset['userID']
        user = User.objects.get(userID=userID)
        if not user.is_admin:
            return Response({'msg': 'NOT ALLOWED!'}, status=status.HTTP_400_BAD_REQUEST)

        serializer = AddTeacherSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        email = serializer.data.get('email')
        name = serializer.data.get('name')
        DOB = serializer.data.get('DOB')
        sdepartment = serializer.data.get('department')
        gender = serializer.data.get('sex')

        teachers = Teacher.objects.all()
        try:
            userID = int(list(teachers)[-1].userID)+1
        except:
            userID = 100000

        # Default Password --> first_name in lowercase + @ + DOB(YYYYMMDD)
        password = name.split(" ")[0].lower() + '@' + DOB.replace("-", "")
        password = password[0].upper()+password[1:]

        try:
            user = User.objects.get(email=email)
            return Response({'msg': 'User with this email already exists'}, status=status.HTTP_400_BAD_REQUEST)
        except:
            pass

        alldepartments = list(Department.objects.all())
        for dep in alldepartments:
            if sdepartment.lower()==dep.id.lower():
                sdepartment=dep
                break 
        else:
            return Response({'msg': 'Department does not exist'}, status=status.HTTP_400_BAD_REQUEST)
        print(gender)
        if gender.lower() == 'm':
            sex='Male'
        elif gender.lower() == 'f':
            sex = 'Female'
        else:
            return Response({'msg': 'Invalid gender input'}, status=status.HTTP_400_BAD_REQUEST)


        try:
            EMAIL.send_credentials_via_email(
                userID, password, name, email, 'teacher')
            user = User.objects.create_user(
                email=email,
                userID=userID,
                name=name,
            )
            user.set_password(password)
            user.is_tea = True
            user.save()

            Teacher(
                user=user,
                userID=userID,
                name=name,
                DOB=DOB,
                department=sdepartment,
                sex=sex
            ).save()
            return Response({'msg': 'Teacher Created Successfully'}, status=status.HTTP_200_OK)
        except:
            return Response({'msg': 'Some error occured! Please try again'}, status=status.HTTP_400_BAD_REQUEST)
