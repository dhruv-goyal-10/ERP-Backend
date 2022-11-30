from rest_framework import serializers
from rest_framework.serializers import ModelSerializer
from account.models import *
import re
from django.shortcuts import get_object_or_404
from django.contrib.auth import authenticate
from .emails import *
from rest_framework_simplejwt.tokens import RefreshToken
import os
from django.core.exceptions import ValidationError


def get_tokens_for_user(user):
    refresh = RefreshToken.for_user(user)
    refresh['userID'] = user.userID
    return {
        'refresh': str(refresh),
        'access': str(refresh.access_token),
    }

def normalize_email(email):
        # remove spaces at start and end & lowercase email address
        email = email.strip().lower()
        # split email into username and domain information
        username, domain = email.split('@')
        # remove . characters from username
        username = username.replace('.', '')
        #remove everything after +
        username = username.split('+')[0]
        return "%s@%s" % (username, domain)
    
def matchotp(enteredOTP, user):
    userOTP = OTP.objects.get(user=user)
    generatedOTP = userOTP.otp
    generatedTIME = userOTP.otp_created_at
    expirestatus = userOTP.isexpired
    if expirestatus is True:
        return 'expired'
    if int(enteredOTP) == generatedOTP:
        if generatedTIME + timedelta(minutes=5) > timezone.now():
            return 'matched'
        userOTP.isexpired = True
        userOTP.save()
        return 'expired'
    return 'notmatched'

def check_strong_password(password):
    
    if not re.findall('\d', password):
            raise ValidationError(
                ("The password must contain at least 1 Digit, 0-9."),
                code='password_no_number',
            )
            
    if not re.findall('[A-Z]', password):
        raise ValidationError(
            ("The password must contain at least 1 Uppercase Letter, A-Z."),
            code='password_no_upper',
        )
        
    if not re.findall('[a-z]', password):
        raise ValidationError(
            ("The password must contain at least 1 Lowercase Letter, a-z."),
            code='password_no_lower',
        )
        
    if not re.findall('[!@#$]', password):
        raise ValidationError(
            ("The password must contain at least 1 Special Character, a-z."),
            code='password_no_special',
            )
    
class UserLoginSerializer(serializers.Serializer):
    userID = serializers.IntegerField()
    password = serializers.CharField(min_length=8, max_length=255)
    
    def save(self):
        userID = self.validated_data["userID"]
        password = self.validated_data["password"]
        user = authenticate(userID=userID, password=password)
            
        if user is None:
            raise ValidationError( "UserID or Password is not Valid", code = "invalid")
        else:
            if user.is_stu:
                designation = "Student"
            elif user.is_tea:
                designation = "Teacher"
            else:
                designation = "Admin"
            token = get_tokens_for_user(user)
            return{
                "Token": token,
                "Username": user.name,
                "Msg": "Login Successful",
                "Designation": designation
            }
            
# class EmailSerializer(serializers.Serializer):
#     email = serializers.EmailField()
        
class SendOTPSerializer(serializers.Serializer):
    email = serializers.EmailField(max_length=255)
    
    def validate_email(self, email):
        email = normalize_email(email)
        try:
            user = User.objects.get(email=email)
        except:
            raise ValidationError("You are not registered with this email ID")
        return email
    
    def save(self):
        email = self.validated_data["email"]
        user = User.objects.get(email=email)
        otprelation = OTP.objects.get(user=user)
        
        if otprelation.otp_created_at + timedelta(minutes=1) < timezone.now():
            EMAIL.send_otp_via_email(email)
        else:
            raise ValidationError('WAIT FOR 1 minute before resending OTP', code = "wait")

        


class VerifyOTPSerializer(serializers.Serializer):
    email = serializers.EmailField(max_length=255)
    otp = serializers.CharField(min_length=4, max_length=4)
    
    def validate_email(self, email):
        email = normalize_email(email)
        try: 
            user = User.objects.get(email=email)
        except: 
            raise ValidationError("Invalid Email ID")
        return email
    
    def save(self):
        email = self.validated_data["email"]
        entered_otp = self.validated_data["otp"]
        user = User.objects.get(email=email)
        
        otp_status = matchotp(entered_otp, user)
        
        if otp_status == 'notmatched':
            raise ValidationError("Wrong OTP Entered", code='notmatched',)

        elif otp_status == 'expired':
            raise ValidationError("OTP Expired", code='expired',)
        
        

class ForgotPasswordSerializer(serializers.Serializer):
    email = serializers.EmailField(max_length=255)
    otp = serializers.CharField(min_length=4, max_length=4)
    password = serializers.CharField(min_length=8, max_length=255)
    confirmpassword = serializers.CharField(min_length=8, max_length=255)
    
    def validate_email(self,email):
        email = self.initial_data["email"]
        email = normalize_email(email)
        return email
    
    def validate_password(self, password):
        
        check_strong_password(password)
        
        return password
    
    def validate_otp(self, entered_otp):
        email = self.initial_data["email"]
        email = normalize_email(email)
        user = get_object_or_404(User, email=email)
        
        otp_status= matchotp(entered_otp, user)
        
        if otp_status == 'notmatched':
            raise ValidationError(("Authorization Failed"))
        elif otp_status == 'expired':
            raise ValidationError(("RESET PASSWORD TIMEOUT, GENERATE ANOTHER OTP"))
        return entered_otp
    
    def save(self):
        user = get_object_or_404(User, email=self.validated_data["email"])
        new_password = self.validated_data["password"]
        checkUser = authenticate(userID=user.userID, password=new_password)
        if checkUser is not None:
            raise ValidationError(("Password entered is same as old one"))
        
        user.set_password(new_password)
        user.save()
        otprelation = get_object_or_404(OTP, user=user)
        otprelation.isexpired = True
        otprelation.save()
        
        
class UpdatePasswordSerializer(serializers.Serializer):
    prevpassword = serializers.CharField(min_length=8, max_length=255)
    newpassword = serializers.CharField(min_length=8, max_length=255)
    confirmpassword = serializers.CharField(min_length=8, max_length=255)
    
    def validate_prevpassword(self, prevpassword):
    
        userID=self.context.get('userID')
        check = authenticate(userID=userID, password=prevpassword)
        if check is None:
            raise ValidationError(("Previous Password is incorrect"))
        
        return prevpassword
    
    def validate_newpassword(self, password):
        
        check_strong_password(password)
        
        if password == self.initial_data["prevpassword"]:
            raise ValidationError(("Password entered is same as old one"))
        return password
    
    def validate_confirmpassword(self, confirmpassword):
        if confirmpassword != self.initial_data["newpassword"]:
            raise ValidationError(("Password and Confirm password doesn't match"))
        return confirmpassword
    
    def save(self):
        userID=self.context.get('userID')
        user = authenticate(userID=userID, password=self.validated_data["prevpassword"])
        user.set_password(self.validated_data["newpassword"])
        user.save()  
        
              
class AddStudentSerializer(ModelSerializer):
    email = serializers.EmailField(max_length=255)

    class Meta:
        model = Student
        fields = ['name', 'class_id', 'email', 'DOB']


class AddTeacherSerializer(ModelSerializer):
    email = serializers.EmailField(max_length=255)

    class Meta:
        model = Teacher
        fields = ['name', 'department', 'email', 'DOB']




class StudentProfileSerializer(ModelSerializer):
    class Meta:
        model = Student
        fields = ['sex', 'DOB', 'picture', 'blood_group', 'pincode', 'address', 'city', 'state',
                  'student_phone', 'father_name', 'father_phone', 'mother_name', 'mother_phone', ]


class TeacherProfileSerializer(ModelSerializer):
    class Meta:
        model = Teacher
        fields = ['sex', 'DOB', 'picture', 'blood_group',
                  'pincode', 'address', 'city', 'state', 'teacher_phone']


class UpdateSectionSerializer(ModelSerializer):

    class Meta:
        model = Update
        fields = '__all__'


class AssignTimeSerializer(ModelSerializer):

    class Meta:
        model = AssignTime
        fields = ['period', 'day', 'assign']


class AssignClassSerializer(ModelSerializer):

    class Meta:
        model = AssignClass
        fields = '__all__'


class CreateAttendanceSerializer(serializers.Serializer):
    start_date = serializers.DateField()
    end_date = serializers.DateField()
    class_id = serializers.CharField(max_length=10)


class StudentAttendanceSerializer(ModelSerializer):
    class Meta:
        model = StudentAttendance
        fields = '__all__'


class AssignsSerializer(serializers.Serializer):
    class_id = serializers.CharField(max_length=10)
    subject_code = serializers.CharField()
    teacher_userID = serializers.IntegerField()


class TimeSlotSerializer(serializers.Serializer):
    period = serializers.ChoiceField(choices=TIME_SLOTS)
    day = serializers.ChoiceField(choices=DAYS)


class FileSerializer(serializers.Serializer):
    file = serializers.FileField()
    
    def validate_file(self, file):
        ext = os.path.splitext(file.name)[1]  # [0] returns path+filename
        valid_extensions = ['.xlsx', '.xls', '.csv']
        if not ext.lower() in valid_extensions:
            raise ValidationError('Unsupported file extension.')
    

class ClassAttendanceSerializer(serializers.ModelSerializer):
    class Meta:
        model = ClassAttendance
        fields = '__all__'
    
    def to_representation(self, instance):
        data = super().to_representation(instance)
        data.clear()
        # data.pop('id')
        data["period"] = instance.assign.period
        data["class_id"] = instance.assign.assign.class_id.id
        data["subject_name"] = instance.assign.assign.subject.code
        data["subject_code"] = instance.assign.assign.subject.code
        data["teacher_userID"]= instance.assign.assign.teacher.userID
        data["status"]= instance.status
    
        return data


class DepartmentSerializer(ModelSerializer):

    class Meta:
        model = Department
        fields = '__all__'


class ClassSerializer(ModelSerializer):
    class Meta:
        model = Class
        fields = '__all__'


class SubjectSerializer(ModelSerializer):
    class Meta:
        model = Subject
        fields = '__all__'


class StudentSubjectAttendance(ModelSerializer):
    date = serializers.DateField(source='classattendance.date')
    day = serializers.CharField(source='classattendance.assign.day')
    period = serializers.CharField(source='classattendance.assign.period')

    class Meta:
        model = StudentAttendance
        fields = ['date', 'day', 'period', 'is_present']


class FeedbackSerializer(ModelSerializer):
    class Meta:
        model = TeacherFeedback
        fields = '__all__'


class TeacherList(ModelSerializer):
    class Meta:
        model = Teacher
        fields = ['userID', 'name']


class StudentList(ModelSerializer):
    class Meta:
        model = Student
        fields = ['userID', 'name']


class StudentFeedbackSerializer(ModelSerializer):
    studentname = serializers.CharField(source = 'student.name')
    class Meta:
        model = StudentFeedback
        fields = ['studentname', 'feed']


class AttendanceObjectsSerializer(ModelSerializer):
    period = serializers.CharField(source = 'assign.period')
    class_id = serializers.CharField(source = 'assign.class_id.id')
    subject_name = serializers.CharField(source = 'assign.assign.subject.name')
    subject_code = serializers.CharField(source = 'assign.assign.subject.code')
    teacher_userID = serializers.CharField(source = 'assign.assign.teacher.userID')
    class Meta:
        model = ClassAttendance
        fields = ['date', 'period', 'class_id', 'subject_name', 'subject_code', 'teacher_userID', 'status']
    
