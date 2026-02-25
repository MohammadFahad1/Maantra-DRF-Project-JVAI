from rest_framework import serializers
from product.models import Product, ProductImage, Category, Size, Review

class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = ['id', 'name', 'description', 'price', 'sale', 'stock', 'sizes', 'category', 'created_at', 'updated_at', 'images']
        
        extra_kwargs = {
            'created_at': {'read_only': True},
            'updated_at': {'read_only': True},
        }
