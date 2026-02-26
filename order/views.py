from django.shortcuts import render
from order.serializers import CartSerializer, CreateCartSerializer, AddToCartSerializer
from maantra.base import NewAPIView
from order.models import Cart, CartItem
from product.models import Product, VariantColour
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import get_object_or_404
# Create or Get Cart
class CartAPIView(NewAPIView):
    serializer_class = CreateCartSerializer
    permission_classes = [IsAuthenticated]
    http_method_names = ['post', 'delete']
    
    def post(self, request):
        ''' 
        ** Create or Get Cart **\n
        It will create a new cart if it doesn't exist. If a cart is already exists for the user, it will return the cart. User must have to log in before he creates a cart.
        
        - It's a POST Request.
        - If the cart is created then the status code will be 201 Created. If the cart already exists then the status code will be 200 OK.
        
        Required Fields:
        - {}
        '''
        existing_cart = Cart.objects.prefetch_related('items').filter(user=request.user).first()
        if existing_cart:
            return Response(CartSerializer(existing_cart).data, status=status.HTTP_200_OK)
        
        cart = Cart.objects.create(user=request.user)
        serializer = CartSerializer(cart)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    
    def delete(self, request):
        ''' 
        **** Delete Cart ****\n
        It will delete a cart. Only Admin can use this API.
        
        - It's a DELETE Request.
        - If the cart is deleted then the status code will be 204 No Content. If the cart is not found then the status code will be 404 Not Found.
        '''
        if not request.user.is_superuser:
            return Response({"error": "You are not authorized to delete the cart"}, status=status.HTTP_403_FORBIDDEN)
        cart = Cart.objects.filter(user=request.user).first()
        if cart:
            cart.delete()
            return Response({"message": "Cart deleted successfully"}, status=status.HTTP_204_NO_CONTENT)
        return Response({"error": "Cart not found"}, status=status.HTTP_404_NOT_FOUND)

class CartItemAPIView(NewAPIView):
    serializer_class = AddToCartSerializer
    permission_classes = [IsAuthenticated]
    http_method_names = ['post']
    
    def post(self, request):
        ''' 
        **Add Product to Cart **\n
        It will add a new product to the cart. Only Admin can use this API. Request Type: POST
        
        Required Fields: \n
        - product \n
        - quantity \n
        '''
        product_id = request.data.get('product')
        quantity = request.data.get('quantity', 1)
        size = request.data.get('size')
        colour = request.data.get('colour')
        
        if not all(['product', 'quantity', 'size', 'colour']):
            return Response({"error": "All fields are required"}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            product = Product.objects.get(id=product_id)
        except Product.DoesNotExist:
            return Response({"error": "Product not found"}, status=status.HTTP_404_NOT_FOUND)
        
        try:
            cart = Cart.objects.get(user=request.user)
        except Cart.DoesNotExist:
            return Response({"error": "Cart not found"}, status=status.HTTP_404_NOT_FOUND)
        
        # if Cart.objects.prefetch_related('items').filter(user=request.user).items.filter(product_id=product_id).variants.filter(size=size).colours.filter(colour=colour).exists():
        #     return Response({"error": "Product with same size and colour already exists in cart"}, status=status.HTTP_400_BAD_REQUEST)
        # Assuming you have the IDs from the request
        exists = CartItem.objects.filter(
            cart__user=request.user,
            product_id=product_id,
            variant_colour__variant__size=size,
            variant_colour__colour=colour
        ).exists()
        
        
        if exists:
            return Response(
                {"error": "Product with this size and colour is already in your cart"}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        vc = get_object_or_404(
            VariantColour, 
            variant__product_id=product_id, 
            variant__size=size, 
            colour=colour
        )
        
        # 3. STOCK CHECK
        if quantity > vc.stock:
            return Response({
                "error": f"Only {vc.stock} items left in stock for this color/size combination.",
                "available_stock": vc.stock
            }, status=status.HTTP_400_BAD_REQUEST)

        # 4. (Optional) Check existing cart quantity
        # If they already have 2 in cart and are adding 3, check if 5 > stock
        existing_item = CartItem.objects.filter(
            cart__user=request.user, 
            variant_colour=vc
        ).first()
        
        total_would_be = quantity
        if existing_item:
            total_would_be += existing_item.quantity
            
        if total_would_be > vc.stock:
            return Response({
                "error": f"You already have {existing_item.quantity} in cart. Adding {quantity} more exceeds available stock."
            }, status=status.HTTP_400_BAD_REQUEST)
            
        
        cart_item, created = CartItem.objects.get_or_create(cart=cart, product=product)
        if not created:
            cart_item.quantity += quantity
            cart_item.save()
        
        return Response({"message": "Product added to cart successfully"}, status=status.HTTP_201_CREATED)