from django.db import models
from django.contrib.auth.models import AbstractUser
from user.managers import CustomUserManager
# Create your models here.
class User(AbstractUser):
    username = None
    email = models.EmailField(unique=True)
    contact = models.CharField(max_length=15, blank=True, null=True)
    otp = models.CharField(max_length=6, blank=True, null=True)
    forgot_password_token = models.CharField(max_length=300, blank=True, null=True)
    
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['contact']
    
    objects = CustomUserManager()
    
    def __str__(self):
        return self.email