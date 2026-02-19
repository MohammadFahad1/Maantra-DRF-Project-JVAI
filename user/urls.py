from django.urls import path
from user.views import UserRegistrationAPIView, UserLoginAPIView, ForgotPasswordAPIView, VerifyOTPAPIView, ResetPasswordAPIView, GoogleLogin, FacebookLogin

urlpatterns = [
    path('register/', UserRegistrationAPIView.as_view(), name='register'),
    path('login', UserLoginAPIView.as_view(), name='login'),
    path('forgot_password', ForgotPasswordAPIView.as_view(), name='forgot_password'),
    path('verify_otp', VerifyOTPAPIView.as_view(), name='verify_otp'),
    path('reset_password', ResetPasswordAPIView.as_view(), name='reset_password'),
]