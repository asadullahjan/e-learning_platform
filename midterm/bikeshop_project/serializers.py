from rest_framework import serializers
from .models import (
    Brand,
    Category,
    Customer,
    OrderItem,
    Product,
    Order,
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


class OrderItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = OrderItem
        fields = ["product", "quantity", "price"]


class OrderCreateSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True)

    class Meta:
        model = Order
        fields = [
            "customer",
            "store",
            "staff",
            "order_date",
            "order_status",
            "expected_delivery_date",
            "items",
        ]

    def create(self, validated_data):
        items = validated_data.pop("items")
        order = Order.objects.create(**validated_data)
        for item in items:
            OrderItem.objects.create(order=order, **item)
        return order


class BrandSerializer(serializers.ModelSerializer):
    class Meta:
        model = Brand
        fields = ["name"]


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ["name"]


class ProductSerializer(serializers.ModelSerializer):
    brand = BrandSerializer(read_only=True)
    category = CategorySerializer(read_only=True)

    class Meta:
        model = Product
        fields = [
            "name",
            "model_year",
            "price",
            "brand",
            "category",
        ]
