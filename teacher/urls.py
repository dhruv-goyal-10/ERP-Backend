from django.urls import path
from teacher.views import *

urlpatterns = [
    path('subjectsindepartment/<str:pk>/', SubjectsInDepartments.as_view(), name='subjectdepartmentfilter'),
    path('teachersindepartment/<str:pk>/', TeachersInDepartments.as_view(), name='teacherdepartmentfilter'),
]
