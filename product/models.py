from django.db import models
from django.core.validators import MinValueValidator

# Create your models here.
class Size(models.Model):
    name = models.CharField(max_length=255)
class Product(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(1)])
    sale = models.IntegerField(default=0)
    stock = models.IntegerField(default=0)
    sizes = models.CharField(max_length=255, choices=Size, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return self.name
    
    def get_main_price(self):
        return self.price
    
    def get_sale_price(self):
        return self.price - ((self.price / 100) * self.sale)

class ProductImage(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='images')
    image = models.ImageField(upload_to='product_images/')