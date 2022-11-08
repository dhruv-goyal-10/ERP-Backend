from rest_framework.response import Response
from rest_framework import status
from rest_framework.views import APIView
from account.serializers import *
from account.models import *
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.permissions import IsAuthenticated
import jwt
from django.conf import settings


class ProfileDetails(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request):
        token = request.META.get('HTTP_AUTHORIZATION', " ").split(' ')[1]
        tokenset = jwt.decode(token, settings.SECRET_KEY, algorithms=['HS256'])
        userID = tokenset['userID']

        student = Student.objects.get(userID=userID)
        serializer = StudentProfileSerializer(student, many=False)

        user = User.objects.get(userID=userID)
        eserializer = EmailSerializer(user, many=False)

        return Response(serializer.data | eserializer.data)

    def put(self, request):
        token = request.META.get('HTTP_AUTHORIZATION', " ").split(' ')[1]
        tokenset = jwt.decode(token, settings.SECRET_KEY, algorithms=['HS256'])
        userID = tokenset['userID']
        student = Student.objects.get(userID=userID)
        serializer = StudentProfileSerializer(student, data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        # Updating the name in User Model
        name = serializer.validated_data.get('name')
        user = User.objects.get(userID=userID)
        user.name = name
        user.save()

        return Response(serializer.data, status=status.HTTP_202_ACCEPTED)
    
class TimeTable(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]
    
    def get(self, request, pk):
        times = AssignTime.objects.filter(assign__class_id=pk)
        classes = AssignClass.objects.filter(class_id=pk)
        list = []
        for klass in classes:
            dict={}
            dict= {"class" : klass.class_id.id, "subject" : klass.subject.name, "teacher" : klass.teacher.name}
            for time in times:
                if time.assign.id == klass.id:
                    dict|= {"period" : time.period, "day" : time.day}
            list.append(dict)
        return Response(list,  status=status.HTTP_200_OK)

