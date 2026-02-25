from django.urls import path, include
from product.views import ProductsAPIView, ProductDetailAPIView

urlpatterns = [
    path("", ProductsAPIView.as_view(), name="product-list"),
    path("<int:pk>/", ProductDetailAPIView.as_view(), name="product-detail"),
]
