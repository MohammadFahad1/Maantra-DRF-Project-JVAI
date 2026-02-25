from django.urls import path, include
from product.views import ProductsAPIView, ProductDetailAPIView, ProductCreateAPIView

urlpatterns = [
    path("list/", ProductsAPIView.as_view(), name="product-list"),
    path("create/", ProductCreateAPIView.as_view(), name="product-create"),
    path("<int:pk>/", ProductDetailAPIView.as_view(), name="product-detail"),
]
