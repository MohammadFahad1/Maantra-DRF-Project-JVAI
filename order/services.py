from django.db import transaction

VALID_STATUS = ['Order Placed', 'Order Confirmed', 'Order Delivered']
def update_order_status(order, new_status, updated_by=None):
    from .models import OrderStatusHistory
    
    if new_status not in VALID_STATUS:
        raise ValueError(f"Invalid status: {new_status}")
    
    with transaction.atomic():
        order.status = new_status
        order.save()
        
        OrderStatusHistory.objects.create(order=order, status=new_status, updated_by=updated_by)