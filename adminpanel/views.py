from rest_framework.response import Response
from rest_framework import status
from rest_framework.views import APIView
from account.serializers import *
from account.models import *
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.permissions import IsAuthenticated
from account.emails import *
from .serializers import *
from account.custom_permissions import *
from datetime import date
from django.shortcuts import get_object_or_404
from django.db.utils import IntegrityError
# from account.views import checkemail
from django.contrib.postgres.search import TrigramWordSimilarity
import os
import pandas

def checkemail(email):
    reg = "^[A-Za-z0-9._%+-]+@gmail\.com$"
    pat = re.compile(reg)
    mat = re.search(pat, email)
    if not mat:
        return True


# 1- API for adding a Student

class AddStudent(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated, IsAdmin]

    def post(self, request):
        serializer = AddStudentSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        email = serializer.data.get('email')
        name = serializer.data.get('name')
        DOB = serializer.data.get('DOB')
        classid = serializer.data.get('class_id')
        print(DOB)
        response = addstudent(email, name, DOB, classid)
        if response == 'DNA':
            return Response({'msg': 'Domain not allowed'}, status=status.HTTP_400_BAD_REQUEST)
        elif response == 'EAE':
            return Response({'msg': 'User with this email already exists'}, status=status.HTTP_400_BAD_REQUEST)
        elif response == 'SEO':
            return Response({'msg': 'Some error occured! Please try again'}, status=status.HTTP_400_BAD_REQUEST)
        elif response == 'SCS':
            return Response({'msg': 'Student Created Successfully'}, status=status.HTTP_200_OK)


def addstudent(email, name, DOB, classid):
    # print(email)
    if checkemail(email):
        # Response({'msg': 'Domain not allowed'}, status=status.HTTP_400_BAD_REQUEST)
        return 'DNA'

    students = list(Student.objects.all().order_by('-userID'))
    if len(students) != 0:
        userID = int(students[0].userID)+1
    else:
        userID = 200000
    classid = get_object_or_404(Class, id=classid)
    # Default Password --> first_name in lowercase + @ + DOB(YYYYMMDD)
    password = name.split(" ")[0].lower() + '@' + DOB.replace("-", "")
    password = password[0].upper()+password[1:]
    email = email.lower()
    user = User.objects.filter(email=email)
    if user.exists():
        # Response({'msg': 'User with this email already exists'}, status=status.HTTP_400_BAD_REQUEST)
        return 'EAE'

    try:
        EMAIL.send_credentials_via_email(
            userID, password, name, email, 'student')
    except:
        # Response({'msg': 'Some error occured! Please try again'}, status=status.HTTP_400_BAD_REQUEST)
        return 'SEO'

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
    # Response({'msg': 'Student Created Successfully'}, status=status.HTTP_200_OK)
    return 'SCS'

# 2- API for adding a Teacher


class AddTeacher(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated, IsAdmin]

    def post(self, request):
        serializer = AddTeacherSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        email = serializer.data.get('email')
        name = serializer.data.get('name')
        DOB = serializer.data.get('DOB')
        department = serializer.data.get('department')
        response = addteacher(email, name, DOB, department)
        if response == 'DNA':
            return Response({'msg': 'Domain not allowed'}, status=status.HTTP_400_BAD_REQUEST)
        elif response == 'EAE':
            return Response({'msg': 'User with this email already exists'}, status=status.HTTP_400_BAD_REQUEST)
        elif response == 'SEO':
            return Response({'msg': 'Some error occured! Please try again'}, status=status.HTTP_400_BAD_REQUEST)
        elif response == 'TCS':
            return Response({'msg': 'Teacher Created Successfully'}, status=status.HTTP_200_OK)


def addteacher(email, name, DOB, department):
    if checkemail(email):
        # Response({'msg': 'Domain not allowed'}, status=status.HTTP_400_BAD_REQUEST)
        return 'DNA'

    teachers = Teacher.objects.all().order_by('-userID')
    if len(teachers) != 0:
        userID = int(list(teachers)[0].userID)+1
    else:
        userID = 100000

    department = get_object_or_404(Department, id=department)
    # Default Password --> first_name in lowercase + @ + DOB(YYYYMMDD)
    password = name.split(" ")[0].lower() + '@' + DOB.replace("-", "")
    password = password[0].upper()+password[1:]
    email = email.lower()
    user = User.objects.filter(email=email)
    if user.exists():
        # Response({'msg': 'User with this email already exists'}, status=status.HTTP_400_BAD_REQUEST)
        return 'EAE'

    try:
        EMAIL.send_credentials_via_email(
            userID, password, name, email, 'teacher')
    except:
        # Response({'msg': 'Some error occured! Please try again'}, status=status.HTTP_400_BAD_REQUEST)
        return 'SEO'
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
    # Response({'msg': 'Teacher Created Successfully'}, status=status.HTTP_200_OK)
    return 'TCS'

# 3- API for performing CRUD operations on Departments


class Departments(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated, IsAdmin]

    def get(self, request, pk):
        if pk == 'ALL':
            departments = Department.objects.all()
            serializer = DepartmentSerializer(departments, many=True)
        else:
            departments = get_object_or_404(Department, id=pk)
            serializer = DepartmentSerializer(departments, many=False)
        return Response(serializer.data)

    def post(self, request, pk):
        serializer = DepartmentSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        if serializer.is_valid():
            serializer.save()
            return Response({'msg': 'Department added successfully'},  status=status.HTTP_200_OK)

    def put(self, request, pk):
        department = get_object_or_404(Department, id=pk)
        serializer = DepartmentSerializer(
            instance=department, data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response({'msg': 'Department modified successfully'},  status=status.HTTP_200_OK)

    def delete(self, request, pk):
        department = get_object_or_404(Department, id=pk)
        department.delete()
        return Response({'msg': 'Department deleted successfully'},  status=status.HTTP_200_OK)

# 4- API for performing CRUD operations on Classes


class ClassObject(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated, IsAdmin]

    def get(self, request, pk):
        if pk == 'ALL':
            allclasses = list(Class.objects.order_by(
                'year', 'department', 'section'))
            arr = []
            for clas in allclasses:
                arr += [[clas.year, clas.department.name,
                         clas.department.id, clas.section, clas.id]]
            return Response(arr, status=status.HTTP_200_OK)
        else:
            classes = get_object_or_404(Class, id=pk)
            serializer = ClassSerializer(classes, many=False)
            return Response(serializer.data)

    def post(self, request, pk):
        serializer = ClassSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response({'msg': 'Class added successfully'},  status=status.HTTP_200_OK)

    def put(self, request, pk):
        clas = get_object_or_404(Class, id=pk)
        serializer = ClassSerializer(instance=clas, data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response({'msg': 'Class modified successfully'},  status=status.HTTP_200_OK)

    def delete(self, request, pk):
        clas = get_object_or_404(Class, id=pk)
        clas.delete()
        return Response({'msg': 'Class deleted successfully'},  status=status.HTTP_200_OK)

# 5- API for getting classes by their departments


class ClassByDepartment(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated, IsAdmin]

    def get(self, request, departmentid):
        department = get_object_or_404(Department, id=departmentid)
        allclasses = Class.objects.all().filter(department=department)
        arr = []
        for clas in allclasses:
            arr += [[clas.id, clas.year, clas.section]]
        return Response(arr,  status=status.HTTP_200_OK)

# 6- API for performing CRUD operations on Subjects


class Subjects(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated, IsAdmin]

    def get(self, request, pk):
        if pk == 'ALL':
            subject = Subject.objects.all()
            serializer = SubjectSerializer(subject, many=True)
        else:
            subject = get_object_or_404(Subject, code=pk)
            serializer = SubjectSerializer(subject, many=False)
        return Response(serializer.data)

    def post(self, request, pk):
        serializer = SubjectSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response({'msg': 'Subject added successfully'},  status=status.HTTP_200_OK)

    def put(self, request, pk):
        subject = get_object_or_404(Subject, code=pk)
        serializer = SubjectSerializer(instance=subject, data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response({'msg': 'Subject modified successfully'},  status=status.HTTP_200_OK)

    def delete(self, request, pk):
        subject = get_object_or_404(Subject, code=pk)
        subject.delete()
        return Response({'msg': 'Subject deleted successfully'},  status=status.HTTP_200_OK)

# 7- API for viewing Feedbacks


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
            user = get_object_or_404(User, userID=key)
            stu = user.is_stu
            tea = user.is_tea
            if stu:
                student = Student.objects.get(userID=key)
            elif tea:
                teacher = Teacher.objects.get(userID=key)
            else:
                return Response({'msg': 'INVALID INPUT'},  status=status.HTTP_400_BAD_REQUEST)
            c = 0
            tf = 0
            if stu:
                feedbacks = list(
                    StudentFeedback.objects.filter(student=student))
            else:
                feedbacks = list(
                    TeacherFeedback.objects.filter(teacher=teacher))
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

# 8- API for creating attendance slots in a date range


class CreateAttendance(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated, IsAdmin]

    def post(self, request):
        serializer = CreateAttendanceSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        start_date = serializer.data.get("start_date")
        end_date = serializer.data.get("end_date")
        class_id = serializer.data.get("class_id")

        sdate = date(int(start_date[:4]), int(
            start_date[5:7]), int(start_date[8:]))
        edate = date(int(end_date[:4]), int(end_date[5:7]), int(end_date[8:]))
        n = (edate - sdate).days
        cur = sdate
        curclass = get_object_or_404(Class, id=class_id)
        students = Student.objects.filter(class_id=curclass)
        days = {1: 'Monday', 2: 'Tuesday', 3: 'Wednesday',
                4: 'Thursday', 5: 'Friday', 6: 'Saturday', 0: 'Sunday'}
        for i in range(n+1):
            curdate = cur
            curday = days[int(cur.strftime('%w'))]
            cur += timedelta(days=1)
            if curday == 'Sunday':
                continue
            assignedtimes = AssignTime.objects.filter(
                day=curday, class_id=curclass)

            for assignedtime in assignedtimes:
                try:
                    ca = ClassAttendance.objects.create(
                        date=curdate, assign=assignedtime)
                    for student in students:
                        StudentAttendance.objects.create(
                            student=student, classattendance=ca, subject=assignedtime.assign.subject)
                except IntegrityError:
                    continue

        return Response({'msg': 'Attendance Objects added successfully'},  status=status.HTTP_200_OK)

# 9- API for performing CRUD operations of assigning (teacher and subject) to a class


class Assigns(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated, IsAdmin]

    def get(self, request, class_id, subject_code, teacher_userID):
        class_assigns = AssignClass.objects.filter(class_id=class_id)
        dict = {}
        list = []
        for assign in class_assigns:
            dict = {
                "class_id": class_id,
                "subject_code": assign.subject.code,
                "subject_name": assign.subject.name,
                "teacher": assign.teacher.name,
                "teacher_userID": assign.teacher.userID
            }
            list.append(dict)
        return Response(list, status=status.HTTP_200_OK)

    def post(self, request, class_id, subject_code, teacher_userID):
        if (AssignClass.objects.filter(class_id__id=class_id,
                                       subject__code=subject_code)).exists():

            return Response({'msg': 'This subject is already assigned to this class'},
                            status=status.HTTP_400_BAD_REQUEST)

        class_id = get_object_or_404(Class, id=class_id)
        subject = get_object_or_404(Subject, code=subject_code)
        teacher = get_object_or_404(Teacher, userID=teacher_userID)

        AssignClass.objects.create(class_id=class_id,
                                   subject=subject,
                                   teacher=teacher)
        return Response({"msg": "Class has been assigned successfully."}, status=status.HTTP_200_OK)

    def put(self, request, class_id, subject_code, teacher_userID):

        serializer = AssignsSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        id = serializer.data.get("class_id")
        if (id != class_id):
            return Response({'msg': 'You cannot modify Class ID'},  status=status.HTTP_400_BAD_REQUEST)

        new_subject_code = serializer.data.get("subject_code")
        new_teacher_userID = serializer.data.get("teacher_userID")

        new_subject = get_object_or_404(Subject, code=new_subject_code)
        new_teacher = get_object_or_404(Teacher, userID=new_teacher_userID)

        assign = AssignClass.objects.filter(class_id__id=class_id,
                                            subject__code=subject_code,
                                            teacher__userID=teacher_userID)
        if not assign.exists():
            return Response({"msg": "No Assigns found"}, status=status.HTTP_200_OK)

        assign.update(subject=new_subject,
                      teacher=new_teacher)

        return Response({"msg": "Assigns has been updated successfully."}, status=status.HTTP_200_OK)

    def delete(self, request, class_id, subject_code, teacher_userID):

        assignedclass = get_object_or_404(AssignClass, class_id__id=class_id,
                                          subject__code=subject_code,
                                          teacher__userID=teacher_userID)

        assignedclass.delete()

        return Response({"msg": "Assign has been deleted successfully"}, status=status.HTTP_200_OK)

# 10- API for performing CRUD operations of assigning day and period to a Assigned Class


class AssignTimeSlots(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated, IsAdmin]

    def get(self, request, class_id, subject_code, teacher_userID):

        assigned_class = get_object_or_404(AssignClass, class_id=class_id,
                                           subject__code=subject_code,
                                           teacher__userID=teacher_userID)
        assigned_times = AssignTime.objects.filter(assign=assigned_class)
        list = []
        for time_slot in assigned_times:
            dict = {
                "id": time_slot.id,
                "day": time_slot.day,
                "period": time_slot.period
            }
            list.append(dict)
        return Response(list, status=status.HTTP_200_OK)

    def post(self, request, class_id, subject_code, teacher_userID):
        assigned_class = get_object_or_404(AssignClass, class_id=class_id,
                                           subject__code=subject_code,
                                           teacher__userID=teacher_userID)
        serializer = TimeSlotSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        day = serializer.data.get("day")
        period = serializer.data.get("period")
        if AssignTime.objects.filter(assign__class_id=class_id,
                                     day=day,
                                     period=period).exists():
            return Response({'msg': 'Time slot is already occupied'},  status=status.HTTP_400_BAD_REQUEST)
        klass = get_object_or_404(Class, id=class_id)
        teacher = get_object_or_404(Teacher, userID=teacher_userID)
        AssignTime.objects.create(
            assign=assigned_class,
            day=day,
            period=period,
            class_id=klass,
            teacher=teacher
        )
        return Response({"msg": "Time Slot has been Saved successfully"}, status=status.HTTP_200_OK)

    def put(self, request, class_id, subject_code, teacher_userID):
        time_slot_id = class_id
        time_slot = get_object_or_404(AssignTime, id=time_slot_id)
        assigned_class = time_slot.assign
        serializer = TimeSlotSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        new_day = serializer.data.get("day")
        new_period = serializer.data.get("period")
        if AssignTime.objects.filter(assign=assigned_class,
                                     day=new_day,
                                     period=new_period).exists():
            return Response({'msg': 'Time slot on this day is already occupied'},  status=status.HTTP_400_BAD_REQUEST)

        time_slot.day = new_day
        time_slot.period = new_period
        time_slot.save()

        return Response({"msg": "Time Slot has been Updated successfully"}, status=status.HTTP_200_OK)

    def delete(self, request, class_id, subject_code, teacher_userID):
        time_slot_id = class_id
        time_slot = get_object_or_404(AssignTime, id=time_slot_id)
        time_slot.delete()

        return Response({"msg": "Time Slot has been deleted successfully"}, status=status.HTTP_200_OK)

# 11- API for viewing the list of Students and their Attendance Percentage


class StudentAttendanceList(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated, IsTeacherorIsAdmin]

    def get(self, request, classid):
        students = Student.objects.filter(class_id=classid)
        list = []
        for student in students:
            total_classes = StudentAttendance.objects.filter(classattendance__assign__class_id=classid,
                                                             classattendance__status=True,
                                                             student__userID=student.userID).count()

            attended_classes = StudentAttendance.objects.filter(classattendance__assign__class_id=classid,
                                                                classattendance__status=True,
                                                                student__userID=student.userID,
                                                                is_present=True).count()

            if total_classes == 0:
                attendance_percent = 0
            else:
                attendance_percent = round(
                    attended_classes / total_classes * 100, 1)
            dict = {}
            dict = {
                "student_name": student.name,
                "userID": student.userID,
                "attendance_percent": attendance_percent
            }
            list.append(dict)
        return Response(list, status=status.HTTP_200_OK)

# 12- API for viewing the Attendance of all the subjects of a student


class StudentSubjectAttendance(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated, IsAdmin]

    def get(self, request, studentid):
        student = get_object_or_404(Student, userID=studentid)
        class_id = student.class_id
        subjects = AssignClass.objects.filter(class_id=class_id)
        list = []
        for subject in subjects:
            subject_name = subject.subject.name
            subject_code = subject.subject.code

            total_classes = StudentAttendance.objects.filter(classattendance__assign__class_id=class_id,
                                                             subject__code=subject_code,
                                                             classattendance__status=True,
                                                             student__userID=student.userID).count()

            attended_classes = StudentAttendance.objects.filter(classattendance__assign__class_id=class_id,
                                                                subject__code=subject_code,
                                                                classattendance__status=True,
                                                                student__userID=student.userID,
                                                                is_present=True).count()
            if total_classes == 0:
                attendance_percent = 0
            else:
                attendance_percent = round(
                    attended_classes / total_classes * 100, 1)
            dict = {}
            dict = {
                "subject_code": subject_code,
                "subject_name": subject_name,
                "attended_classes": attended_classes,
                "total_classes": total_classes,
                "attendance_percent": attendance_percent
            }
            list.append(dict)
        return Response(list, status=status.HTTP_200_OK)


class DeleteUser(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated, IsAdmin]

    def delete(self, request, userID):
        user = get_object_or_404(User, userID=userID)
        user.delete()
        return Response({"msg": "user deleted !!"}, status=status.HTTP_200_OK)


class Search(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated, IsAdmin]

    def get(self, request):
        search = request.GET.get('search')
        students = Student.objects.annotate(similarity=TrigramWordSimilarity(
            search, 'name'),).filter(similarity__gt=0.3).order_by('-similarity')
        teachers = Teacher.objects.annotate(similarity=TrigramWordSimilarity(
            search, 'name'),).filter(similarity__gt=0.3).order_by('-similarity')
        departments = Department.objects.annotate(similarity=TrigramWordSimilarity(
            search, 'name'),).filter(similarity__gt=0.3).order_by('-similarity')
        classes = Class.objects.annotate(similarity=TrigramWordSimilarity(
            search, 'id'),).filter(similarity__gt=0.3).order_by('-similarity')
        dict = {"students": [], "teachers": [],
                "departments": [], "classes": []}
        for student in students:
            dict["students"].append(student.name)
        for teacher in teachers:
            dict["teachers"].append(teacher.name)
        for department in departments:
            dict["departments"].append(department.name)
        for clas in classes:
            dict["classes"].append(clas.id)
        return Response(dict, status=status.HTTP_200_OK)


class AddUserBulk(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated, IsAdmin]

    def post(self, request, user):
        serializer = FileSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        file = request.FILES.get('field_name')
        extension = os.path.splitext(file.name)[1]
        if extension == '.csv':
            df = pandas.read_csv(file)
        else:
            df = pandas.read_excel(file)
        datas = df.to_csv().strip()
        datas = datas.split('\n')[1:]
        serializerobject = []
        if user == 'students':
            dependancy = 'class_id'
        else:
            dependancy = 'department'
        for data in datas:
            data = data.split(',')[1:]
            serializerobject += [{"name": data[0].strip(),
                                  "DOB": data[1].strip(),
                                  "email": data[2].strip(),
                                  dependancy: data[3].strip()}]
        if user == 'students':
            serializer = AddStudentSerializer(data=serializerobject, many=True)
        else:
            serializer = AddTeacherSerializer(data=serializerobject, many=True)
        serializer.is_valid(raise_exception=True)
        addstatus = {}
        i = 1
        for data in serializer.data:
            if user == 'students':
                response = addstudent(
                    data['email'], data['name'], data['DOB'], data[dependancy])
            else:
                response = addteacher(
                    data['email'], data['name'], data['DOB'], data[dependancy])
            if response == 'DNA':
                addstatus["entry "+str(i)] = 'Domain not allowed'
            elif response == 'EAE':
                addstatus["entry " +
                          str(i)] = 'User with this email already exists'
            elif response == 'SEO':
                addstatus["entry " +
                          str(i)] = 'Some error occured! Please try again'
            elif response == 'SCS':
                addstatus["entry "+str(i)] = 'Student Created Successfully'
            elif response == 'TCS':
                addstatus["entry "+str(i)] = 'Teacher Created Successfully'
            i += 1
        return Response(addstatus,  status=status.HTTP_200_OK)
