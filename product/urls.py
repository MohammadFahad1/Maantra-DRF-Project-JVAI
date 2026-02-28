from django.urls import path, include
from product.views import ProductsAPIView, ProductDetailAPIView, ProductCreateAPIView, CreateProductReview

urlpatterns = [
    path("list/", ProductsAPIView.as_view(), name="product-list"),
    path("create/", ProductCreateAPIView.as_view(), name="product-create"),
    path("<int:pk>/", ProductDetailAPIView.as_view(), name="product-detail"),
    path("create-review/", CreateProductReview.as_view(), name="create-review"),
]
