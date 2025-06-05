from rest_framework import serializers
from .models import (
    # Brand,
    # Category,
    Customer,
    # Product,
    Order,
    # OrderItem,
    Store,
    # Stock,
    Staff,
)


class CustomerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Customer
        fields = [
            "id",
            "first_name",
            "last_name",
        ]


class StoreSerializer(serializers.ModelSerializer):
    class Meta:
        model = Store
        fields = ["id", "name"]


class StaffSerializer(serializers.ModelSerializer):
    class Meta:
        model = Staff
        fields = ["id", "first_name", "last_name"]


class OrderSerializer(serializers.ModelSerializer):
    customer = CustomerSerializer(read_only=True)
    store = StoreSerializer(read_only=True)
    staff = StaffSerializer(read_only=True)
    order_status_display = serializers.CharField(
        source="get_order_status_display", read_only=True
    )

    class Meta:
        model = Order
        fields = [
            "id",
            "customer",
            "store",
            "staff",
            "order_status",
            "order_status_display",
            "order_date",
            "expected_delivery_date",
            "shipped_date",
        ]
