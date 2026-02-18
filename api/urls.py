from django.urls import path, include
from .views import intro
# from rest_framework_nested import routers
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)
from user.views import UserRegistrationAPIView

# router = routers.DefaultRouter()
# router.register('user', UserAuthView, basename='user')

# router.register('user', UserViewSet, basename='user')

urlpatterns = [
    path('auth/', include('rest_framework.urls')),
    path('token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    # path('', include(router.urls)),
    path("user/", UserRegistrationAPIView.as_view(), name="user"),
    path("", intro, name="intro"),
]
