import random
import uuid
from .serializers import UserSerializer, UserLoginSerializer, ForgotPasswordSerializer, VerifyOTPSerializer, ResetPasswordSerializer
from rest_framework import status
from django.contrib.auth import get_user_model, authenticate
from maantra.base import NewAPIView
from maantra.response import error_response, s_406, s_201
from rest_framework.response import Response
from django.core.validators import validate_email
from django.core.exceptions import ValidationError
from django.core.mail import send_mail
from rest_framework_simplejwt.tokens import RefreshToken
from django.conf import settings
from django.template.loader import render_to_string
from django.utils.html import strip_tags
User = get_user_model()

def send_otp_email(email, otp):
    subject = "Reset your Maantra Password"
    from_email = settings.EMAIL_HOST_USER
    
    context = {
        "otp": otp
    }
        
    html_content = render_to_string("otp_template.html", context)
    message = strip_tags(html_content)
    
    if subject and from_email and email:
        try:
            send_mail(subject, message, from_email, [email])
            context['result'] = 'Email sent successfully'
        except Exception as e:
            context['result'] = f'Error sending email: {e}'

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

class ForgotPasswordAPIView(NewAPIView):
    serializer_class = ForgotPasswordSerializer
    def post(self, request):
        '''
        **This API is for User Forgot Password.**\n
        Enter email address to reset your password.
        
        Required Fields: \n
        - email
        '''
        serializer = ForgotPasswordSerializer(data=request.data)
        if serializer.is_valid():
            email = serializer.validated_data['email']
            try:
                user = User.objects.get(email=email)
            except User.DoesNotExist:
                return Response({"error": "User does not exist"}, status=status.HTTP_400_BAD_REQUEST)
            
            otp = str(random.randint(100000, 999999))
            # user = User.objects.get(email=email)
            user.otp = otp
            user.save()
            send_otp_email(email, otp)
            return Response({"message": "OTP sent successfully"})
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class VerifyOTPAPIView(NewAPIView):
    serializer_class = VerifyOTPSerializer
    
    def post(self, request):
        '''
        **This API is for User Verify OTP.**\n
        Enter email and otp to reset your password.
        
        Required Fields: \n
        - email \n
        - otp
        '''
        serializer = VerifyOTPSerializer(data=request.data)
        if serializer.is_valid():
            email = serializer.validated_data['email']
            otp = serializer.validated_data['otp']
            try:
                user = User.objects.get(email=email)
            except User.DoesNotExist:
                return Response({"error": "User does not exist"}, status=status.HTTP_400_BAD_REQUEST)
            
            if user.otp == otp:
                reset_token = uuid.uuid4()
                user.forgot_password_token = str(reset_token)
                user.otp = None
                user.save()
                return Response({"message": "OTP verified successfully", "reset_token": f"{reset_token}"})
            else:
                return Response({"error": "Invalid OTP"}, status=status.HTTP_400_BAD_REQUEST)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class ResetPasswordAPIView(NewAPIView):
    serializer_class = ResetPasswordSerializer
    def post(self, request):
        '''
        **This API is for User Reset Password.**\n
        Enter email, reset token and new password to reset your password.
        
        Required Fields: \n
        - email \n
        - reset_token \n
        - password \n
        - confirm_password
        '''
        serializer = ResetPasswordSerializer(data=request.data)
        if serializer.is_valid():
            email = serializer.validated_data['email']
            reset_token = serializer.validated_data['reset_token']
            password = serializer.validated_data['password']
            confirm_password = serializer.validated_data['confirm_password']
            
            try:
                user = User.objects.get(email=email, forgot_password_token=reset_token)
            except User.DoesNotExist:
                return Response({"error": "Invalid password reset token"}, status=status.HTTP_400_BAD_REQUEST)
            
            if password != confirm_password:
                return Response({"error": "Passwords do not match"}, status=status.HTTP_400_BAD_REQUEST)
            
            user.set_password(password)
            user.forgot_password_token = None
            user.save()
            return Response({"message": "Password reset successfully"})
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)