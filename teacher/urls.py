from django.urls import path
from teacher.views import *

urlpatterns = [
    path('profiledetails/', TProfileDetails.as_view(), name='teacherprofiledetails'),

    path('studentinclass/<str:classid>/', StudentInClass.as_view(), name='studentclassfilter'),
    path('studentinclass/<str:classid>/<str:feedback>/', StudentInClass.as_view(), name='studentclassfeedback'),
 
    path('teachersofclass/<str:classid>/', TeacherOfClass.as_view(), name='teacherclassfilter'),
    path('teachersofclass/<str:classid>/<str:feedback>/', TeacherOfClass.as_view(), name='teacherclassfeedback'),
   
    path('subjectsindepartment/<str:pk>/', SubjectsInDepartments.as_view(), name='subjectdepartmentfilter'),
    
    path('teachersindepartment/<str:pk>/', TeachersInDepartments.as_view(), name='teacherdepartmentfilter'),
    
    path('studentfeedback/<str:student>/', StudentFeedbackView.as_view(), name='studentfeedback'),
    
    path('classofteacher/<str:teacherid>/', ClassOfTeacher.as_view(), name='classofteacherfilter'),
    
    path('timetable/', TimeTable.as_view(), name='TimeTable'),
]
