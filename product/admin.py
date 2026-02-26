from django.contrib import admin
from product.models import Product, ProductImage, Category, Review, Variant, VariantColour
# Register your models here.
admin.site.register(Product)
admin.site.register(ProductImage)
admin.site.register(Category)
admin.site.register(Review)
admin.site.register(Variant)
admin.site.register(VariantColour)