from rest_framework import serializers
from .models import UserTab,RegisterFace

class UserTabSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserTab
        fields = ['serial', 'name', 'email', 'department_id', 'access']


class RegisterFaceSerializer(serializers.ModelSerializer):
    class Meta:
        model = RegisterFace
        fields = ['name', 'mobile_number', 'email', 'address', 'department_id','access']
