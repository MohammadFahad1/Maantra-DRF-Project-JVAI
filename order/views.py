from django.shortcuts import render
from order.serializers import CartSerializer, CreateCartSerializer, AddToCartSerializer, UpdateCartItemQuantitySerializer, CartItemSerializer, ApplyCouponSerializer, PaymentSerializer, CreateOrderSerializer, OrderSerializer, CreateCheckoutSessionSerializer
from maantra.base import NewAPIView
from order.models import Cart, CartItem, Coupon, Payment, Order, OrderItem, OrderStatusHistory
from user.models import Address
from product.models import Product, VariantColour, Variant
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import get_object_or_404
import stripe
from django.conf import settings
from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponse

stripe.api_key = settings.STRIPE_SECRET_KEY


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

class CreateOrder(NewAPIView):
    serializer_class = CreateOrderSerializer
    permission_classes = [IsAuthenticated]
    http_method_names = ['post']
    
    def post(self, request):
        ''' 
        **Create Order **\n
        It will create an order for the user. Only authenticated user (after logging in) can use this API. Request Type: POST
        
        If the order is created successfully then, it will return the order and the message "Order created successfully" and the status code will be 200 OK.
        '''
        from django.db import transaction
        with transaction.atomic():
            cart = get_object_or_404(Cart, user=request.user)
            if not cart.items.exists():
                return Response({"error": "Your cart is empty"}, status=status.HTTP_400_BAD_REQUEST)
            shipping_address = Address.objects.get(id=request.data.get('shipping_address_id'))
            coupon = cart.coupon
            order_status = "Order Placed"
            total_price = CartSerializer(cart).get_total_price(cart)
            
            order = Order.objects.create(user=request.user, status=order_status, total_price=total_price, coupon=coupon, shipping_address=shipping_address)
            OrderStatusHistory.objects.create(order=order, status=order_status)
            
            for item in cart.items.all():
                OrderItem.objects.create(order=order, product=item.product, price=item.product.get_price(), variant=item.variant, colour=item.colour, quantity=item.quantity, subtotal=item.subtotal())
                item.colour.stock -= item.quantity
                item.colour.save()
            cart.delete()
            
            serializer = OrderSerializer(order)
            return Response({"message": "Order created successfully", "data": serializer.data}, status=status.HTTP_201_CREATED)

class CreateCheckoutSessionView(NewAPIView):
    serializer_class = CreateCheckoutSessionSerializer
    permission_classes = [IsAuthenticated]

    def post(self, request, order_id):
        ''' 
        ** Make Payment Using Stripe to Create Checkout Session **\n
        It will create a checkout session for the user. Only authenticated user (after logging in) can use this API. Request Type: POST
        
        If the checkout session is created successfully then, it will return the checkout url and the status code will be 200 OK.
        
        Required Fields: \n
        - order_id
        '''
        order = get_object_or_404(Order, id=order_id)

        if order.status != "Order Placed":
            return Response({"error": "Order already processed"}, status=400)

        session = stripe.checkout.Session.create(
            payment_method_types=["card"],
            line_items=[
                {
                    "price_data": {
                        "currency": "usd",
                        "product_data": {
                            "name": f"Order #{order.id}- {order.user.email} - {order.status}",
                        },
                        "unit_amount": int(order.total_price * 100),
                    },
                    "quantity": 1,
                }
            ],
            mode="payment",
            success_url="http://localhost:3000/success",
            cancel_url="http://localhost:3000/cancel",
            metadata={
                "order_id": order.id
            }
        )

        return Response({"checkout_url": session.url})

@csrf_exempt
def stripe_webhook(request):
    payload = request.body
    sig_header = request.META.get("HTTP_STRIPE_SIGNATURE")

    try:
        event = stripe.Webhook.construct_event(
            payload,
            sig_header,
            settings.STRIPE_WEBHOOK_SECRET
        )
    except Exception:
        return HttpResponse(status=400)

    if event["type"] == "checkout.session.completed":
        session = event["data"]["object"]
        order_id = session["metadata"]["order_id"]

        from .models import Order, Payment, OrderStatusHistory
        from django.db import transaction
        
        with transaction.atomic():
            order = Order.objects.get(id=order_id)
            order.status = 'Order Confirmed'
            order.save() 

            Payment.objects.create(
                order=order, 
                amount=order.total_price, 
                currency='USD', 
                payment_id=session["payment_intent"]
            )
            
            OrderStatusHistory.objects.create(order=order, status='Order Confirmed')

    return HttpResponse(status=200)

# Order List API View
class OrderListAPIView(NewAPIView):
    serializer_class = OrderSerializer
    permission_classes = [IsAuthenticated]
    http_method_names = ['get']
    
    def get(self, request):
        ''' 
        **Get Order List **\n
        It will get the list of orders for the user. Only authenticated user (after logging in) can use this API. Request Type: GET
        
        If the order list is fetched successfully then, it will return the order list and the status code will be 200 OK.
        '''
        orders = Order.objects.filter(user=request.user)
        serializer = OrderSerializer(orders, many=True)
        return Response({"message": "Order list fetched successfully", "data": serializer.data}, status=status.HTTP_200_OK)


""" 
# Make review API View
class MakeReviewAPIView(NewAPIView):
    serializer_class = ReviewSerializer
    permission_classes = [IsAuthenticated]
    http_method_names = ['post']
    
    def post(self, request):
        ''' 
        **Make Review **\n
        It will make a review for the product. Only authenticated user (after logging in) can use this API. Request Type: POST
        
        If the review is made successfully then, it will return the review and the status code will be 201 Created.
        '''
        product = get_object_or_404(Product, id=request.data.get('product_id'))
        review = Review.objects.create(user=request.user, product=product, rating=request.data.get('rating'), comment=request.data.get('comment'))
        serializer = ReviewSerializer(review)
        return Response({"message": "Review made successfully", "data": serializer.data}, status=status.HTTP_201_CREATED)
"""