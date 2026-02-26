from django.db import models
from django.contrib.auth import get_user_model
from django.core.validators import MinValueValidator, MaxValueValidator
from product.models import Product, Size
User = get_user_model()

# Create your models here.
class Coupon(models.Model):
    code = models.CharField(max_length=10)
    discount_percentage = models.IntegerField(validators=[MinValueValidator(1), MaxValueValidator(100)], blank=True, null=True)
    discount_amount = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(1)], blank=True, null=True)
    active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

class Cart(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='cart')
    created_at = models.DateTimeField(auto_now_add=True)
    
class CartItem(models.Model):
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='cart')
    quantity = models.PositiveIntegerField(default=1, validators=[MinValueValidator(1)])
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        unique_together = [['cart', 'product']]
    
    def __str__(self):
        return f'{self.quantity} x {self.product.name} in {self.cart.user.email} cart'
    
    def subtotal(self):
        return self.product.get_price() * self.quantity

class Order(models.Model): 
    ORDER_PLACED = 'Order Placed'
    ORDER_CONFIRMED = 'Order Confirmed'
    ORDER_DELIVERED = 'Order Delivered'
    STATUS_CHOICES = [
        (ORDER_PLACED, 'Order Placed'),
        (ORDER_CONFIRMED, 'Order Confirmed'),
        (ORDER_DELIVERED, 'Order Delivered'),
    ]
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='orders')
    status = models.CharField(max_length=30, choices=STATUS_CHOICES, default=ORDER_PLACED)
    total_price = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(1)])
    coupon = models.OneToOneField(Coupon, on_delete=models.SET_NULL, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self, *args, **kwds):
        return f"Order #{self.id} - {self.user.email} - {self.status}"

class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, on_delete = models.CASCADE, related_name='order')
    size = models.ForeignKey(Size, on_delete=models.CASCADE)
    price = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(1)])
    quantity = models.PositiveIntegerField(default=1, validators=[MinValueValidator(1)])
    subtotal = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(1)])
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        unique_together = [['order', 'product', 'size']]
    
    def __str__(self):
        return f'{self.quantity} x {self.product.name} in Order #{self.order.id}'

class OrderStatusHistory(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='status_history')
    status = models.CharField(max_length=30)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ["created_at"]

class Refund(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='refunds')
    reason = models.TextField()
    amount = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(1)])
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)