from django.urls import path
from django.urls import path
from adminpanel.views import *

urlpatterns = [
    path('addstudent/', AddStudent.as_view(), name='addStudent'),
    path('addteacher/', AddTeacher.as_view(), name='addTeacher'),
    path('departments/<str:pk>/', Departments.as_view(), name='Departments'),
    path('classes/<str:pk>/', ClassObject.as_view(), name='Classes'),
    path('subjects/<str:pk>/', Subjects.as_view(), name='Subjects'),
]
