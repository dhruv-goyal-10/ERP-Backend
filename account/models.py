from unittest.util import _MAX_LENGTH
from django.db import models
from django.contrib.auth.models import BaseUserManager, AbstractBaseUser
from django.utils import timezone
from datetime import timedelta
from django.core.validators import MaxValueValidator, MinValueValidator
from django.core.exceptions import ValidationError

#  Custom User Manager


class UserManager(BaseUserManager):
    def create_user(self, email, name, userID, password=None, password2=None):
        """
        Creates and saves a User with the given email, name, User ID and password.
        """
        if not userID:
            raise ValueError('User must have an User ID')

        user = self.model(
            email=self.normalize_email(email),
            name=name,
            userID=userID,
        )

        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, name, userID, password=None):
        """
        Creates and saves a superuser with the given email, name, userID and password.
        """
        user = self.create_user(
            email,
            password=password,
            name=name,
            userID=userID,
        )
        user.is_admin = True
        user.save(using=self._db)
        return user

#  Custom User Model


class User(AbstractBaseUser):
    email = models.EmailField(
        verbose_name='Email',
        max_length=255,
        unique=True,
    )

    userID = models.IntegerField(
        verbose_name='User ID',
        unique=True,
    )

    name = models.CharField(max_length=200)
    is_admin = models.BooleanField(default=False)
    is_stu = models.BooleanField(default=False)
    is_tea = models.BooleanField(default=False)
    otp = models.CharField(max_length=4, null=True, blank=True)
    otp_created_at = models.DateTimeField(
        default=timezone.now()-timedelta(minutes=1))
    objects = UserManager()

    USERNAME_FIELD = 'userID'
    REQUIRED_FIELDS = ['name', 'email']

    def __str__(self):
        return self.email

    def has_perm(self, perm, obj=None):
        "Does the user have a specific permission?"
        # Simplest possible answer: Yes, always
        return self.is_admin

    def has_module_perms(self, app_label):
        "Does the user have permissions to view the app `app_label`?"
        # Simplest possible answer: Yes, always
        return True

    @property
    def is_staff(self):
        "Is the user a member of staff?"
        return self.is_admin

    @property
    def is_teacher(self):
        "Is the user a member of staff?"
        return self.is_tea

    @property
    def is_student(self):
        "Is the user a member of staff?"
        return self.is_stu


sex_choice = (
    ('Male', 'Male'),
    ('Female', 'Female')
)



class Department(models.Model):
    id = models.CharField(primary_key='True', max_length=100)
    name = models.CharField(max_length=200)

    def __str__(self):
        return self.name
    
class Class(models.Model):
    id = models.CharField(primary_key='True', max_length=100)
    department = models.ForeignKey(Department, on_delete=models.CASCADE)
    section = models.CharField(max_length=100)
    year = models.IntegerField()
    def __str__(self):
        department = Department.objects.get(name=self.department)
        return '%s : %s --> %d%s' % (department.name,self.id, self.year, self.section)
    
    class Meta:
        verbose_name_plural = 'Classes'
        
class Subject(models.Model):
    department = models.ManyToManyField(Department)
    code = models.CharField(primary_key='True', max_length=50)
    name = models.CharField(max_length=50)
    def __str__(self):
        return self.name
    
class Student(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    class_id = models.ForeignKey(Class, on_delete=models.CASCADE)
    userID = models.CharField(max_length=100)
    name = models.CharField(max_length=200)
    sex = models.CharField(
        max_length=10, choices=sex_choice, blank=True, null=True)
    DOB = models.DateField()

    picture = models.ImageField(upload_to='students/', default='', height_field=None,
                                width_field=None, max_length=100, blank=True, null=True)

    blood_group = models.CharField(max_length=20, blank=True, null=True)
    pincode = models.IntegerField(blank=True, null=True)
    address = models.CharField(max_length=200, blank=True, null=True)
    city = models.CharField(max_length=200, blank=True, null=True)
    state = models.CharField(max_length=200, blank=True, null=True)

    student_phone = models.BigIntegerField(blank=True, null=True, validators=[
                                           MinValueValidator(1000000000), MaxValueValidator(9999999999)])

    father_name = models.CharField(max_length=200, blank=True, null=True)
    father_phone = models.BigIntegerField(blank=True, null=True, validators=[
                                          MinValueValidator(1000000000), MaxValueValidator(9999999999)])
    mother_name = models.CharField(max_length=200, blank=True, null=True)
    mother_phone = models.BigIntegerField(blank=True, null=True, validators=[
                                          MinValueValidator(1000000000), MaxValueValidator(9999999999)])

    def __str__(self):
        return self.name


class Teacher(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    department = models.ForeignKey(Department, on_delete=models.CASCADE)
    userID = models.CharField(max_length=100)
    name = models.CharField(max_length=100)
    sex = models.CharField(
        max_length=10, choices=sex_choice, blank=True, null=True)
    DOB = models.DateField()
    picture = models.ImageField(upload_to='teachers/', height_field=None,width_field=None, max_length=100, blank=True, null=True)
    blood_group = models.CharField(max_length=20, blank=True, null=True)
    pincode = models.IntegerField(blank=True, null=True)
    address = models.CharField(max_length=200, blank=True, null=True)
    city = models.CharField(max_length=200, blank=True, null=True)
    state = models.CharField(max_length=200, blank=True, null=True)
    teacher_phone = models.BigIntegerField(blank=True, null=True, validators=[MinValueValidator(1000000000), MaxValueValidator(9999999999)])

    def __str__(self):
        return self.name
    

class TeacherFeedback(models.Model):
    teacher = models.ForeignKey(Teacher, on_delete=models.CASCADE)
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    feed = models.IntegerField(default=3,validators=[MaxValueValidator(5), MinValueValidator(1)])
    class Meta:
        unique_together = (('student', 'teacher'),)
        verbose_name_plural = 'Teacher Feedbacks'
        
    def __str__(self):
        return '%s' % (self.teacher.name)


class StudentFeedback(models.Model):
    teacher = models.ForeignKey(Teacher, on_delete=models.CASCADE)
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    feed = models.IntegerField(default=3,validators=[MaxValueValidator(5), MinValueValidator(1)])
    class Meta:
        unique_together = (('student', 'teacher'),)
        verbose_name_plural = 'Student Feedbacks'
        
    def __str__(self):
        return '%s' % (self.student.name)

class Update(models.Model):
    title = models.TextField()
    description = models.TextField()
    lastedit = models.DateTimeField(auto_now=True)
    showto = models.IntegerField(default=3)

    def __str__(self):
        return self.title

    class Meta:
        ordering = ['-lastedit']
        
        
TIME_SLOTS = (
    ('8:30 - 9:20', '8:30 - 9:20'),
    ('9:20 - 10:10', '9:20 - 10:10'),
    ('11:00 - 11:50', '11:00 - 11:50'),
    ('11:50 - 12:40', '11:50 - 12:40'),
    ('1:30 - 2:20', '1:30 - 2:20'),
)

DAYS = (
    ('Monday', 'Monday'),
    ('Tuesday', 'Tuesday'),
    ('Wednesday', 'Wednesday'),
    ('Thursday', 'Thursday'),
    ('Friday', 'Friday'),
    ('Saturday', 'Saturday'),
)

class AssignClass(models.Model):
    class_id = models.ForeignKey(Class, on_delete=models.CASCADE)
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE)
    teacher = models.ForeignKey(Teacher, on_delete=models.CASCADE, related_name = "assignclass_teacher")

    class Meta:
        unique_together = (('subject', 'class_id'),)
        verbose_name_plural = 'Assign Classes'
        
    def __str__(self):
        return '%s' % (self.class_id)
class AssignTime(models.Model):
    assign = models.ForeignKey(AssignClass, on_delete=models.CASCADE)
    period = models.CharField(max_length=50, choices=TIME_SLOTS, default='11:00 - 11:50')
    day = models.CharField(max_length=15, choices=DAYS)
    class_id = models.ForeignKey(Class, on_delete=models.CASCADE, null=True)
    teacher = models.ForeignKey(Teacher, on_delete=models.CASCADE, null=True)
    class Meta:
        unique_together = (('period', 'day', 'class_id'),('period', 'day', 'teacher'),)
        
    def __str__(self):
        return '%s : %s --> %s' % (self.class_id.id,self.day, self.period)
    
    
class ClassAttendance(models.Model):
    assign = models.ForeignKey(AssignTime, on_delete=models.CASCADE)
    date = models.DateField()
    status = models.BooleanField(default=False)
    
    class Meta:
        unique_together = (('assign', 'date'),)


class StudentAttendance(models.Model):
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE)
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    classattendance = models.ForeignKey(ClassAttendance, on_delete=models.CASCADE)
    is_present = models.BooleanField(default=True)


