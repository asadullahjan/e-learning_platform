from django.urls import path
from .views import (
    OrderListAPIView,
    OrdersByWeekdayAPIView,
    TopContributingStaffAPIView,
    BikesByBrandAPIView,
    CreateNewOrderAPIView,
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
    path(
        "api/BikesByBrand/<int:brand_id>",
        BikesByBrandAPIView.as_view(),
        name="bikes-by-brand",
    ),
    path(
        "api/createOrder",
        CreateNewOrderAPIView.as_view(),
        name="create-order",
    ),
]
