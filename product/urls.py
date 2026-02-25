from django.urls import path, include
from product.views import ProductListAPIView

urlpatterns = [
    path("", ProductListAPIView.as_view(), name="product-list"),
]
