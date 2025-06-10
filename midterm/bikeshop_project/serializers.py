from datetime import date
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


class OrderItemCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = OrderItem
        fields = ["product", "quantity", "price"]


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

    def create(self, validated_data):
        items = validated_data.pop("items")
        order = Order.objects.create(**validated_data)
        for item in items:
            OrderItem.objects.create(order=order, **item)
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
        fields = ["order_date", "staff", "order_status", "order_items"]

    def validate_order_date(self, value):
        if value < date.today():
            raise serializers.ValidationError(
                "Order date cannot be in the past."
            )
        return value

    def update(self, instance, validated_data):
        order_items_data = validated_data.pop("order_items", [])

        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()

        instance.order_items.all().delete()

        total_price = 0

        for item in order_items_data:
            product = Product.objects.get(id=item["product"])
            quantity = item["quantity"]

            if product.stock < quantity:
                raise serializers.ValidationError(
                    f"Not enough stock for {product.name}. "
                    f"Available: {product.stock}"
                )

            product.stock -= quantity
            product.save()

            total_price += product.price * quantity

            OrderItem.objects.create(
                order=instance,
                product=product,
                quantity=quantity,
                price=product.price,
            )

        instance.total_price = total_price
        instance.save()

        return instance


# {
#     "staff": 1,
#     "order_status": 1,
#     "order_date": "2025-06-20",
#     "order_items": [
#         {"product": 1, "quantity": 2}
#     ]
# }
