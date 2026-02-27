from django.urls import path, include
from user.views import UserRegistrationAPIView, UserLoginAPIView, ForgotPasswordAPIView, VerifyOTPAPIView, ResetPasswordAPIView, CreateAddress

urlpatterns = [
    path('register/', UserRegistrationAPIView.as_view(), name='register'),
    path('login', UserLoginAPIView.as_view(), name='login'),
    path('forgot_password', ForgotPasswordAPIView.as_view(), name='forgot_password'),
    path('verify_otp', VerifyOTPAPIView.as_view(), name='verify_otp'),
    path('reset_password', ResetPasswordAPIView.as_view(), name='reset_password'),
    path('auth/social/', include('djoser.social.urls')),
    path('address/', CreateAddress.as_view(), name='address'),
    ]