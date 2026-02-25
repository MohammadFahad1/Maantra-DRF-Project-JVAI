from django.db import models
from django.core.validators import MinValueValidator
from product.validators import validate_file_size
from django.contrib.auth import get_user_model

User = get_user_model()

# Create your models here.
class Category(models.Model):
    name = models.CharField(max_length=255)
    image = models.ImageField(upload_to='category_images/', validators=[validate_file_size])
    
    def __str__(self):
        return self.name
    
class Size(models.Model):
    name = models.CharField(max_length=255)
    
    def __str__(self):
        return self.name


class Product(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(1)])
    sale = models.IntegerField(default=0)
    stock = models.IntegerField(default=0)
    sizes = models.ManyToManyField(Size, related_name='products')
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='products')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return self.name
    
    def get_price(self):
        if self.sale:
            return self.price - (self.price * self.sale / 100)
        return self.price

class ProductImage(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='images')
    image = models.ImageField(upload_to='product_images/', validators=[validate_file_size])
    
class Review(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='reviews')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='reviews')
    rating = models.IntegerField()
    complaint = models.TextField()
    applied_for_refund = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)