from unittest.util import _MAX_LENGTH
from django.db import models
from django.contrib.auth.models import BaseUserManager,AbstractBaseUser

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
      primary_key=True
  )

  name = models.CharField(max_length=200)
  IN = models.IntegerField(default=0)
#   is_active = models.BooleanField(default=True)
#   created_at = models.DateTimeField(auto_now_add=True)
#   updated_at = models.DateTimeField(auto_now=True)
  is_admin = models.BooleanField(default=False)
  is_stu = models.BooleanField(default=False)
  is_tea = models.BooleanField(default=False)
  otp = models.CharField(max_length=4, null=True, blank=True)
  otp_created_at = models.DateTimeField(null = True)
  objects = UserManager()

  USERNAME_FIELD = 'userID'
  REQUIRED_FIELDS = ['name', 'email']

  def __str__(self):
      return self.name

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
      # Simplest possible answer: All admins are staff
      return self.is_admin

  @property
  def is_teacher(self):
      "Is the user a member of staff?"
      # Simplest possible answer: All admins are staff
      return self.is_tea

  @property
  def is_student(self):
      "Is the user a member of staff?"
      # Simplest possible answer: All admins are staff
      return self.is_stu


sex_choice = (
    ('Male', 'Male'),
    ('Female', 'Female')
)

class Student(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, null=True)
    userID = models.CharField(primary_key='True', max_length=100)
    name = models.CharField(max_length=200)
    sex = models.CharField(max_length=10,choices=sex_choice, blank=True,null= True)
    DOB = models.DateField(blank=True,null= True)

    def __str__(self):
        return self.name


class Teacher(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, null=True)
    userID = models.CharField(primary_key=True, max_length=100)
    # dept = models.ForeignKey(Dept, on_delete=models.CASCADE, default=1)
    name = models.CharField(max_length=100)
    sex = models.CharField(max_length=10,choices=sex_choice,blank=True,null= True)
    DOB = models.DateField(blank=True,null= True)

    def __str__(self):
        return self.name
