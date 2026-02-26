from django_filters import rest_framework as filters
from product.models import Product, Category

class ProductFilter(filters.FilterSet):
    # category_id = filters.ModelChoiceFilter(
    #     queryset = Category.objects.all(),
    #     to_field_name = 'id',
    # )
    category_id = filters.NumberFilter(field_name='category_id', lookup_expr='exact')
    class Meta:
        model = Product
        fields = {
            'category_id': ['exact'],
        }