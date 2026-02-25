from django.urls import path, include
from product.views import ProductsAPIView

urlpatterns = [
    path("", ProductsAPIView.as_view(), name="product-list"),
]
