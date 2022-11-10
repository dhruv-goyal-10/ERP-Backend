from django.urls import path
from teacher.views import *

urlpatterns = [
    path('profiledetails/', TProfileDetails.as_view(), name='teacherprofiledetails'),

    path('studentinclass/', StudentInClass.as_view(), name='studentclassfilter'),
    path('studentinclass/<str:feedback>/', StudentInClass.as_view(), name='studentclassfeedback'),
 
    path('teachersofclass/', TeacherOfClass.as_view(), name='teacherclassfilter'),
    path('teachersofclass/<str:feedback>/', TeacherOfClass.as_view(), name='teacherclassfeedback'),
    
    path('subjectsindepartment/', SubjectsInDepartments.as_view(), name='subjectdepartmentfilter'),
    path('teachersindepartment/', TeachersInDepartments.as_view(), name='teacherdepartmentfilter'),
    path('studentfeedback/', StudentFeedbackView.as_view(), name='studentfeedback'),
    path('classofteacher/', ClassOfTeacher.as_view(), name='classofteacherfilter'),
    path('timetable/', TimeTable.as_view(), name='TimeTable'),
    path('StudentsinClassAttendance/', StudentsinClassAttendance.as_view(), name='StudentsinClassAttendance'),
]
