from django.shortcuts import render
from .serializers import UserSerializer
from rest_framework import status
from django.contrib.auth import get_user_model
from maantra.base import NewAPIView
from maantra.response import error_response, s_406, s_201
from rest_framework.response import Response
from django.core.validators import validate_email
from django.core.exceptions import ValidationError
User = get_user_model()

# Create your views here.
class UserRegistrationAPIView(NewAPIView):
    serializer_class = UserSerializer
    def post(self, request):
        '''
        **This API is for User Registration. **\n
        After Creating User, It will return User Data with 201 Created Response
        
        Required Fields: \n
        - email \n
        - contact \n
        - password \n
        - confirm_password
        '''
        data = request.data
        email = data.get('email')
        contact = data.get('contact')
        password = data.get('password')
        confirm_password = data.get('confirm_password')
        
        if not all(['email', 'contact', 'password', 'confirm_password']):
            return s_406("All fields ")
        try:
            validate_email(email)
        except ValidationError:
            return Response({"error": "Email is not valid"}, status=status.HTTP_400_BAD_REQUEST)
        if User.objects.filter(email=email).exists():
            return Response({"error": "Email already exists"}, status=status.HTTP_400_BAD_REQUEST)
        User.objects.create(email=email, contact=contact, password=password)
        return s_201("User")
            