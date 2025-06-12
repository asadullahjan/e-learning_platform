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
    """Base serializer providing shared validation logic for order creation and updates."""

    def validate(self, data):
        """Validate order data for stock availability, duplicate products, and date consistency."""
        # Extract order items and store from data
        order_items = data.get("order_items", [])
        store = data.get("store")

        # Ensure order has at least one item
        if not order_items:
            raise serializers.ValidationError(
                "Order must have at least one item",
                code="empty_order",
            )

        # Check for duplicate products in order items
        products = [item["product"] for item in order_items]
        if len(products) != len(set(products)):
            raise serializers.ValidationError(
                "Duplicate products found in order items",
                code="duplicate_products",
            )

        # Ensure store is provided if order items are included
        if order_items and not store:
            raise serializers.ValidationError(
                {
                    "store": "Store must be provided to check stock availability."
                },
                code="missing_store",
            )

        # Validate stock availability for each order item
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

        # Ensure expected delivery date is after order date
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
    """Serializer for handling order item data within orders."""

    class Meta:
        model = OrderItem
        fields = ["product", "quantity"]  # Fields to serialize


# Model Serializers
class BrandSerializer(serializers.ModelSerializer):
    """Serializer for brand data, used in nested product serialization."""

    class Meta:
        model = Brand
        fields = ["id", "name"]  # Basic brand fields


class CategorySerializer(serializers.ModelSerializer):
    """Serializer for category data, used in nested product serialization."""

    class Meta:
        model = Category
        fields = ["id", "name"]  # Basic category fields


class CustomerSerializer(serializers.ModelSerializer):
    """Serializer for customer data, used in nested order serialization."""

    class Meta:
        model = Customer
        fields = [
            "id",
            "first_name",
            "last_name",
        ]  # Customer identification fields


class ProductSerializer(serializers.ModelSerializer):
    """Serializer for product data with nested brand and category information."""

    brand = BrandSerializer(read_only=True)  # Nested brand data
    category = CategorySerializer(read_only=True)  # Nested category data

    class Meta:
        model = Product
        fields = [
            "brand",
            "category",
            "model_year",
            "name",
            "price",
        ]  # Product details


class StaffSerializer(serializers.ModelSerializer):
    """Serializer for staff data, used in nested order serialization."""

    class Meta:
        model = Staff
        fields = [
            "id",
            "first_name",
            "last_name",
        ]  # Staff identification fields


class StoreSerializer(serializers.ModelSerializer):
    """Serializer for store data, used in nested order serialization."""

    class Meta:
        model = Store
        fields = ["id", "name"]  # Store identification fields


# Order Serializers
class OrderSerializer(serializers.ModelSerializer):
    """Serializer for order data, including nested relationships and total amount."""

    # Nested serializers for related models (read-only)
    customer = CustomerSerializer(read_only=True)
    staff = StaffSerializer(read_only=True)
    store = StoreSerializer(read_only=True)
    order_status_display = serializers.CharField(
        source="get_order_status_display",
        read_only=True,
    )  # Human-readable order status
    total_amount = (
        serializers.SerializerMethodField()
    )  # Calculated total amount

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
        ]  # Order fields to serialize

    def get_total_amount(self, order):
        """Calculate the total amount for the order based on order items."""
        if hasattr(order, "total_amount"):
            return float(
                order.total_amount or 0
            )  # Use precomputed total if available
        # Aggregate total from order items (quantity * price)
        total = order.order_items.aggregate(
            total=Sum(F("quantity") * F("price"))
        )["total"]
        return float(total or 0)  # Return 0 if no items


class OrderCreateSerializer(BaseOrderSerializer):
    """Serializer for creating new orders with order items."""

    order_items = OrderItemSerializer(many=True)  # Nested order items

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
        ]  # Fields required for order creation

    def create(self, validated_data):
        """Create a new order and its associated order items within a transaction."""
        with transaction.atomic():  # Ensure atomicity for stock updates
            order_items_data = validated_data.pop(
                "order_items"
            )  # Extract order items
            order = Order.objects.create(**validated_data)  # Create order
            try:
                order.update_items(order_items_data)  # Update order items
            except ValueError as e:
                raise serializers.ValidationError(
                    str(e),
                    code="stock_error",
                )
            return order


class OrderUpdateSerializer(BaseOrderSerializer):
    """Serializer for updating existing orders with order items."""

    order_items = OrderItemSerializer(many=True)  # Nested order items

    class Meta:
        model = Order
        fields = [
            "expected_delivery_date",
            "order_date",
            "order_items",
            "order_status",
            "shipped_date",
            "staff",
        ]  # Fields allowed for update

    def validate(self, data):
        """Validate update data using the instance's store."""
        # Copy data and add instance's store for stock validation
        data = data.copy()
        data["store"] = self.instance.store
        return super().validate(data)

    def update(self, instance, validated_data):
        """Update an existing order and its order items within a transaction."""
        with transaction.atomic():  # Ensure atomicity for stock updates
            order_items_data = validated_data.pop(
                "order_items", []
            )  # Extract order items
            # Update order fields
            for attr, value in validated_data.items():
                setattr(instance, attr, value)
            instance.save()
            # Update order items if provided
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
    """Serializer for individual weekday order statistics."""

    weekday = serializers.SerializerMethodField()  # Weekday name
    weekday_number = serializers.IntegerField(
        source="weekday"
    )  # Weekday number
    total_orders = serializers.IntegerField()  # Total orders
    total_revenue = serializers.SerializerMethodField()  # Total revenue
    avg_order_value = (
        serializers.SerializerMethodField()
    )  # Average order value
    percentage_of_total = (
        serializers.SerializerMethodField()
    )  # Percentage of total orders

    def __init__(self, *args, total_orders=0, **kwargs):
        """Initialize with total orders for percentage calculation."""
        super().__init__(*args, **kwargs)
        self.total_orders = total_orders
        # Map weekday numbers to names
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
        """Convert weekday number to weekday name."""
        return self.weekday_map.get(obj["weekday"], "Unknown")

    def get_total_revenue(self, obj):
        """Return total revenue as a float."""
        return float(obj["total_revenue"] or 0)

    def get_avg_order_value(self, obj):
        """Return average order value as a float."""
        return float(obj["avg_order_value"] or 0)

    def get_percentage_of_total(self, obj):
        """Calculate percentage of total orders for the weekday."""
        orders = obj["total_orders"]
        return (
            round((orders / self.total_orders * 100), 2)
            if self.total_orders > 0
            else 0
        )


class OrderWeekdayStatsResponseSerializer(serializers.Serializer):
    """Serializer for weekday statistics response with summary data."""

    summary = serializers.SerializerMethodField()  # Summary data
    weekday_data = serializers.SerializerMethodField()  # Weekday statistics

    def __init__(
        self,
        *args,
        start_date=None,
        end_date=None,
        total_orders=0,
        total_revenue=0,
        **kwargs,
    ):
        """Initialize with summary data for response."""
        super().__init__(*args, **kwargs)
        self.start_date = start_date
        self.end_date = end_date
        self.total_orders = total_orders
        self.total_revenue = total_revenue

    def validate(self, data):
        """Ensure input data is a list of weekday statistics."""
        if not isinstance(data, list):
            raise serializers.ValidationError(
                "Data must be a list of weekday statistics."
            )
        return data

    def get_summary(self, obj):
        """Generate summary of total orders, revenue, and date range."""
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
        # Sort by total orders and weekday number (descending)
        return sorted(
            serializer.data,
            key=lambda x: (x["total_orders"], x["weekday_number"]),
            reverse=True,
        )


class TopContributingStaffStatsSerializer(serializers.Serializer):
    """Serializer for individual staff performance statistics."""

    id = serializers.IntegerField()  # Staff ID
    name = serializers.SerializerMethodField()  # Full name
    store_name = serializers.SerializerMethodField()  # Store name
    order_count = serializers.SerializerMethodField()  # Total orders
    total_revenue = serializers.SerializerMethodField()  # Total revenue
    avg_order_value = (
        serializers.SerializerMethodField()
    )  # Average order value
    total_items_sold = serializers.SerializerMethodField()  # Total items sold
    unique_customers = serializers.SerializerMethodField()  # Unique customers
    performance_score = (
        serializers.SerializerMethodField()
    )  # Performance score
    rank = serializers.IntegerField()  # Staff rank

    def get_name(self, obj):
        """Combine first and last name for display."""
        first_name = obj.get("first_name", "")
        last_name = obj.get("last_name", "")
        return f"{first_name} {last_name}".strip()

    def get_store_name(self, obj):
        """Return store name with fallback for missing data."""
        return obj.get("store__name", "Unknown Store")

    def get_order_count(self, obj):
        """Return total order count with fallback."""
        return obj.get("order_count", 0)

    def get_total_revenue(self, obj):
        """Return total revenue as a float with fallback."""
        return float(obj.get("total_revenue", 0))

    def get_avg_order_value(self, obj):
        """Return average order value as a float with fallback."""
        return float(obj.get("avg_order_value", 0))

    def get_total_items_sold(self, obj):
        """Return total items sold with fallback."""
        return obj.get("total_items_sold", 0)

    def get_unique_customers(self, obj):
        """Return count of unique customers with fallback."""
        return obj.get("unique_customers", 0)

    def get_performance_score(self, obj):
        """Return performance score as a float with fallback."""
        return float(obj.get("performance_score", 0))


class TopContributingStaffStatsResponseSerializer(serializers.Serializer):
    """Serializer for top staff statistics response with period information."""

    period_info = serializers.SerializerMethodField()  # Period details
    staff_data = serializers.SerializerMethodField()  # Staff statistics

    def __init__(
        self,
        *args,
        start_date=None,
        period="all",
        total_staff_analyzed=0,
        **kwargs,
    ):
        """Initialize with period and total staff data."""
        super().__init__(*args, **kwargs)
        self.start_date = start_date
        self.period = period
        self.total_staff_analyzed = total_staff_analyzed

    def validate(self, data):
        """Ensure input data is a list of staff statistics."""
        if not isinstance(data, list):
            raise serializers.ValidationError(
                "Data must be a list of staff statistics."
            )
        return data

    def get_period_info(self, obj):
        """Generate period information for the response."""
        return {
            "period": self.period,
            "start_date": self.start_date,
            "total_staff_analyzed": self.total_staff_analyzed,
        }

    def get_staff_data(self, obj):
        """Return ranked staff statistics."""
        # Assign ranks to staff based on index
        for idx, staff in enumerate(obj, start=1):
            staff["rank"] = idx
        return TopContributingStaffStatsSerializer(obj, many=True).data
