from django.shortcuts import render
from .serializers import UserSerializer, UserLoginSerializer
from rest_framework import status
from django.contrib.auth import get_user_model, authenticate
from maantra.base import NewAPIView
from maantra.response import error_response, s_406, s_201
from rest_framework.response import Response
from django.core.validators import validate_email
from django.core.exceptions import ValidationError
from rest_framework_simplejwt.tokens import RefreshToken
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
        
        if password != confirm_password:
            return Response({"error": "Password and Confirm Password does not match"}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            validate_email(email)
        except ValidationError:
            return Response({"error": "Email is not valid"}, status=status.HTTP_400_BAD_REQUEST)
        if User.objects.filter(email=email).exists():
            return Response({"error": "Email already exists"}, status=status.HTTP_400_BAD_REQUEST)
        User.objects.create(email=email, contact=contact, password=password)
        return s_201("User")

class UserLoginAPIView(NewAPIView):
    serializer_class = UserLoginSerializer
    def post(self, request):
        '''
        **This API is for User Login.**\n
        After Login, It will return Access token, Refresh token and User data with 200 OK Response
        
        Required Fields: \n
        - email \n
        - password
        '''
        data = request.data
        email = data.get('email')
        password = data.get('password')
        
        if not all(['email', 'password']):
            return s_406('All Fields')
        try:
            validate_email(email)
        except ValidationError:
            return Response({"error": "Email is not valid"}, status=status.HTTP_400_BAD_REQUEST)
        
        if not User.objects.filter(email=email).exists():
            return Response({"error": "Email does not exist"}, status=status.HTTP_400_BAD_REQUEST)
        
        user = User.objects.get(email=email)
        if not user.check_password(password):
            return Response({"error": "Password is not valid"}, status=status.HTTP_400_BAD_REQUEST)
        
        if not user.is_active:
            return Response({"error": "User is not active"}, status=status.HTTP_400_BAD_REQUEST)
        
        userData = authenticate(email=email, password=password)
        if not userData:
            return Response({"error": "No user found with the given credentials"}, status=status.HTTP_400_BAD_REQUEST)
        
        refresh = RefreshToken.for_user(user)
        
        return Response({
            "access": str(refresh.access_token),
            "refresh": str(refresh),
            "user": UserSerializer(user).data
        })