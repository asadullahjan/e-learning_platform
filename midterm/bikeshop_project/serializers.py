from datetime import date
from rest_framework import serializers
from django.db import transaction
from .models import (
    Brand,
    Category,
    Customer,
    OrderItem,
    Product,
    Order,
    Store,
    Stock,
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


class OrderItemCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = OrderItem
        fields = ["product", "quantity"]

        def validate(self, data):
            """Validate individual order item"""
            quantity = data.get("quantity", 0)

            if quantity <= 0:
                raise serializers.ValidationError(
                    "Quantity must be greater than 0"
                )

            # You can add more OrderItem-specific validation here
            return data

    def create(self, validated_data):
        """Create OrderItem with any specific logic"""
        return OrderItem.objects.create(**validated_data)


class OrderCreateSerializer(serializers.ModelSerializer):
    items = OrderItemCreateSerializer(many=True)

    class Meta:
        model = Order
        fields = [
            "id",
            "customer",
            "store",
            "staff",
            "order_date",
            "order_status",
            "expected_delivery_date",
            "items",
        ]

    def validate(self, data):
        """Validate the entire order"""
        items_data = data.get("items", [])
        store = data.get("store")

        if not items_data:
            raise serializers.ValidationError(
                "Order must have at least one item"
            )

        # Check for duplicate products
        products = [item["product"] for item in items_data]
        if len(products) != len(set(products)):
            raise serializers.ValidationError(
                "Duplicate products found in order items"
            )

        # Validate stock availability for each item
        for item_data in items_data:
            product = item_data["product"]
            quantity = item_data["quantity"]

            try:
                stock = Stock.objects.get(store=store, product=product)
                if stock.quantity < quantity:
                    raise serializers.ValidationError(
                        f"Not enough stock for {product.name}. "
                        f"Available: {stock.quantity}, Requested: {quantity}"
                    )
            except Stock.DoesNotExist:
                raise serializers.ValidationError(
                    f"Product {product.name} is not available in this store"
                )

        # Validate dates
        if data.get("expected_delivery_date") and data.get("order_date"):
            if data["expected_delivery_date"] < data["order_date"]:
                raise serializers.ValidationError(
                    "Expected delivery date must be after the order date"
                )

        return data

    def create(self, validated_data):
        """Create order with items using transaction"""
        with transaction.atomic():
            items_data = validated_data.pop("items")

            # Create the main order
            order = Order.objects.create(**validated_data)

            # Create order items using nested serializer
            for item_data in items_data:
                # Add order reference to item data
                item_data["order"] = order
                item_data["price"] = item_data["product"].price

                # Use nested serializer for creation
                OrderItemCreateSerializer().create(item_data)

                # Update stock quantity
                stock = Stock.objects.select_for_update().get(
                    store=order.store, product=item_data["product"]
                )
                stock.quantity -= item_data["quantity"]
                stock.save()

            return order


class BrandSerializer(serializers.ModelSerializer):
    class Meta:
        model = Brand
        fields = ["id", "name"]


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ["id", "name"]


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


class OrderItemUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = OrderItem
        fields = ["product", "quantity"]


class OrderUpdateSerializer(serializers.ModelSerializer):
    order_items = OrderItemUpdateSerializer(many=True)

    class Meta:
        model = Order
        fields = [
            "order_date",
            "expected_delivery_date",
            "shipped_date",
            "staff",
            "order_status",
            "order_items",
        ]

    def validate(self, data):
        if "expected_delivery_date" in data and "order_date" in data:
            if data["expected_delivery_date"] < data["order_date"]:
                raise serializers.ValidationError(
                    "Expected delivery date must be after the order date."
                )

        products = [item["product"] for item in data.get("order_items", [])]
        if len(products) != len(set(products)):
            raise serializers.ValidationError(
                "Duplicate products found in order items."
            )

        return data

    def update(self, instance, validated_data):
        with transaction.atomic():
            order_items_data = validated_data.pop("order_items", [])

            for attr, value in validated_data.items():
                setattr(instance, attr, value)
            instance.save()

            if order_items_data is not None:
                try:
                    instance.update_items(order_items_data)
                except ValueError as e:
                    raise serializers.ValidationError(str(e))

            return instance


# {
#     "staff": 1,
#     "order_status": 1,
#     "order_date": "2025-06-20",
#     "order_items": [
#         {"product": 1, "quantity": 2}
#     ]
# }
