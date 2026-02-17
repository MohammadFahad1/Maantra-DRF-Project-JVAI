from rest_framework import serializers
from .models import User

class UserSerializer(serializers.ModelSerializer):
    confirm_password = serializers.CharField(write_only=True)
    class Meta:
        model = User
        fields = ['email', 'contact', 'password', 'confirm_password']
        extra_kwargs = {'password': {'write_only': True}}