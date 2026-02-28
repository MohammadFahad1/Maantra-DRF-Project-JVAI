from django.urls import path
from order.views import CreateOrder, CreateCheckoutSessionView, stripe_webhook, OrderListAPIView, ApplyForRefund, ShipmentStatusList

urlpatterns = [
    path("create/", CreateOrder.as_view(), name="create-order"),
    path("list/", OrderListAPIView.as_view(), name="order-list"),
    path("apply-for-refund", ApplyForRefund.as_view(), name="apply-for-refund"),
    path("shipment-status/<int:order_id>/", ShipmentStatusList.as_view(), name="shipment-status"),
    path("create-checkout-session/<int:order_id>/", CreateCheckoutSessionView.as_view(), name="create-checkout-session"),
    path("stripe/webhook/", stripe_webhook),
]