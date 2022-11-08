from django.urls import path
from django.urls import path
from student.views import *

urlpatterns = [
    path('profiledetails/', ProfileDetails.as_view(), name='profiledetails'),
    path('teacherfeedback/<str:teacher>/', TeacherFeedbackView.as_view(), name='teacherfeedback'),
]
