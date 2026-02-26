from django.shortcuts import render
from order.serializers import CartSerializer, CreateCartSerializer
from maantra.base import NewAPIView
from order.models import Cart
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status

# Create or Get Cart
class CartAPIView(NewAPIView):
    serializer_class = CreateCartSerializer
    permission_classes = [IsAuthenticated]
    
    def post(self, request):
        ''' 
        ** Create or Get Cart **\n
        It will create a new cart if it doesn't exist. If a cart is already exists for the user, it will return the cart. User must have to log in before he creates a cart.
        
        - It's a POST Request.
        - If the cart is created then the status code will be 201 Created. If the cart already exists then the status code will be 200 OK.
        
        Required Fields:
        - {}
        '''
        existing_cart = Cart.objects.filter(user=request.user).first()
        if existing_cart:
            return Response(CartSerializer(existing_cart).data, status=status.HTTP_200_OK)
        
        cart = Cart.objects.create(user=request.user)
        serializer = CartSerializer(cart)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

