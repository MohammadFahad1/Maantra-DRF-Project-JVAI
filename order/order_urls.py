from django.urls import path
from order.views import CreateOrder, CreateCheckoutSessionView, stripe_webhook, OrderListAPIView

urlpatterns = [
    path("create/", CreateOrder.as_view(), name="create-order"),
    path("list/", OrderListAPIView.as_view(), name="order-list"),
    path("create-checkout-session/<int:order_id>/", CreateCheckoutSessionView.as_view(), name="create-checkout-session"),
    path("stripe/webhook/", stripe_webhook),
]