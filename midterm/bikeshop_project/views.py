from datetime import date, datetime, timedelta
from decimal import Decimal
import logging

from .constants import ORDER_STATUS
from .filters import OrderFilter
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import generics, status
from rest_framework.pagination import PageNumberPagination
from django.shortcuts import get_object_or_404
from django.db.models import Count, F, Sum, Case, Avg, When, Value, FloatField
from django.db.models.functions import ExtractWeekDay
from .models import Order, OrderItem, Staff, Product, Stock
from .serializers import (
    OrderSerializer,
    ProductSerializer,
    OrderCreateSerializer,
    OrderUpdateSerializer,
)
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from django_filters.rest_framework import DjangoFilterBackend

logger = logging.getLogger(__name__)


# Create your views here.
class OrderListAPIView(generics.ListAPIView):
    serializer_class = OrderSerializer
    filterset_class = OrderFilter
    filter_backends = [DjangoFilterBackend]

    @swagger_auto_schema(
        operation_description="Get paginated list of orders with filtering",
        manual_parameters=[
            openapi.Parameter(
                "customer_id", openapi.IN_QUERY, type=openapi.TYPE_INTEGER
            ),
            openapi.Parameter(
                "store_id", openapi.IN_QUERY, type=openapi.TYPE_INTEGER
            ),
            openapi.Parameter(
                "staff_id", openapi.IN_QUERY, type=openapi.TYPE_INTEGER
            ),
            openapi.Parameter(
                "start_date",
                openapi.IN_QUERY,
                type=openapi.TYPE_STRING,
                format="date",
            ),
            openapi.Parameter(
                "end_date",
                openapi.IN_QUERY,
                type=openapi.TYPE_STRING,
                format="date",
            ),
            openapi.Parameter(
                "order_status",
                openapi.IN_QUERY,
                type=openapi.TYPE_INTEGER,
                enum=[1, 2, 3, 4],
                description="Order status: 1=Pending, 2=Processing, 3=Shipped, 4=Rejected",
            ),
            openapi.Parameter(
                "min_amount", openapi.IN_QUERY, type=openapi.TYPE_NUMBER
            ),
            openapi.Parameter(
                "max_amount", openapi.IN_QUERY, type=openapi.TYPE_NUMBER
            ),
            openapi.Parameter(
                "delayed_orders", openapi.IN_QUERY, type=openapi.TYPE_BOOLEAN
            ),
            openapi.Parameter(
                "premium_orders", openapi.IN_QUERY, type=openapi.TYPE_BOOLEAN
            ),
        ],
    )
    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)

    def get_queryset(self):
        queryset = (
            Order.objects.select_related("customer", "store", "staff")
            .prefetch_related("order_items__product")
            .all()
        )

        return queryset.order_by("-order_date")

    def list(self, request, *args, **kwargs):
        response = super().list(request, *args, **kwargs)
        if hasattr(self, "filter_error"):
            response.data = {"error": self.filter_error, "data": response.data}
        return response


class OrdersByWeekdayAPIView(APIView):
    """
    IMPROVED: Added error handling, better response structure, more metrics
    """

    @swagger_auto_schema(
        operation_description="Get comprehensive order statistics by weekday with revenue and performance metrics",
        manual_parameters=[
            openapi.Parameter(
                "start_date",
                openapi.IN_QUERY,
                type=openapi.TYPE_STRING,
                format="date",
                description="Start date for analysis (YYYY-MM-DD)",
            ),
            openapi.Parameter(
                "end_date",
                openapi.IN_QUERY,
                type=openapi.TYPE_STRING,
                format="date",
                description="End date for analysis (YYYY-MM-DD)",
            ),
        ],
        responses={
            200: openapi.Response(
                "Weekday statistics with enhanced metrics",
                examples={
                    "application/json": {
                        "summary": {
                            "total_orders": 150,
                            "total_revenue": 45000.00,
                            "date_range": "2024-01-01 to 2024-12-31",
                        },
                        "weekday_data": [
                            {
                                "weekday": "Monday",
                                "weekday_number": 2,
                                "total_orders": 25,
                                "total_revenue": 7500.00,
                                "avg_order_value": 300.00,
                                "percentage_of_total": 16.67,
                            }
                        ],
                    }
                },
            ),
            400: openapi.Response("Bad Request - Invalid date format"),
        },
    )
    def get(self, request):
        try:
            # Parse date parameters with validation
            start_date = request.query_params.get("start_date")
            end_date = request.query_params.get("end_date")

            queryset = Order.objects.all()

            if start_date:
                try:
                    start_date_obj = date.fromisoformat(start_date)
                    queryset = queryset.filter(order_date__gte=start_date_obj)
                except ValueError:
                    return Response(
                        {"error": "Invalid start_date format. Use YYYY-MM-DD"},
                        status=status.HTTP_400_BAD_REQUEST,
                    )

            if end_date:
                try:
                    end_date_obj = date.fromisoformat(end_date)
                    queryset = queryset.filter(order_date__lte=end_date_obj)
                except ValueError:
                    return Response(
                        {"error": "Invalid end_date format. Use YYYY-MM-DD"},
                        status=status.HTTP_400_BAD_REQUEST,
                    )

            # Enhanced query with more metrics
            weekday_data = (
                queryset.annotate(weekday=ExtractWeekDay("order_date"))
                .values("weekday")
                .annotate(
                    total_orders=Count("id"),
                    total_revenue=Sum(
                        F("order_items__quantity") * F("order_items__price")
                    ),
                    avg_order_value=Avg(
                        F("order_items__quantity") * F("order_items__price")
                    ),
                    order_count_with_items=Count("order_items", distinct=True),
                )
                .order_by("weekday")
            )

            # Calculate totals for percentage calculations
            total_orders = sum(day["total_orders"] for day in weekday_data)
            total_revenue = sum(
                day["total_revenue"] or 0 for day in weekday_data
            )

            weekday_map = {
                1: "Sunday",
                2: "Monday",
                3: "Tuesday",
                4: "Wednesday",
                5: "Thursday",
                6: "Friday",
                7: "Saturday",
            }

            # Process data with enhanced metrics
            processed_data = []
            for entry in weekday_data:
                revenue = float(entry["total_revenue"] or 0)
                orders = entry["total_orders"]

                processed_data.append(
                    {
                        "weekday": weekday_map[entry["weekday"]],
                        "weekday_number": entry["weekday"],
                        "total_orders": orders,
                        "total_revenue": revenue,
                        "avg_order_value": float(
                            entry["avg_order_value"] or 0
                        ),
                        "percentage_of_total": (
                            round((orders / total_orders * 100), 2)
                            if total_orders > 0
                            else 0
                        ),
                    }
                )

            # Sort by total orders descending for better insights
            processed_data.sort(key=lambda x: x["total_orders"], reverse=True)

            response_data = {
                "summary": {
                    "total_orders": total_orders,
                    "total_revenue": total_revenue,
                    "date_range": f"{start_date or 'All time'} to {end_date or 'Present'}",
                },
                "weekday_data": processed_data,
            }

            return Response(response_data, status=status.HTTP_200_OK)

        except Exception as e:
            return Response(
                {"error": f"An error occurred: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )


class TopContributingStaffAPIView(APIView):
    """
    IMPROVED: Better period handling, more metrics, error handling
    """

    @swagger_auto_schema(
        operation_description="Get top contributing staff with comprehensive performance metrics",
        manual_parameters=[
            openapi.Parameter(
                "limit",
                openapi.IN_QUERY,
                type=openapi.TYPE_INTEGER,
                default=10,
                description="Number of top staff to return (1-50)",
            ),
            openapi.Parameter(
                "period",
                openapi.IN_QUERY,
                type=openapi.TYPE_STRING,
                enum=["week", "month", "quarter", "year", "all"],
                default="month",
                description="Time period for analysis",
            ),
            openapi.Parameter(
                "min_orders",
                openapi.IN_QUERY,
                type=openapi.TYPE_INTEGER,
                default=1,
                description="Minimum orders to be included",
            ),
        ],
        responses={
            200: openapi.Response(
                "Top Contributing Staff with enhanced metrics",
                examples={
                    "application/json": {
                        "period_info": {
                            "period": "month",
                            "start_date": "2024-05-11",
                            "total_staff_analyzed": 15,
                        },
                        "staff_data": [
                            {
                                "id": 1,
                                "name": "John Doe",
                                "store_name": "Downtown Store",
                                "order_count": 45,
                                "total_revenue": 15750.00,
                                "avg_order_value": 350.00,
                                "performance_score": 95.5,
                                "rank": 1,
                            }
                        ],
                    }
                },
            ),
            400: openapi.Response("Bad Request - Invalid parameters"),
        },
    )
    def get(self, request):
        try:
            # Validate parameters
            limit = min(
                int(request.query_params.get("limit", 10)), 50
            )  # Cap at 50
            period = request.query_params.get("period", "month")
            min_orders = int(request.query_params.get("min_orders", 1))

            if limit < 1:
                return Response(
                    {"error": "Limit must be at least 1"},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            # Calculate date range
            today = date.today()
            period_map = {
                "week": 7,
                "month": 30,
                "quarter": 90,
                "year": 365,
                "all": 365 * 10,  # 10 years for "all"
            }

            if period not in period_map:
                return Response(
                    {
                        "error": "Invalid period. Use: week, month, quarter, year, or all"
                    },
                    status=status.HTTP_400_BAD_REQUEST,
                )

            start_date = today - timedelta(days=period_map[period])

            # Enhanced query with more comprehensive metrics
            staff_data = (
                Staff.objects.filter(
                    active=True,  # Only active staff
                    orders__order_date__gte=start_date,
                )
                .select_related("store")  # Optimize query
                .annotate(
                    order_count=Count("orders", distinct=True),
                    total_revenue=Sum(
                        F("orders__order_items__quantity")
                        * F("orders__order_items__price")
                    ),
                    avg_order_value=Avg(
                        F("orders__order_items__quantity")
                        * F("orders__order_items__price")
                    ),
                    total_items_sold=Sum("orders__order_items__quantity"),
                    unique_customers=Count("orders__customer", distinct=True),
                    # Performance score calculation
                    performance_score=Case(
                        When(
                            order_count__gt=0,
                            then=(F("total_revenue") / Value(100))
                            + (F("order_count") * Value(2)),
                        ),
                        default=Value(0),
                        output_field=FloatField(),
                    ),
                )
                .filter(
                    order_count__gte=min_orders
                )  # Filter by minimum orders
                .values(
                    "id",
                    "first_name",
                    "last_name",
                    "store__name",
                    "order_count",
                    "total_revenue",
                    "avg_order_value",
                    "total_items_sold",
                    "unique_customers",
                    "performance_score",
                )
                .order_by("-performance_score")[:limit]
            )

            # Process and rank results
            result = []
            for rank, staff in enumerate(staff_data, 1):
                result.append(
                    {
                        "id": staff["id"],
                        "name": f"{staff['first_name']} {staff['last_name']}",
                        "store_name": staff["store__name"] or "Unknown Store",
                        "order_count": staff["order_count"],
                        "total_revenue": float(staff["total_revenue"] or 0),
                        "avg_order_value": float(
                            staff["avg_order_value"] or 0
                        ),
                        "total_items_sold": staff["total_items_sold"] or 0,
                        "unique_customers": staff["unique_customers"] or 0,
                        "performance_score": float(
                            staff["performance_score"] or 0
                        ),
                        "rank": rank,
                    }
                )

            response_data = {
                "period_info": {
                    "period": period,
                    "start_date": start_date.isoformat(),
                    "total_staff_analyzed": len(result),
                },
                "staff_data": result,
            }

            return Response(response_data, status=status.HTTP_200_OK)

        except ValueError as e:
            return Response(
                {"error": f"Invalid parameter value: {str(e)}"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        except Exception as e:
            return Response(
                {"error": f"An error occurred: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )


class BikesByBrandAPIView(generics.ListAPIView):
    serializer_class = ProductSerializer

    def get_queryset(self):
        brand_id = self.kwargs.get("brand_id")
        queryset = Product.objects.select_related("brand", "category").filter(
            brand_id=brand_id
        )

        # Additional filtering options
        min_price = self.request.query_params.get("min_price")
        max_price = self.request.query_params.get("max_price")
        category_id = self.request.query_params.get("category_id")
        model_year = self.request.query_params.get("model_year")
        in_stock = self.request.query_params.get("in_stock")

        try:
            if min_price:
                queryset = queryset.filter(price__gte=Decimal(min_price))
            if max_price:
                queryset = queryset.filter(price__lte=Decimal(max_price))
            if category_id:
                queryset = queryset.filter(category_id=category_id)
            if model_year:
                queryset = queryset.filter(model_year=model_year)
            if in_stock == "true":
                queryset = queryset.filter(stock__quantity__gt=0).distinct()
        except (ValueError, TypeError) as e:
            logger.error(
                f"Invalid filter parameters in BikesByBrandAPIView: {e}"
            )
            return Product.objects.none()

        return queryset

    @swagger_auto_schema(
        operation_description="Get bikes by brand with filtering options",
        manual_parameters=[
            openapi.Parameter(
                "min_price", openapi.IN_QUERY, type=openapi.TYPE_NUMBER
            ),
            openapi.Parameter(
                "max_price", openapi.IN_QUERY, type=openapi.TYPE_NUMBER
            ),
            openapi.Parameter(
                "category_id", openapi.IN_QUERY, type=openapi.TYPE_INTEGER
            ),
            openapi.Parameter(
                "model_year", openapi.IN_QUERY, type=openapi.TYPE_STRING
            ),
            openapi.Parameter(
                "in_stock", openapi.IN_QUERY, type=openapi.TYPE_BOOLEAN
            ),
        ],
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)


class CreateNewOrderAPIView(APIView):
    """
    Create a new order with order items
    """

    @swagger_auto_schema(
        operation_description="Create a new order",
        request_body=OrderCreateSerializer,
        responses={
            201: OrderSerializer,
            400: "Bad Request - Validation errors",
            409: "Conflict - Insufficient stock",
        },
    )
    def post(self, request):
        """Handle POST request to create new order"""
        serializer = OrderCreateSerializer(data=request.data)

        if serializer.is_valid():
            try:
                # Create order (this calls serializer.create())
                order = serializer.save()

                # Return created order data
                response_serializer = OrderSerializer(order)
                return Response(
                    {
                        "message": "Order created successfully",
                        "order": response_serializer.data,
                    },
                    status=status.HTTP_201_CREATED,
                )

            except Exception as e:
                # Handle any unexpected errors during creation
                return Response(
                    {"error": f"Failed to create order: {str(e)}"},
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR,
                )

        # Return validation errors
        return Response(
            {"error": "Validation failed", "details": serializer.errors},
            status=status.HTTP_400_BAD_REQUEST,
        )


class UpdateOrderAPIView(APIView):
    @swagger_auto_schema(
        operation_description="Update an existing order",
        request_body=OrderUpdateSerializer,
        responses={
            200: OrderSerializer,
            400: "Bad Request - Validation errors",
            404: "Order not found",
            409: "Conflict - Insufficient stock",
        },
    )
    def patch(self, request, pk):
        order = get_object_or_404(Order, pk=pk)
        serializer = OrderUpdateSerializer(
            order, data=request.data, partial=True
        )

        if serializer.is_valid():
            updated_order = serializer.save()
            return Response(OrderSerializer(updated_order).data)
        return Response(serializer.errors, status=400)
