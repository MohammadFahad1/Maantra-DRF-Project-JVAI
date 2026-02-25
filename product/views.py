from django.shortcuts import render
from maantra.base import NewAPIView
from product.serializers import ProductSerializer
from rest_framework import status
from rest_framework.response import Response
from product.models import Product, ProductImage, Category, Size, Review
from django_filters.rest_framework import DjangoFilterBackend
from .filters import ProductFilter
from django.db.models import Sum

# Create your views here.
class ProductListAPIView(NewAPIView):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_class = ProductFilter
    search_fields = ['name']
    ordering_fields = ['price', 'created_at', 'total_sold']
    http_method_names = ['get']
    
    def get(self, request):
        '''
        **This API will fetch All Products **\n
        It supports searching (by product name) and filtering (by category, price, date (created_at) and best_selling (popular products)). Anyone can use this API.
        
        Query param Fields: \n
        - price__gte \n
        - price__lte \n
        - created_at__gte \n
        - created_at__lte \n
        - category \n
        - sort ('price', 'created_at', 'total_sold') \n
        '''
        queryset = Product.objects.prefetch_related('category', 'sizes', 'order', 'images').annotate(total_sold=Sum('order__quantity')).all()

        # 2. Manually apply the filter logic
        filterset = ProductFilter(request.GET, queryset=queryset)
        
        if filterset.is_valid():
            queryset = filterset.qs

        # 3. Serialize and return
        serializer = ProductSerializer(queryset, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)