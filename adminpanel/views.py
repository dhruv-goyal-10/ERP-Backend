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
        allclasses = list(Class.objects.all())
        dic = {}
        for clas in allclasses:
            dic[(clas.year, clas.department.name, clas.section)] = clas.id
        sortedclasses = list(dic.keys())
        sortedclasses.sort()
        tdic = {}
        for key in sortedclasses:
            tdic[dic[key]] = key
        return Response(tdic, status=status.HTTP_200_OK)

    def post(self, request):

        serializer = AddStudentSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        email = serializer.data.get('email')
        name = serializer.data.get('name')
        DOB = serializer.data.get('DOB')
        classid = serializer.data.get('class_id')
        gender = request.data.get('sex')

        students = list(Student.objects.all())
        if len(students) != 0:
            userID = int(students[-1].userID)+1
        else:
            userID = 200000

        classid = Class.objects.get(id=classid)

        # Default Password --> first_name in lowercase + @ + DOB(YYYYMMDD)
        password = name.split(" ")[0].lower() + '@' + DOB.replace("-", "")
        password = password[0].upper()+password[1:]

        try:
            user = User.objects.get(email=email)
            return Response({'msg': 'User with this email already exists'}, status=status.HTTP_400_BAD_REQUEST)
        except:
            pass

        if gender is not None:
            if gender.lower() == 'm':
                sex = 'Male'
            elif gender.lower() == 'f':
                sex = 'Female'
            else:
                return Response({'msg': 'Invalid gender input'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            EMAIL.send_credentials_via_email(
                userID, password, name, email, 'student')
        except:
            return Response({'msg': 'Some error occured! Please try again'}, status=status.HTTP_400_BAD_REQUEST)
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
            class_id=classid,
        ).save()
        curstu = Student.objects.get(userID=userID)
        if gender is not None:
            curstu.sex = sex
        curstu.save()
        return Response({'msg': 'Student Created Successfully'}, status=status.HTTP_200_OK)


class AddTeacher(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated, IsAdmin]

    def get(self, request):
        alldepartments = list(Department.objects.all())
        dict = {}
        for dep in alldepartments:
            dict[dep.id] = dep.name
        return Response(dict, status=status.HTTP_200_OK)

    def post(self, request):

        serializer = AddTeacherSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        email = serializer.data.get('email')
        name = serializer.data.get('name')
        DOB = serializer.data.get('DOB')
        department = serializer.data.get('department')
        gender = request.data.get('sex')

        teachers = Teacher.objects.all()
        try:
            userID = int(list(teachers)[-1].userID)+1
        except:
            userID = 100000

        department = Department.objects.get(id=department)

        # Default Password --> first_name in lowercase + @ + DOB(YYYYMMDD)
        password = name.split(" ")[0].lower() + '@' + DOB.replace("-", "")
        password = password[0].upper()+password[1:]

        try:
            user = User.objects.get(email=email)
            return Response({'msg': 'User with this email already exists'}, status=status.HTTP_400_BAD_REQUEST)
        except:
            pass

        if gender is not None:
            if gender.lower() == 'm':
                sex = 'Male'
            elif gender.lower() == 'f':
                sex = 'Female'
            else:
                return Response({'msg': 'Invalid gender input'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            EMAIL.send_credentials_via_email(
                userID, password, name, email, 'teacher')
        except:
            return Response({'msg': 'Some error occured! Please try again'}, status=status.HTTP_400_BAD_REQUEST)
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
            department=department
        ).save()
        curtea = Teacher.objects.get(userID=userID)
        if gender is not None:
            curtea.sex = sex
        curtea.save()
        return Response({'msg': 'Teacher Created Successfully'}, status=status.HTTP_200_OK)


class Departments(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated, IsAdmin]

    def get(self, request, pk):
        if pk == 'ALL':
            departments = Department.objects.all()
            serializer = DepartmentSerializer(departments, many=True)
        else:
            departments = Department.objects.get(id=pk)
            serializer = DepartmentSerializer(departments, many=False)
        return Response(serializer.data)

    def post(self, request, pk):
        serializer = DepartmentSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        if serializer.is_valid():
            serializer.save()
            return Response({'msg': 'Department added successfully'},  status=status.HTTP_200_OK)

    def put(self, request, pk):
        try:
            department = Department.objects.get(id=pk)
        except:
            return Response({'msg': 'Department does not exist'}, status=status.HTTP_400_BAD_REQUEST)
        serializer = DepartmentSerializer(
            instance=department, data=request.data)
        serializer.is_valid(raise_exception=True)
        id = serializer.validated_data.get('id')
        if (id != pk):
            return Response({'msg': 'Invalid Update Request'}, status=status.HTTP_400_BAD_REQUEST)
        serializer.save()
        return Response({'msg': 'Department modified successfully'},  status=status.HTTP_200_OK)

    def delete(self, request, pk):
        try:
            department = Department.objects.get(id=pk)
        except:
            return Response({'msg': 'Department does not exist'}, status=status.HTTP_400_BAD_REQUEST)
        department.delete()
        return Response({'msg': 'Department deleted successfully'},  status=status.HTTP_200_OK)


class ClassObject(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated, IsAdmin]

    def get(self, request, pk):
        if pk == 'ALL':
            allclasses = list(Class.objects.all())
            dic = {}
            for clas in allclasses:
                dic[(clas.year, clas.department.name, clas.section)] = clas.id
            sortedclasses = list(dic.keys())
            sortedclasses.sort()
            tdic = {}
            for key in sortedclasses:
                tdic[dic[key]] = key
            return Response(tdic, status=status.HTTP_200_OK)
        else:
            classes = Class.objects.get(id=pk)
            serializer = ClassSerializer(classes, many=False)
            return Response(serializer.data)

    def post(self, request, pk):
        serializer = ClassSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response({'msg': 'Class added successfully'},  status=status.HTTP_200_OK)

    def put(self, request, pk):
        try:
            clas = Class.objects.get(id=pk)
        except:
            return Response({'msg': 'Class does not exist'}, status=status.HTTP_400_BAD_REQUEST)
        serializer = ClassSerializer(instance=clas, data=request.data)
        serializer.is_valid(raise_exception=True)
        id = serializer.validated_data.get('id')
        if (id != pk):
            return Response({'msg': 'Invalid Update Request'}, status=status.HTTP_400_BAD_REQUEST)
        serializer.save()
        return Response({'msg': 'Class modified successfully'},  status=status.HTTP_200_OK)

    def delete(self, request, pk):
        try:
            clas = Class.objects.get(id=pk)
        except:
            return Response({'msg': 'Class does not exist'}, status=status.HTTP_400_BAD_REQUEST)
        clas.delete()
        return Response({'msg': 'Class deleted successfully'},  status=status.HTTP_200_OK)


class ClassByDepartment(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated, IsAdmin]

    def get(self, request, departmentid):
        try:
            dep = Department.objects.get(id=departmentid)
        except:
            return Response({'msg': 'Department does not exist'}, status=status.HTTP_400_BAD_REQUEST)
        allclasses = Class.objects.all().filter(department=dep)
        dict = {}
        for clas in allclasses:
            dict[clas.id] = {"year": clas.year, "section": clas.section}
        return Response(dict,  status=status.HTTP_200_OK)


class Subjects(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated, IsAdmin]

    def get(self, request, pk):
        if pk == 'ALL':
            subject = Subject.objects.all()
            serializer = SubjectSerializer(subject, many=True)
        else:
            subject = Subject.objects.get(code=pk)
            serializer = SubjectSerializer(subject, many=False)
        return Response(serializer.data)

    def post(self, request, pk):
        serializer = SubjectSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response({'msg': 'Subject added successfully'},  status=status.HTTP_200_OK)

    def put(self, request, pk):
        try:
            subject = Subject.objects.get(code=pk)
        except:
            return Response({'msg': 'Subject does not exist'}, status=status.HTTP_400_BAD_REQUEST)
        serializer = SubjectSerializer(instance=subject, data=request.data)
        serializer.is_valid(raise_exception=True)
        code = serializer.validated_data.get('code')
        if (code != pk):
            return Response({'msg': 'Invalid Update Request'}, status=status.HTTP_400_BAD_REQUEST)
        serializer.save()
        return Response({'msg': 'Subject modified successfully'},  status=status.HTTP_200_OK)

    def delete(self, request, pk):
        try:
            subject = Subject.objects.get(code=pk)
        except:
            return Response({'msg': 'Subject does not exist'}, status=status.HTTP_400_BAD_REQUEST)
        subject.delete()
        return Response({'msg': 'Subject deleted successfully'},  status=status.HTTP_200_OK)


class FeedbackView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated, IsAdmin]

    def get(self, request, key):
        resdict = {}
        if key.lower() == 'teachers':
            feedbacks = list(TeacherFeedback.objects.all())
            for feedback in feedbacks:
                try:
                    resdict[feedback.teacher.name] += [
                        {feedback.student.name: feedback.feed}]
                except:
                    resdict[feedback.teacher.name] = [
                        {feedback.student.name: feedback.feed}]
        elif key.lower() == 'students':
            feedbacks = list(StudentFeedback.objects.all())
            for feedback in feedbacks:
                try:
                    resdict[feedback.student.name] += [
                        {feedback.teacher.name: feedback.feed}]
                except:
                    resdict[feedback.student.name] = [
                        {feedback.teacher.name: feedback.feed}]
        else:
            try:
                fuser = User.objects.get(userID=key)
            except:
                return Response({'msg': 'INVALID INPUT'},  status=status.HTTP_400_BAD_REQUEST)
            stu = False
            tea = False
            try:
                student = Student.objects.get(userID=key)
                stu = True
            except:
                teacher = Teacher.objects.get(userID=key)
                tea = True
            c = 0
            tf = 0
            if stu:
                feedbacks = list(
                    StudentFeedback.objects.filter(student=student))
            elif tea:
                feedbacks = list(
                    TeacherFeedback.objects.filter(teacher=teacher))
            else:
                return Response({'msg': 'INVALID INPUT'},  status=status.HTTP_400_BAD_REQUEST)
            for feedback in feedbacks:
                if stu:
                    resdict[feedback.teacher.name] = feedback.feed
                else:
                    resdict[feedback.student.name] = feedback.feed
                tf += feedback.feed
                c += 1
            avgfeed = tf/c
            resdict["averagefeed"] = avgfeed
        return Response(resdict,  status=status.HTTP_200_OK)
