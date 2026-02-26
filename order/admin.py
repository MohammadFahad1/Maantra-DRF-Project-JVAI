from django.contrib import admin
from order.models import Order, OrderItem, Coupon, Cart, CartItem, OrderStatusHistory, Refund
# Register your models here.
admin.site.register(Order)
admin.site.register(OrderItem)
admin.site.register(Coupon)
admin.site.register(Cart)
admin.site.register(CartItem)
admin.site.register(OrderStatusHistory)
admin.site.register(Refund)