from django.shortcuts import render, get_object_or_404
from maantra.base import NewAPIView
from product.serializers import ProductSerializer
from rest_framework import status
from rest_framework.response import Response
from product.models import Product, ProductImage, Category, Size, Review
from django_filters.rest_framework import DjangoFilterBackend
from .filters import ProductFilter
from django.db.models import Sum

# Create your views here.
class ProductsAPIView(NewAPIView):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_class = ProductFilter
    search_fields = ['name']
    ordering_fields = ['price', 'created_at', 'total_sold']
    http_method_names = ['get', 'post']
    
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
        queryset = Product.objects.select_related('category').annotate(total_sold=Sum('order__quantity')).all()

        filterset = ProductFilter(request.GET, queryset=queryset)
        
        if filterset.is_valid():
            queryset = filterset.qs

        serializer = ProductSerializer(queryset, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
""" 
    def post(self, request):
        '''
        **Add Product or Create Product **\n
        It will add a new product. Only Admin can use this API. Request Type: POST
        
        Required Fields: \n
        - name \n
        - description \n
        - price \n
        - sale (default is 0, means no sale!)\n
        - stock \n
        - sizes \n
        - category \n
        '''
        if not self.request.user.is_staff:
            return Response({"error": "You are not authorized to add a product"}, status=status.HTTP_403_FORBIDDEN)
        serializer = ProductSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)  
"""
        



class ProductDetailAPIView(NewAPIView):
    queryset = Product.objects.prefetch_related('category', 'sizes', 'order', 'images').annotate(total_sold=Sum('order__quantity')).all()
    serializer_class = ProductSerializer
    http_method_names = ['get', 'patch', 'delete']
    
    # Get Product Details
    def get(self, request, pk):
        '''
        **Get Product Details **\n
        It will return product details.
        
        Request Type: GET
        
        Response Type: JSON
        '''
        product = get_object_or_404(self.queryset, pk=pk)
        serializer = self.serializer_class(product)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    # Delete Product
    def delete(self, request, pk):
        '''
        **Delete Product **\n
        It will delete a product. Only Admin can use this API.
        
        Request Type: DELETE
        
        Response Type: JSON with status code 204 No Content
        '''
        if not self.request.user.is_staff:
            return Response({"error": "You are not authorized to delete a product"}, status=status.HTTP_403_FORBIDDEN)
        product = get_object_or_404(self.queryset, pk=pk)
        product.delete()
        return Response({"message": "Product deleted successfully"}, status=status.HTTP_204_NO_CONTENT)

    # Update Product
    def patch(self, request, pk):
        '''
        **This API will partially update a product **\n
        It will return product details after update is complete with a status code 200. Only Admin can use this API.
        
        Request Type: PATCH
        
        Response Type: JSON with status code 200 (is successfully updated)
        '''
        if not self.request.user.is_staff:
            return Response({"error": "You are not authorized to update a product"}, status=status.HTTP_403_FORBIDDEN)
        product = get_object_or_404(self.queryset, pk=pk)
        serializer = self.serializer_class(product, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)