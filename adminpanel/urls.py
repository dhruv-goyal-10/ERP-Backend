from django.urls import path
from django.urls import path
from adminpanel.views import *

urlpatterns = [
    path('addstudent/', AddStudent.as_view(), name='addStudent'),
    path('addteacher/', AddTeacher.as_view(), name='addTeacher'),
    path('departments/<str:pk>/', Departments.as_view(), name='Departments'),
    path('classes/<str:pk>/', ClassObject.as_view(), name='Classes'),
    path('classesindepartment/<str:departmentid>/',
         ClassByDepartment.as_view(), name='classdepartmentfilter'),
    path('subjects/<str:pk>/', Subjects.as_view(), name='Subjects'),
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
