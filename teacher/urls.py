from django.urls import path
from teacher.views import *

urlpatterns = [
    path('profiledetails/', TProfileDetails.as_view()),
    path('studentinclass/<str:classid>/', StudentInClass.as_view()),
    path('studentinclassfeedback/<str:classid>/', StudentInClassFeedback.as_view()),
    path('teachersofclass/<str:classid>/', TeacherOfClass.as_view()),
    path('teachersofclass/<str:classid>/<str:feedback>/', TeacherOfClass.as_view()),
    path('subjectsindepartment/<str:departmentid>/', SubjectsInDepartments.as_view()),
    path('teachersindepartment/<str:departmentid>/', TeachersInDepartments.as_view()),
    path('studentfeedback/', StudentFeedbackView.as_view()),
    path('classofteacher/<str:pk>/', ClassOfTeacher.as_view()),

    path('timetable/', TimeTable.as_view(), name='TimeTable'),
    path('ClassAttendanceObjects/', ClassAttendanceObjects.as_view(),
         name='ClassAttendanceObjects'),
    path('TakeStudentsAttendance/<str:date>/<str:class_id>/<str:period>/',
         TakeStudentsAttendance.as_view(), name='StudentsinClassAttendance'),

    path('CreateTodayAttendance/', CreateTodayAttendance.as_view(),
         name='CreateTodayAttendance')
]
