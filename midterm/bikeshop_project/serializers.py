from django.db import transaction
from django.db.models import F, Sum

from rest_framework import serializers, status

from .customError import CustomValidation
from .models import (
    Brand,
    Category,
    Customer,
    Order,
    OrderItem,
    Product,
    Staff,
    Stock,
    Store,
)


# Base Serializers
class BaseOrderSerializer(serializers.ModelSerializer):
    """Base serializer for shared order validation logic."""

    def validate(self, data):
        """Validate order data for stock, duplicates, and dates."""
        order_items = data.get("order_items", [])
        store = data.get("store")

        # Ensure at least one order item
        if not order_items:
            raise serializers.ValidationError(
                "Order must have at least one item",
                code="empty_order",
            )

        # Check for duplicate products
        products = [item["product"] for item in order_items]
        if len(products) != len(set(products)):
            raise serializers.ValidationError(
                "Duplicate products found in order items",
                code="duplicate_products",
            )

        # Check for if order items are provided without store
        if order_items and not store:
            raise serializers.ValidationError(
                {
                    "store": "Store must be provided to check stock availability."
                },
                code="missing_store",
            )

        # Validate stock availability
        if order_items and store:
            for item in order_items:
                product = item["product"]
                quantity = item["quantity"]
                try:
                    stock = Stock.objects.get(store=store, product=product)
                    if stock.quantity < quantity:
                        raise CustomValidation(
                            (
                                f"Not enough stock for {product.name}. "
                                f"Available: {stock.quantity}, Requested: {quantity}"
                            ),
                            status_code=status.HTTP_409_CONFLICT,
                        )
                except Stock.DoesNotExist:
                    raise CustomValidation(
                        f"Product {product.name} is not available in this store",
                        status_code=status.HTTP_409_CONFLICT,
                    )

        # Validate date order
        order_date = data.get("order_date")
        expected_delivery_date = data.get("expected_delivery_date")
        if expected_delivery_date and order_date:
            if expected_delivery_date < order_date:
                raise serializers.ValidationError(
                    "Expected delivery date must be after the order date",
                    code="invalid_dates",
                )

        return data


class OrderItemSerializer(serializers.ModelSerializer):
    """Serializer for order items."""

    class Meta:
        model = OrderItem
        fields = ["product", "quantity"]


# Model Serializers
class BrandSerializer(serializers.ModelSerializer):
    """Serializer for brand data."""

    class Meta:
        model = Brand
        fields = ["id", "name"]


class CategorySerializer(serializers.ModelSerializer):
    """Serializer for category data."""

    class Meta:
        model = Category
        fields = ["id", "name"]


class CustomerSerializer(serializers.ModelSerializer):
    """Serializer for customer data."""

    class Meta:
        model = Customer
        fields = ["id", "first_name", "last_name"]


class ProductSerializer(serializers.ModelSerializer):
    """Serializer for product data with nested brand and category."""

    brand = BrandSerializer(read_only=True)
    category = CategorySerializer(read_only=True)

    class Meta:
        model = Product
        fields = ["brand", "category", "model_year", "name", "price"]


class StaffSerializer(serializers.ModelSerializer):
    """Serializer for staff data."""

    class Meta:
        model = Staff
        fields = ["id", "first_name", "last_name"]


class StoreSerializer(serializers.ModelSerializer):
    """Serializer for store data."""

    class Meta:
        model = Store
        fields = ["id", "name"]


# Order Serializers
class OrderSerializer(serializers.ModelSerializer):
    """Serializer for order data with nested relationships and total amount."""

    customer = CustomerSerializer(read_only=True)
    staff = StaffSerializer(read_only=True)
    store = StoreSerializer(read_only=True)
    order_status_display = serializers.CharField(
        source="get_order_status_display",
        read_only=True,
    )
    total_amount = serializers.SerializerMethodField()

    class Meta:
        model = Order
        fields = [
            "customer",
            "expected_delivery_date",
            "id",
            "order_date",
            "order_status",
            "order_status_display",
            "shipped_date",
            "staff",
            "store",
            "total_amount",
        ]

    def get_total_amount(self, order):
        """Calculate total amount for the order."""
        if hasattr(order, "total_amount"):
            return float(order.total_amount or 0)
        total = order.order_items.aggregate(
            total=Sum(F("quantity") * F("price"))
        )["total"]
        return float(total or 0)


class OrderCreateSerializer(BaseOrderSerializer):
    """Serializer for creating new orders."""

    order_items = OrderItemSerializer(many=True)

    class Meta:
        model = Order
        fields = [
            "customer",
            "expected_delivery_date",
            "id",
            "order_date",
            "order_items",
            "order_status",
            "staff",
            "store",
        ]

    def create(self, validated_data):
        """Create a new order with order items."""
        with transaction.atomic():
            order_items_data = validated_data.pop("order_items")
            order = Order.objects.create(**validated_data)
            try:
                order.update_items(order_items_data)
            except ValueError as e:
                raise serializers.ValidationError(
                    str(e),
                    code="stock_error",
                )
            return order


class OrderUpdateSerializer(BaseOrderSerializer):
    """Serializer for updating existing orders."""

    order_items = OrderItemSerializer(many=True)

    class Meta:
        model = Order
        fields = [
            "expected_delivery_date",
            "order_date",
            "order_items",
            "order_status",
            "shipped_date",
            "staff",
        ]

    def validate(self, data):
        """Validate order update data using instance store."""
        data = data.copy()
        data["store"] = self.instance.store
        return super().validate(data)

    def update(self, instance, validated_data):
        """Update an existing order with order items."""
        with transaction.atomic():
            order_items_data = validated_data.pop("order_items", [])
            for attr, value in validated_data.items():
                setattr(instance, attr, value)
            instance.save()
            if order_items_data:
                try:
                    instance.update_items(order_items_data)
                except ValueError as e:
                    raise serializers.ValidationError(
                        str(e),
                        code="stock_error",
                    )
            return instance


# Stats Serializers
class OrderWeekdayStatsSerializer(serializers.Serializer):
    """Serializer for weekday order statistics."""

    weekday = serializers.SerializerMethodField()
    weekday_number = serializers.IntegerField(source="weekday")
    total_orders = serializers.IntegerField()
    total_revenue = serializers.SerializerMethodField()
    avg_order_value = serializers.SerializerMethodField()
    percentage_of_total = serializers.SerializerMethodField()

    def __init__(self, *args, total_orders=0, **kwargs):
        """Initialize with total orders for percentage calculation."""
        super().__init__(*args, **kwargs)
        self.total_orders = total_orders
        self.weekday_map = {
            1: "Sunday",
            2: "Monday",
            3: "Tuesday",
            4: "Wednesday",
            5: "Thursday",
            6: "Friday",
            7: "Saturday",
        }

    def get_weekday(self, obj):
        """Return weekday name from weekday number."""
        return self.weekday_map.get(obj["weekday"], "Unknown")

    def get_total_revenue(self, obj):
        """Return total revenue as float."""
        return float(obj["total_revenue"] or 0)

    def get_avg_order_value(self, obj):
        """Return average order value as float."""
        return float(obj["avg_order_value"] or 0)

    def get_percentage_of_total(self, obj):
        """Calculate percentage of total orders."""
        orders = obj["total_orders"]
        return (
            round((orders / self.total_orders * 100), 2)
            if self.total_orders > 0
            else 0
        )


class OrderWeekdayStatsResponseSerializer(serializers.Serializer):
    """Serializer for weekday stats response with summary."""

    summary = serializers.SerializerMethodField()
    weekday_data = serializers.SerializerMethodField()

    def __init__(
        self,
        *args,
        start_date=None,
        end_date=None,
        total_orders=0,
        total_revenue=0,
        **kwargs,
    ):
        """Initialize with summary data."""
        super().__init__(*args, **kwargs)
        self.start_date = start_date
        self.end_date = end_date
        self.total_orders = total_orders
        self.total_revenue = total_revenue

    def validate(self, data):
        """Ensure valid data for serialization."""
        if not isinstance(data, list):
            raise serializers.ValidationError(
                "Data must be a list of weekday statistics."
            )
        return data

    def get_summary(self, obj):
        """Return summary of total orders and revenue."""
        return {
            "total_orders": self.total_orders,
            "total_revenue": float(self.total_revenue or 0),
            "date_range": f'{self.start_date or "All time"} to {self.end_date or "Present"}',
        }

    def get_weekday_data(self, obj):
        """Return sorted weekday statistics."""
        serializer = OrderWeekdayStatsSerializer(
            obj,
            many=True,
            total_orders=self.total_orders,
        )
        return sorted(
            serializer.data,
            key=lambda x: (x["total_orders"], x["weekday_number"]),
            reverse=True,
        )


class TopContributingStaffStatsSerializer(serializers.Serializer):
    """Serializer for top contributing staff statistics."""

    id = serializers.IntegerField()
    name = serializers.SerializerMethodField()
    store_name = serializers.SerializerMethodField()
    order_count = serializers.SerializerMethodField()
    total_revenue = serializers.SerializerMethodField()
    avg_order_value = serializers.SerializerMethodField()
    total_items_sold = serializers.SerializerMethodField()
    unique_customers = serializers.SerializerMethodField()
    performance_score = serializers.SerializerMethodField()
    rank = serializers.IntegerField()

    def get_name(self, obj):
        """Return full name of staff member."""
        first_name = obj.get("first_name", "")
        last_name = obj.get("last_name", "")
        return f"{first_name} {last_name}".strip()

    def get_store_name(self, obj):
        """Return store name or default."""
        return obj.get("store__name", "Unknown Store")

    def get_order_count(self, obj):
        """Return total order count."""
        return obj.get("order_count", 0)

    def get_total_revenue(self, obj):
        """Return total revenue as float."""
        return float(obj.get("total_revenue", 0))

    def get_avg_order_value(self, obj):
        """Return average order value as float."""
        return float(obj.get("avg_order_value", 0))

    def get_total_items_sold(self, obj):
        """Return total items sold."""
        return obj.get("total_items_sold", 0)

    def get_unique_customers(self, obj):
        """Return count of unique customers."""
        return obj.get("unique_customers", 0)

    def get_performance_score(self, obj):
        """Return performance score as float."""
        return float(obj.get("performance_score", 0))


class TopContributingStaffStatsResponseSerializer(serializers.Serializer):
    """Serializer for top staff stats response with period info."""

    period_info = serializers.SerializerMethodField()
    staff_data = serializers.SerializerMethodField()

    def __init__(
        self,
        *args,
        start_date=None,
        period="all",
        total_staff_analyzed=0,
        **kwargs,
    ):
        """Initialize with period and staff data."""
        super().__init__(*args, **kwargs)
        self.start_date = start_date
        self.period = period
        self.total_staff_analyzed = total_staff_analyzed

    def validate(self, data):
        """Ensure valid data for serialization."""
        if not isinstance(data, list):
            raise serializers.ValidationError(
                "Data must be a list of staff statistics."
            )
        return data

    def get_period_info(self, obj):
        """Return period information."""
        return {
            "period": self.period,
            "start_date": self.start_date,
            "total_staff_analyzed": self.total_staff_analyzed,
        }

    def get_staff_data(self, obj):
        """Return ranked staff statistics."""
        for idx, staff in enumerate(obj, start=1):
            staff["rank"] = idx
        return TopContributingStaffStatsSerializer(obj, many=True).data
