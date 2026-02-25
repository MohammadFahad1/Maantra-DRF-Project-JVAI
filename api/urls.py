from django.urls import path, include
from .views import intro
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)

urlpatterns = [
    path('auth/', include('rest_framework.urls')),
    path('token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path("user/", include("user.urls"), name="user"),
    path("products/", include("product.urls"), name="product"),
    path("", intro, name="intro"),
]
