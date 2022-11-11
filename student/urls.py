from django.urls import path
from django.urls import path
from student.views import *

urlpatterns = [
    path('profiledetails/', SProfileDetails.as_view(), name='studentprofiledetails'),
    path('teacherfeedback/', TeacherFeedbackView.as_view(), name='teacherfeedback'),
    path('timetable/', TimeTable.as_view(), name='timetable'),
    path('studentoverallattendance/', StudentOverallAttendance.as_view(), name='StudentOverallAttendance'),
    path('studentsubjectattendance/<str:subject_code>/<str:month>/', StudentSubjectAttendance.as_view(), name='StudentSubjectAttendance'),
]
