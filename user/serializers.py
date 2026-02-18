from rest_framework import serializers
from .models import User

class UserSerializer(serializers.ModelSerializer):
    confirm_password = serializers.CharField(write_only=True)
    class Meta:
        model = User
        fields = ['email', 'contact', 'password', 'confirm_password']
        extra_kwargs = {'password': {'write_only': True}}
        
    def validate(self, data):
        if data['password'] != data['confirm_password']:
            raise serializers.ValidationError("Password and confirm password do not match")
        elif(User.objects.filter(email=data['email']).exists()):
            raise serializers.ValidationError("Email already exists")
        return data
    
    
