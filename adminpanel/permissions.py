from account.models import User
from rest_framework.permissions import BasePermission
from django.conf import settings
import jwt

class IsAdmin(BasePermission):
    def has_permission(self, request, view):
        token = request.META.get('HTTP_AUTHORIZATION', " ").split(' ')[1]
        tokenset = jwt.decode(token, settings.SECRET_KEY, algorithms=['HS256'])
        userID = tokenset['userID']
        user = User.objects.get(userID=userID)
        print(user)
        return user.is_admin