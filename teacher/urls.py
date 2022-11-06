from django.urls import path
from django.urls import path
from teacher.views import *

urlpatterns = [
    path('studentinclass/<str:classid>/', StudentInClass.as_view(), name='studentclassfilter'),
    path('teachersofclass/<str:classid>/', TeacherOfClass.as_view(), name='teacherclassfilter')
]
