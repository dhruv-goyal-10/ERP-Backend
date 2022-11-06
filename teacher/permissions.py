from account.models import User
from rest_framework.permissions import BasePermission
from django.conf import settings
import jwt

class IsTeacherorIsAdmin(BasePermission):
    def has_permission(self, request, view):
        token = request.META.get('HTTP_AUTHORIZATION', " ").split(' ')[1]
        tokenset = jwt.decode(token, settings.SECRET_KEY, algorithms=['HS256'])
        userID = tokenset['userID']
        user = User.objects.get(userID=userID)
        perm = user.is_tea or user.is_admin
        return (perm)