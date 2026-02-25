import django_filters
from .models import Product

class ProductFilter(django_filters.FilterSet):
    # Explicitly define date filters to handle string-to-date conversion
    created_at__gte = django_filters.DateFilter(field_name='created_at', lookup_expr='gte')
    created_at__lte = django_filters.DateFilter(field_name='created_at', lookup_expr='lte')

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
            'category': ['exact'],
        }