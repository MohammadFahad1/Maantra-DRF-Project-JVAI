from django.urls import path
from order.views import CreateOrder

urlpatterns = [
    path("create/", CreateOrder.as_view(), name="create-order"),
]