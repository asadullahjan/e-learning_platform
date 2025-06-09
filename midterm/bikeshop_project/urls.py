from django.urls import path
from .views import (
    OrderListAPIView,
    OrdersByWeekdayAPIView,
    TopContributingStaffAPIView,
)

urlpatterns = [
    path("api/orders/", OrderListAPIView.as_view(), name="order-list"),
    path(
        "api/ordersByWeekday/",
        OrdersByWeekdayAPIView.as_view(),
        name="order-list-by-weekday",
    ),
    path(
        "api/topContributingStaff/",
        TopContributingStaffAPIView.as_view(),
        name="top-contributing-staff",
    ),
]
