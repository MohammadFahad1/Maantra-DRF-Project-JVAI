from rest_framework import serializers
from .models import Order, OrderItem, Coupon, Cart, CartItem, Refund

class CartItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = CartItem
        fields = ['id', 'cart', 'product', 'quantity']

class CartSerializer(serializers.ModelSerializer):
    items = CartItemSerializer(many=True, read_only=True)
    class Meta:
        model = Cart
        fields = ['id', 'user', 'items']
        
        extra_kwargs = {
            'user': {'read_only': True},
        }

class CreateCartSerializer(serializers.ModelSerializer):
    class Meta:
        model = Cart
        fields = ['id', 'user']
        extra_kwargs = {
            'user': {'read_only': True},
        }