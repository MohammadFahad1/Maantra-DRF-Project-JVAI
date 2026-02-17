from django.urls import path
from .views import UserAuthView

urlpatterns = [
    path('register/', UserAuthView.as_view(), name='register'),
]