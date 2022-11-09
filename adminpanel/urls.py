from django.urls import path
from django.urls import path
from adminpanel.views import *

urlpatterns = [
    path('addstudent/', AddStudent.as_view(), name='addStudent'),
    path('addteacher/', AddTeacher.as_view(), name='addTeacher'),
    path('departments/', Departments.as_view(), name='Departments'),
    path('classes/', ClassObject.as_view(), name='Classes'),
    path('classesindepartment/',ClassByDepartment.as_view(), name='classdepartmentfilter'),
    path('subjects/', Subjects.as_view(), name='Subjects'),
    path('feedback/', FeedbackView.as_view(), name='Feedbacks'),
]
