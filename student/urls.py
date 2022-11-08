from django.urls import path
from django.urls import path
from student.views import *

urlpatterns = [
    path('profiledetails/', SProfileDetails.as_view(), name='studentprofiledetails'),
    path('teacherfeedback/<str:teacher>/', TeacherFeedbackView.as_view(), name='teacherfeedback'),
]
