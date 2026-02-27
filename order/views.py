from django.shortcuts import render
from order.serializers import CartSerializer, CreateCartSerializer, AddToCartSerializer, UpdateCartItemQuantitySerializer, CartItemSerializer, ApplyCouponSerializer
from maantra.base import NewAPIView
from order.models import Cart, CartItem, Coupon
from product.models import Product, VariantColour, Variant
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

# Add Product to Cart
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
        - size \n
        - colour \n
        '''
        product_id = request.data.get('product')
        quantity = int(request.data.get('quantity', 1))
        size = int(request.data.get('size'))
        colour = int(request.data.get('colour'))
        
        if not all(['product', 'quantity', 'size', 'colour']):
            return Response({"error": "All fields are required"}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            product = Product.objects.get(id=product_id)
        except Product.DoesNotExist:
            return Response({"error": "Product not found"}, status=status.HTTP_404_NOT_FOUND)
        
        cart = Cart.objects.get_or_create(user=request.user)[0]
        variant = get_object_or_404(Variant, id=size)
        
        exists = CartItem.objects.filter(
            cart__user=request.user,
            product_id=product_id,
            product__variants__size=size,
            product__variants__colours=colour
        ).exists()
        
        if exists:
            return Response(
                {"error": "Product with this size and colour is already in your cart"}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        vc = get_object_or_404(
            VariantColour, 
            variant__product_id=product_id, 
            variant_id=size, 
            id=colour
        )
        
        if quantity > vc.stock:
            return Response({
                "error": f"Only {vc.stock} items left in stock for this color/size combination.",
                "available_stock": vc.stock
            }, status=status.HTTP_400_BAD_REQUEST)

        existing_item = CartItem.objects.filter(
            cart__user=request.user, 
            colour=vc
        ).first()
        
        total_would_be = quantity
        if existing_item:
            total_would_be += existing_item.quantity
            
        if total_would_be > vc.stock:
            return Response({
                "error": f"You already have {existing_item.quantity} in cart. Adding {quantity} more exceeds available stock."
            }, status=status.HTTP_400_BAD_REQUEST)
            
        
        cart_item, created = CartItem.objects.get_or_create(cart=cart, product=product, variant=variant, colour=vc, defaults={'quantity': quantity})
        if not created:
            cart_item.quantity += quantity
            cart_item.save()
        
        return Response({"message": "Product added to cart successfully"}, status=status.HTTP_201_CREATED)
    
# Update Cart Item Quantity
class UpdateCartItemQuantityAPIView(NewAPIView):
    serializer_class = UpdateCartItemQuantitySerializer
    permission_classes = [IsAuthenticated]
    http_method_names = ['patch']
    
    def patch(self, request):
        ''' 
        **Update Cart Item Quantity **\n
        It will update the quantity of a cart item. Only authenticated user (after logging in) can use this API. Request Type: PATCH
        
        Required Fields: \n
        - cart_item_id \n
        - quantity \n
        '''
        cart_item_id = request.data.get('cart_item_id')
        quantity = int(request.data.get('quantity'))
        cart_item = get_object_or_404(CartItem, id=cart_item_id)
        if quantity <= 0:
            return Response({"error": "Quantity must be greater than 0"}, status=status.HTTP_400_BAD_REQUEST)
        if cart_item.cart.user != request.user:
            return Response({"error": "You are not authorized to update this cart item"}, status=status.HTTP_403_FORBIDDEN)
        # if cart_item.quantity + quantity > cart_item.colour.stock:
        if quantity > cart_item.colour.stock:
            return Response({"error": f"Sorry, We don't have {quantity} stock for this color/size combination."}, status=status.HTTP_400_BAD_REQUEST)
            # return Response({"error": f"You already have {cart_item.quantity} in cart. Adding {quantity} more exceeds available stock."}, status=status.HTTP_400_BAD_REQUEST)
        # cart_item.quantity += quantity
        cart_item.quantity = quantity
        cart_item.save()
        return Response({"message": "Cart item quantity updated successfully", "data": CartItemSerializer(cart_item).data}, status=status.HTTP_200_OK)

# Delete Cart Item
class DeleteCartItem(NewAPIView):
    permission_classes = [IsAuthenticated]
    http_method_names = ['delete']
    
    def delete(self, request, cart_item_id):
        ''' 
        **Delete Cart Item **\n
        It will delete a cart item. Only authenticated user (after logging in) can use this API. Request Type: DELETE
        
        Required Fields: \n
        - cart_item_id \n
        '''
        cart_item = get_object_or_404(CartItem, id=cart_item_id)
        if cart_item.cart.user != request.user:
            return Response({"error": "You are not authorized to delete this cart item"}, status=status.HTTP_403_FORBIDDEN)
        cart_item.delete()
        return Response({"message": "Cart item deleted successfully"}, status=status.HTTP_204_NO_CONTENT)

# Apply Coupon
class ApplyCoupon(NewAPIView):
    serializer_class = ApplyCouponSerializer
    permission_classes = [IsAuthenticated]
    http_method_names = ['post', 'delete']
    
    def post(self, request):
        ''' 
        **Apply Coupon **\n
        It will apply a coupon to the user's cart. Only authenticated user (after logging in) can use this API. Request Type: POST
        
        If the coupon is applied successfully then, it will return the updated cart and the message "Coupon applied successfully" and the status code will be 200 OK.
        
        Required Fields: \n
        - coupon_code \n
        '''
        coupon = get_object_or_404(Coupon, code=request.data.get('coupon_code'))
        cart = get_object_or_404(Cart, user=request.user)
        if coupon.active == False:
            return Response({"error": "Coupon is expired"}, status=status.HTTP_400_BAD_REQUEST)
        if cart.coupon:
            return Response({"error": "You already have a coupon applied to your cart"}, status=status.HTTP_400_BAD_REQUEST)
        cart.coupon = coupon
        cart.save()
        serializer = CartSerializer(cart)
        return Response({"message": "Coupon applied successfully", "data": serializer.data}, status=status.HTTP_200_OK)
    
    def delete(self, request):
        ''' 
        **Remove Coupon **\n
        It will remove the coupon from the user's cart. Only authenticated user (after logging in) can use this API. Request Type: DELETE
        
        If the coupon is removed successfully then, it will return the updated cart and the message "Coupon removed successfully" and the status code will be 200 OK.
        '''
        cart = get_object_or_404(Cart, user=request.user)
        serializer = CartSerializer(cart)
        cart.coupon = None
        cart.save()
        return Response({"message": "Coupon removed successfully", "data": serializer.data}, status=status.HTTP_200_OK)