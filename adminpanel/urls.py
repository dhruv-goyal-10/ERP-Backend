from django.urls import path
from django.urls import path
from adminpanel.views import *

urlpatterns = [
    path('addstudent/', AddStudent.as_view(), name='addStudent'),
    path('addteacher/', AddTeacher.as_view(), name='addTeacher'),

    path('departments/', DepartmentsLC.as_view()),
    path('departments/<str:pk>/', DepartmentsRUD.as_view()),

    path('classes/', ClassesLC.as_view()),
    path('classes/<str:pk>/', ClassesRUD.as_view()),

    path('classesindepartment/<str:pk>/', ClassByDepartment.as_view()),

    path('subjects/', SubjectsLC.as_view()),
    path('subjects/<str:pk>/', SubjectsRUD.as_view()),

    path('feedback/<str:key>/', FeedbackView.as_view(), name='Feedbacks'),
    path('createattendance/', CreateAttendance.as_view(), name='createattendance'),
    path('assignclass/<str:class_id>/<str:subject_code>/<str:teacher_userID>/',
         Assigns.as_view(), name='assignclass'),
    path('assigntimeslots/<str:class_id>/<str:subject_code>/<str:teacher_userID>/',
         AssignTimeSlots.as_view(), name='assigntimeslots'),
    path('studentattendancelist/<str:classid>/',
         StudentAttendanceList.as_view(), name='attendancelist'),
    path('studentsubjectattendancelist/<str:studentid>/',
         StudentSubjectAttendance.as_view(), name='studentsubjectattendance'),
    path('deleteuser/<str:userID>/', DeleteUser.as_view(), name='deleteuser'),
    path('search/', Search.as_view(), name='search'),
    path('adduserbulk/<str:user>/', AddUserBulk.as_view(),
         name='updatesectionthroughparams'),
]
