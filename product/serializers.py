from rest_framework import serializers
from product.models import Product, ProductImage, Category, Review, Variant, VariantColour
from django.db.models import Sum

class CategorySerializer(serializers.ModelSerializer):
    image = serializers.ImageField()
    class Meta:
        model = Category
        fields = ['id', 'name', 'image']

class ProductImageSerializer(serializers.ModelSerializer):
    image = serializers.ImageField()
    class Meta:
        model = ProductImage
        fields = ['id', 'image']

class ReviewCreateSerializer(serializers.Serializer):
    product_id = serializers.PrimaryKeyRelatedField(queryset=Product.objects.all())
    rating = serializers.IntegerField(max_value=5, min_value=1)
    complaint = serializers.CharField(max_length=500)

class ReviewSerializer(serializers.ModelSerializer):
    class Meta:
        model = Review
        fields = ['id', 'product', 'user', 'rating', 'complaint', 'created_at']
        extra_kwargs = {
            'created_at': {'read_only': True},
        }

class ProductVariantColourSerializer(serializers.ModelSerializer):
    class Meta:
        model = VariantColour
        fields = ['id', 'colour', 'stock']

class ProductVariantSerializer(serializers.ModelSerializer):
    colours = ProductVariantColourSerializer(many=True, read_only=True)
    class Meta:
        model = Variant
        fields = ['id', 'size', 'colours']

class ProductSerializer(serializers.ModelSerializer):
    variants = ProductVariantSerializer(many=True, read_only=True)
    images = ProductImageSerializer(many=True)
    category = CategorySerializer()
    rating = serializers.ReadOnlyField(source='avg_rating')
    class Meta:
        model = Product
        fields = ['id', 'name', 'description', 'price', 'sale', 'variants', 'category', 'images', 'rating', 'visits', 'created_at', 'updated_at']
        
        extra_kwargs = {
                'images': {'read_only': True},
                'created_at': {'read_only': True},
                'updated_at': {'read_only': True},
            }          

class ProductCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = ['id', 'name', 'description', 'price', 'sale', 'category', 'created_at', 'updated_at']
        
        extra_kwargs = {
                'created_at': {'read_only': True},
                'updated_at': {'read_only': True},
            }