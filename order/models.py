from django.db import models
from django.contrib.auth import get_user_model
from django.core.validators import MinValueValidator, MaxValueValidator
from product.models import Product, Variant, VariantColour
from user.models import Address
from product.validators import validate_file_size
User = get_user_model()

# Create your models here.
class Coupon(models.Model):
    code = models.CharField(max_length=10)
    discount_percentage = models.IntegerField(validators=[MinValueValidator(1), MaxValueValidator(100)], blank=True, null=True)
    discount_amount = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(1)], blank=True, null=True)
    active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.code} - " + (f"{self.discount_percentage}% Off" if self.discount_percentage else f"${self.discount_amount} Off")

class Cart(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='cart')
    coupon = models.OneToOneField(Coupon, on_delete=models.SET_NULL, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"Cart of {self.user.first_name} - {self.user.email}"
    
class CartItem(models.Model):
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='cart')
    variant = models.ForeignKey(Variant, on_delete=models.CASCADE, related_name='cartitem')
    colour = models.ForeignKey(VariantColour, on_delete=models.CASCADE, related_name='cartitem')
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
    coupon = models.ForeignKey(Coupon, on_delete=models.SET_NULL, related_name='orders', blank=True, null=True)
    shipping_address = models.ForeignKey(Address, on_delete=models.SET_NULL, related_name='orders', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self, *args, **kwds):
        return f"Order #{self.id} - {self.user.email} - {self.status}"

class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, on_delete = models.CASCADE, related_name='order')
    price = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(1)])
    variant = models.ForeignKey(Variant, on_delete=models.CASCADE, related_name='orderitem')
    colour = models.ForeignKey(VariantColour, on_delete=models.CASCADE, related_name='orderitem')
    quantity = models.PositiveIntegerField(default=1, validators=[MinValueValidator(1)])
    subtotal = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(1)])
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        unique_together = [['order', 'product']]
    
    def __str__(self):
        return f'{self.quantity} x {self.product.name} in Order #{self.order.id}'

class OrderStatusHistory(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='status_history')
    status = models.CharField(max_length=30)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ["created_at"]
        
    unique_together = [['order', 'status']]
    
    def __str__(self):
        return f"Order #{self.order.id} - {self.status}"

class Payment(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='payment')
    amount = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(1)])
    currency = models.CharField(max_length=3, default='USD')
    payment_id = models.CharField(max_length=100, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

class Refund(models.Model):
    order = models.OneToOneField(Order, on_delete=models.CASCADE, related_name='refund')
    reason = models.TextField()
    attachment = models.FileField(upload_to='refunds/', validators=[validate_file_size])
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)