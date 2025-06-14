from decimal import Decimal
from django.utils import timezone
from django.db.models import F, Q, Sum
import django_filters
from .models import Order


class OrderFilter(django_filters.FilterSet):
    """Filter for querying orders based on customer, store, dates, and other criteria."""

    # Filter by customer ID (exact match)
    customer_id = django_filters.NumberFilter(
        field_name="customer",
        help_text="Filter orders by customer ID.",
    )

    # Filter by store ID (exact match)
    store_id = django_filters.NumberFilter(
        field_name="store",
        help_text="Filter orders by store ID.",
    )

    # Filter by staff ID (exact match)
    staff_id = django_filters.NumberFilter(
        field_name="staff",
        help_text="Filter orders by staff ID.",
    )

    # Filter by order status (exact match)
    order_status = django_filters.NumberFilter(
        help_text="Filter orders by status (e.g., 1=Pending, 2=Processing, 3=Rejected, 4=Completed).",
    )

    # Filter orders on or after the start date
    start_date = django_filters.DateFilter(
        field_name="order_date",
        lookup_expr="gte",
        help_text="Filter orders placed on or after this date (YYYY-MM-DD).",
    )

    # Filter orders on or before the end date
    end_date = django_filters.DateFilter(
        field_name="order_date",
        lookup_expr="lte",
        help_text="Filter orders placed on or before this date (YYYY-MM-DD).",
    )

    # Filter orders with total amount >= specified value
    min_amount = django_filters.NumberFilter(
        method="filter_min_amount",
        help_text="Filter orders with total amount (quantity × price) greater than or equal to this value.",
    )

    # Filter orders with total amount <= specified value
    max_amount = django_filters.NumberFilter(
        method="filter_max_amount",
        help_text="Filter orders with total amount (quantity × price) less than or equal to this value.",
    )

    # Filter delayed orders (shipped late or unshipped past due date)
    delayed_orders = django_filters.BooleanFilter(
        method="filter_delayed_orders",
        help_text=(
            "Filters orders that are delayed. "
            "Includes orders that were shipped after the expected delivery date "
            "or have not yet been shipped and are past their expected delivery date. "
            "Rejected orders are excluded."
        ),
    )

    # Filter premium orders (high-value with specific criteria)
    premium_orders = django_filters.BooleanFilter(
        method="filter_premium_orders",
        help_text=(
            "Filter for high-value orders: includes orders where at least one "
            "product costs ≥ $1000 and the total order value averages ≥ $800."
        ),
    )

    class Meta:
        model = Order
        fields = []  # No default fields; all filters are explicitly defined

    def filter_min_amount(self, queryset, name, value):
        """Filter orders with total amount greater than or equal to the specified value."""
        # Annotate queryset with total amount (quantity * price)
        return queryset.annotate(
            total_amount=Sum(
                F("order_items__quantity") * F("order_items__price")
            )
        ).filter(total_amount__gte=value)

    def filter_max_amount(self, queryset, name, value):
        """Filter orders with total amount less than or equal to the specified value."""
        # Annotate queryset with total amount (quantity * price)
        return queryset.annotate(
            total_amount=Sum(
                F("order_items__quantity") * F("order_items__price")
            )
        ).filter(total_amount__lte=value)

    def filter_delayed_orders(self, queryset, name, value):
        """Filter delayed orders, excluding rejected orders, if value is True."""
        if value:
            today = timezone.now().date()
            # Include orders that are:
            # 1. Shipped after expected delivery date, or
            # 2. Not shipped and past expected delivery date
            # Exclude rejected orders (order_status=3)
            return queryset.filter(
                (
                    Q(
                        shipped_date__isnull=False,
                        shipped_date__gt=F("expected_delivery_date"),
                    )
                    | Q(
                        shipped_date__isnull=True,
                        expected_delivery_date__lt=today,
                    )
                )
                & ~Q(order_status=3)  # Exclude rejected orders
            )
        return queryset  # Return unfiltered queryset if value is False

    def filter_premium_orders(self, queryset, name, value):
        """Filter high-value orders with specific criteria if value is True."""
        if value:
            # Annotate queryset with total amount
            queryset = queryset.annotate(
                total_amount=Sum(
                    F("order_items__price") * F("order_items__quantity")
                )
            ).filter(total_amount__gte=1000)

            # Calculate average total amount
            total_sum = queryset.aggregate(total=Sum("total_amount"))["total"]
            count = queryset.count()
            if not total_sum or count == 0:
                return queryset.none()  # Return empty queryset if no orders

            # Filter orders above average total amount
            avg = Decimal(total_sum) / Decimal(count)
            return queryset.filter(total_amount__gte=avg)
        return queryset  # Return unfiltered queryset if value is False
