from django.contrib import admin
from product.models import Product, ProductImage, Category, Size, Review
# Register your models here.
admin.site.register(Product)
admin.site.register(ProductImage)
admin.site.register(Category)
admin.site.register(Size)
admin.site.register(Review)