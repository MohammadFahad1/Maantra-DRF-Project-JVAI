from django.shortcuts import render, get_object_or_404
from maantra.base import NewAPIView
from product.serializers import ProductSerializer, ProductCreateSerializer, CategorySerializer
from rest_framework import status
from rest_framework.response import Response
from product.models import Product, ProductImage, Category, Review
from django_filters.rest_framework import DjangoFilterBackend
from .filters import ProductFilter
from django.db.models import Sum, Avg
from rest_framework.filters import SearchFilter, OrderingFilter
from django.db.models.functions import Coalesce
from product.paginations import ProductListPagination
from rest_framework.pagination import PageNumberPagination

# Category List
class CategoryListAPIView(NewAPIView):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    http_method_names = ['get', 'post']
    
    def get(self, request):
        '''
        **Get all Categories **\n
        It will return all categories.
        
        Note: It's public API anyone can use this API.
        '''
        queryset = Category.objects.all()
        serializer = CategorySerializer(queryset, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    def post(self, request):
        '''
        **Add Category or Create Category **\n
        It will add a new category. Only Admin can use this API. Request Type: POST
        
        Required Fields: \n
        - name \n
        - image \n
        '''
        if not self.request.user.is_staff:
            return Response({"error": "You are not authorized to add a category"}, status=status.HTTP_403_FORBIDDEN)
        serializer = CategorySerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

# Category Detail, Update and Delete
class CategoryDetailAPIView(NewAPIView):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    http_method_names = ['get', 'patch', 'delete']
    
    def get(self, request, pk):
        '''
        **Get Category Details **\n
        It will return category details.
        
        Request Type: GET
        
        Response Type: JSON
        '''
        category = get_object_or_404(self.queryset, pk=pk)
        serializer = self.serializer_class(category)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    def patch(self, request, pk):
        '''
        **This API will partially update a category **\n
        It will return category details after update is complete with a status code 200. Only Admin can use this API.
        
        Request Type: PATCH
        
        Response Type: JSON with status code 200 (is successfully updated)
        '''
        if not self.request.user.is_staff:
            return Response({"error": "You are not authorized to update a category"}, status=status.HTTP_403_FORBIDDEN)
        category = get_object_or_404(self.queryset, pk=pk)
        serializer = self.serializer_class(category, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    def delete(self, request, pk):
        '''
        **Delete Category **\n
        It will delete a category. Only Admin can use this API.
        
        Request Type: DELETE
        
        Response Type: JSON with status code 204 No Content
        '''
        if not self.request.user.is_staff:
            return Response({"error": "You are not authorized to delete a category"}, status=status.HTTP_403_FORBIDDEN)
        category = get_object_or_404(self.queryset, pk=pk)
        category.delete()
        return Response({"message": "Category deleted successfully"}, status=status.HTTP_204_NO_CONTENT)



# Product List
class ProductsAPIView(NewAPIView):
    queryset = Product.objects.select_related('category') \
            .prefetch_related('variants', 'images') \
            .annotate(
                total_sold=Coalesce(Sum('order__quantity'), 0), 
                avg_rating=Coalesce(Avg('reviews__rating'), 0)
            )
    serializer_class = ProductSerializer
    filter_backends = [DjangoFilterBackend, OrderingFilter, SearchFilter]
    filterset_class = ProductFilter
    search_fields = ['name']
    ordering_fields = ['price', 'created_at', 'total_sold']
    ordering = ['-created_at']
    pagination_class = ProductListPagination
    http_method_names = ['get']
    
    def get(self, request):
        '''
        **This API will fetch All Products **\n
        It supports searching (by product name) and filtering (by category, price, date (created_at) and best_selling (popular products)). Anyone can use this API.
        
        Query param Fields: \n
        - category_id (Enter the category id and it will display the products of that category) \n
        - sort ('price', 'created_at', 'total_sold') # For descending order use '-' as prefix \n
        '''
        query = request.GET.get('ordering', '-created_at')
        queryset = Product.objects.select_related('category') \
            .prefetch_related('variants', 'images') \
            .annotate(
                total_sold=Sum('order__quantity'), 
                avg_rating=Avg('reviews__rating')
            ).order_by(query)
            
        # 2. Apply Filters (The loop we discussed earlier)
        for backend in list(self.filter_backends):
            queryset = backend().filter_queryset(request, queryset, self)

        # 3. PAGINATION LOGIC
        paginator = PageNumberPagination()
        paginator.page_size = 6 # You can set this dynamically or in settings
        
        # This actually slices the queryset (LIMIT/OFFSET)
        page = paginator.paginate_queryset(queryset, request)
        
        if page is not None:
            serializer = ProductSerializer(page, many=True)
            # This helper method returns the 'count', 'next', 'previous' JSON structure
            return paginator.get_paginated_response(serializer.data)
            
        serializer = ProductSerializer(queryset, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

# Product Create
class ProductCreateAPIView(NewAPIView):
    serializer_class = ProductCreateSerializer
    http_method_names = ['post']
    
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
        serializer = ProductCreateSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)  

# Product Detail, Update and Delete
class ProductDetailAPIView(NewAPIView):
    queryset = Product.objects.select_related('category').prefetch_related('sizes', 'order', 'images', 'reviews').annotate(total_sold=Sum('order__quantity')).all()
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