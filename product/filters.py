import django_filters
from .models import Product

class ProductFilter(django_filters.FilterSet):
    sort = django_filters.OrderingFilter(
        fields=(
            ('price', 'price'),
            ('created_at', 'date'),
            ('total_sold', 'best_selling'),
        ),
    )
    
    class Meta:
        model = Product
        fields = {
            'price': ['gte', 'lte'],
            'created_at': ['gte', 'lte'],
            'category': ['exact'],
        }