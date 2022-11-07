from django.urls import path
from teacher.views import *

urlpatterns = [
    path('studentinclass/<str:classid>/', StudentInClass.as_view(), name='studentclassfilter'),
    path('teachersofclass/<str:classid>/', TeacherOfClass.as_view(), name='teacherclassfilter'),
    path('subjectsindepartment/<str:pk>/', SubjectsInDepartments.as_view(), name='subjectdepartmentfilter'),
    path('teachersindepartment/<str:pk>/', TeachersInDepartments.as_view(), name='teacherdepartmentfilter'),
    path('studentfeedback/<str:student>/', StudentFeedbackView.as_view(), name='studentfeedback'),
]


