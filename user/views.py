from django.shortcuts import render
from .serializers import UserSerializer
from rest_framework import status
from django.contrib.auth import get_user_model
from rest_framework.generics import CreateAPIView

User = get_user_model()

# Create your views here.
class UserAuthView(CreateAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)
        
            