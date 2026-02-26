from django.urls import path, include
from .views import intro
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)


from rest_framework import permissions
from drf_yasg.views import get_schema_view
from drf_yasg import openapi

schema_view = get_schema_view(
   openapi.Info(
        title="Maantra API",
        default_version='v1',
        description="Base URL: http://127.0.0.1:8000/api/v1/",
        terms_of_service="https://www.google.com/policies/terms/",
        contact=openapi.Contact(email="contact@snippets.local"),
        license=openapi.License(name="BSD License"),
   ),
   public=True,
   permission_classes=(permissions.AllowAny,),
)

urlpatterns = [
    path('auth/', include('rest_framework.urls')),
    path('token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path("user/", include("user.urls"), name="user"),
    path("products/", include("product.urls"), name="product"),
    path("categories/", include("product.category_urls"), name="category"),
    path("cart/", include("order.cart_urls"), name="cart"),
    path('swagger/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    path('redoc/', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),
]
