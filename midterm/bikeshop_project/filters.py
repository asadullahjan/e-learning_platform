from django.utils import timezone
from decimal import Decimal
import django_filters
from django.db.models import Sum, F, Q
from .models import Order


class OrderFilter(django_filters.FilterSet):
    customer_id = django_filters.NumberFilter(field_name="customer")
    store_id = django_filters.NumberFilter(field_name="store")
    staff_id = django_filters.NumberFilter(field_name="staff")
    order_status = django_filters.NumberFilter()

    start_date = django_filters.DateFilter(
        field_name="order_date", lookup_expr="gte"
    )
    end_date = django_filters.DateFilter(
        field_name="order_date", lookup_expr="lte"
    )

    min_amount = django_filters.NumberFilter(method="filter_min_amount")
    max_amount = django_filters.NumberFilter(method="filter_max_amount")

    delayed_orders = django_filters.BooleanFilter(
        method="filter_delayed_orders",
        help_text=(
            "Filters orders that are delayed. "
            "Includes orders that were shipped after the expected delivery date "
            "or have not yet been shipped and are past their expected delivery date. "
            "Rejected orders are excluded."
        ),
    )

    premium_orders = django_filters.BooleanFilter(
        method="filter_premium_orders",
        help_text=(
            "Filter for high-value orders: includes orders where at least one "
            "product costs ≥ $1000 and the total order value averages ≥ $800."
        ),
    )

    class Meta:
        model = Order
        fields = []

    def filter_min_amount(self, queryset, name, value):
        return queryset.annotate(
            total_amount=Sum(
                F("order_items__quantity") * F("order_items__price")
            )
        ).filter(total_amount__gte=value)

    def filter_max_amount(self, queryset, name, value):
        return queryset.annotate(
            total_amount=Sum(
                F("order_items__quantity") * F("order_items__price")
            )
        ).filter(total_amount__lte=value)

    def filter_delayed_orders(self, queryset, name, value):
        if value:
            today = timezone.now().date()
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
                & ~Q(
                    order_status=3
                )  # exclude rejected orders (adjust the value as needed)
            )
        return queryset

    def filter_premium_orders(self, queryset, name, value):
        if value:
            queryset = queryset.annotate(
                total_amount=Sum(
                    F("order_items__price") * F("order_items__quantity")
                )
            ).filter(total_amount__gte=1000)

            total_sum = queryset.aggregate(total=Sum("total_amount"))["total"]
            count = queryset.count()
            if not total_sum or count == 0:
                return queryset.none()

            avg = Decimal(total_sum) / Decimal(count)
            return queryset.filter(total_amount__gte=avg)
        return queryset
