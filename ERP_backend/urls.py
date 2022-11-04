from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/user/', include('account.urls')),
    path('api/user/admin/', include('adminpanel.urls')),
    path('api/user/teacher/', include('teacher.urls')),
    path('api/user/student/', include('student.urls')),
]
