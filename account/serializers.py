from rest_framework import serializers
from account.models import User 


class UserLoginSerializer(serializers.ModelSerializer):
  userID = serializers.IntegerField()
  class Meta:
    model = User
    fields = ['userID','password']


class SendOTPSerializer(serializers.Serializer):
  email = serializers.EmailField(max_length=255)
  class Meta:
    model = User
    fields = ['email']