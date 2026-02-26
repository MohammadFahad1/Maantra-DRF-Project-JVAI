from rest_framework import serializers
from .models import Order, OrderItem, Coupon, Cart, CartItem, Refund
from product.models import Product
from product.serializers import ProductVariantSerializer, ProductImageSerializer

class SimpleProductSerializer(serializers.ModelSerializer):
    variants = ProductVariantSerializer(many=True, read_only=True)
    images = ProductImageSerializer(many=True)
    class Meta:
        model = Product
        fields = ['id', 'name','variants', 'images']
        
        extra_kwargs = {
                'images': {'read_only': True},
                'created_at': {'read_only': True},
                'updated_at': {'read_only': True},
            }          

class CartItemSerializer(serializers.ModelSerializer):
    product = SimpleProductSerializer(many=False, read_only=True)
    class Meta:
        model = CartItem
        fields = ['id', 'product', 'quantity']

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

class AddToCartSerializer(serializers.ModelSerializer):
    size = serializers.IntegerField()
    colour = serializers.IntegerField()
    class Meta:
        model = CartItem
        fields = ['id', 'product', 'quantity', 'size', 'colour']