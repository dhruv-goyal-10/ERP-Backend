from rest_framework import serializers
from rest_framework.serializers import ModelSerializer
from account.models import *


class DepartmentSerializer(ModelSerializer):

    class Meta:
        model = Department
        fields = '__all__'


class ClassSerializer(ModelSerializer):
    class Meta:
        model = Class
        fields = ['id', 'year', 'section']