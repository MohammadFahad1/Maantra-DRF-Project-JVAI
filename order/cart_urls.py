from django.urls import path, include
from order.views import CartAPIView, CartItemAPIView

urlpatterns = [
    path("", CartAPIView.as_view(), name="cart"),
    path("add-to-cart/", CartItemAPIView.as_view(), name="add-to-cart"),
]