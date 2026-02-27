from django.urls import path, include
from order.views import CartAPIView, CartItemAPIView, UpdateCartItemQuantityAPIView, DeleteCartItem, ApplyCoupon

urlpatterns = [
    path("", CartAPIView.as_view(), name="cart"),
    path("add-to-cart/", CartItemAPIView.as_view(), name="add-to-cart"),
    path('update-item-quantity/', UpdateCartItemQuantityAPIView.as_view(), name='update-item-quantity'),
    path('delete-item/<int:cart_item_id>/', DeleteCartItem.as_view(), name='delete-item'),
    path('coupon/', ApplyCoupon.as_view(), name='apply-coupon'),
]