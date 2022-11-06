from django.urls import path
from django.urls import path
from teacher.views import *

urlpatterns = [
    path('studentinclass/', StudentInClass.as_view(), name='studentclassfilter')
]
