from django.urls import path
from user.views import UserRegistrationAPIView, UserLoginAPIView, ForgotPasswordAPIView

urlpatterns = [
    path('register/', UserRegistrationAPIView.as_view(), name='register'),
    path('login', UserLoginAPIView.as_view(), name='login'),
    path('forgot_password', ForgotPasswordAPIView.as_view(), name='forgot_password'),
]