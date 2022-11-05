from rest_framework.response import Response
from rest_framework import status
from rest_framework.views import APIView
from account.serializers import *
from account.models import *
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.permissions import IsAuthenticated
from account.emails import *
from .serializers import *
from adminpanel.permissions import *



class AddStudent(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated, IsAdmin]

    def get(self, request):
        token = request.META.get('HTTP_AUTHORIZATION', " ").split(' ')[1]
        tokenset = jwt.decode(token, settings.SECRET_KEY, algorithms=['HS256'])
        userID = tokenset['userID']
        user = User.objects.get(userID=userID)
        if not user.is_admin:
            return Response({'msg': 'NOT ALLOWED!'}, status=status.HTTP_400_BAD_REQUEST)
        allclasses = list(Class.objects.all())
        dic={}
        for clas in allclasses:
            dic[(clas.year, clas.department.name, clas.section)]=clas.id
        sortedclasses = list(dic.keys())
        sortedclasses.sort()
        tdic={}
        for key in sortedclasses:
            tdic[dic[key]]=key
        return Response(tdic, status=status.HTTP_200_OK)


    def post(self, request):

        serializer = AddUserSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        email = serializer.data.get('email')
        name = serializer.data.get('name')
        DOB = serializer.data.get('DOB')
        sclass = request.data.get('assignedclass')
        gender = request.data.get('sex')

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

        if sclass is not None:
            allclass = list(Class.objects.all())
            for clas in allclass:
                if sclass.lower()==clas.id.lower():
                    sclass=clas
                    break 
            else:
                return Response({'msg': 'Class does not exist'}, status=status.HTTP_400_BAD_REQUEST)

        if gender is not None:
            if gender.lower() == 'm':
                sex='Male'
            elif gender.lower() == 'f':
                sex = 'Female'
            else:
                return Response({'msg': 'Invalid gender input'}, status=status.HTTP_400_BAD_REQUEST)

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
            curstu=Student.objects.get(userID = userID)
            if sclass is not None:
                curstu.class_id=sclass 
            if gender is not None:
                curstu.sex = sex
            curstu.save()
            return Response({'msg': 'Student Created Successfully'}, status=status.HTTP_200_OK)
        except:
            return Response({'msg': 'Some error occured! Please try again'}, status=status.HTTP_400_BAD_REQUEST)


class AddTeacher(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated, IsAdmin]

    def get(self, request):
        alldepartments = list(Department.objects.all())
        dict = {}
        for dep in alldepartments:
            dict[dep.id]=dep.name
        return Response(dict, status=status.HTTP_200_OK)

    def post(self, request):

        serializer = AddUserSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        email = serializer.data.get('email')
        name = serializer.data.get('name')
        DOB = serializer.data.get('DOB')
        sdepartment = request.data.get('department')
        gender = request.data.get('sex')

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

        if sdepartment is not None:
            alldepartments = list(Department.objects.all())
            for dep in alldepartments:
                if sdepartment.lower()==dep.id.lower():
                    sdepartment=dep
                    break 
            else:
                return Response({'msg': 'Department does not exist'}, status=status.HTTP_400_BAD_REQUEST)

        if gender is not None:
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
                DOB=DOB
            ).save()
            curtea=Teacher.objects.get(userID = userID)
            if sdepartment is not None:
                curtea.class_id=sdepartment
            if gender is not None:
                curtea.sex = sex
            curtea.save()
            return Response({'msg': 'Teacher Created Successfully'}, status=status.HTTP_200_OK)
        except:
            return Response({'msg': 'Some error occured! Please try again'}, status=status.HTTP_400_BAD_REQUEST)
        
        
class Departments(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated, IsAdmin]
    
    def get(self, request, id):
        if id == 'ALL':
            departments = Department.objects.all()
            serializer = DepartmentSerializer(departments, many=True)
        else:
            departments = Department.objects.get(id=id) 
            serializer = DepartmentSerializer(departments, many=False)
        return Response(serializer.data)

    def post(self, request, id):
        serializer = DepartmentSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        if serializer.is_valid():
            serializer.save()
            return Response({'msg': 'Department added successfully'},  status=status.HTTP_200_OK)
        
    def put(self, request, id):
        department = Department.objects.get(id=id)
        serializer = DepartmentSerializer(
            instance=department, data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response({'msg': 'Department modified successfully'},  status=status.HTTP_200_OK)
    
    def delete(self, request, id):
        department = Department.objects.get(id=id)
        department.delete()
        return Response({'msg': 'Department deleted successfully'},  status=status.HTTP_200_OK)