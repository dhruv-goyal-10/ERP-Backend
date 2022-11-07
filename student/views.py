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


class TeacherFeedbackView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def post(self, request, teacher):
        token = request.META.get('HTTP_AUTHORIZATION', " ").split(' ')[1]
        tokenset = jwt.decode(token, settings.SECRET_KEY, algorithms=['HS256'])
        userID = tokenset['userID']
        try:
            student = Student.objects.get(userID=userID)
        except:
            return Response({'msg': 'NOT ALLOWED'},  status=status.HTTP_400_BAD_REQUEST)
        try:
            teacher = Teacher.objects.get(userID=teacher)
        except:
            return Response({'msg': 'teacher does not exist'},  status=status.HTTP_400_BAD_REQUEST)
        feed = request.data.get('feed')
        if feed is None:
            feed = 3
        try:
            TeacherFeedback(
                teacher = teacher,
                student = student,
                feed = feed
            ).save()
        except:
            return Response({'msg': 'already submitted'},  status=status.HTTP_400_BAD_REQUEST)
        return Response({'msg': 'Feedback Submitted Successfully !!'}, status=status.HTTP_200_OK)