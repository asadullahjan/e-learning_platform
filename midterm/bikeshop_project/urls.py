from django.urls import path
from .views import OrderListAPIView, OrdersByWeekdayAPIView

urlpatterns = [
    path("api/orders/", OrderListAPIView.as_view(), name="order-list"),
    path(
        "api/ordersByWeekday/",
        OrdersByWeekdayAPIView.as_view(),
        name="order-list-by-weekday",
    ),
]
