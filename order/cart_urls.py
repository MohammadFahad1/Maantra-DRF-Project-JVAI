from django.urls import path, include
from order.views import CartAPIView

urlpatterns = [
    path("", CartAPIView.as_view(), name="order"),
]