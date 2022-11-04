from django.urls import path
from django.urls import path
from adminpanel.views import *

urlpatterns = [
    path('addstudent/', AddStudent.as_view(), name='addStudent'),
    path('addteacher/', AddTeacher.as_view(), name='addTeacher'),
]
