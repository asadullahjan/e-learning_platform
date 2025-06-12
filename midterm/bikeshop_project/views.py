    import logging
    from datetime import date, timedelta
    from decimal import Decimal

    from django.db.models import Avg, Case, Count, F, FloatField, Sum, Value, When
    from django.db.models.functions import ExtractWeekDay
    from django.shortcuts import get_object_or_404

    from django_filters.rest_framework import DjangoFilterBackend
    from drf_yasg import openapi
    from drf_yasg.utils import swagger_auto_schema
    from rest_framework import generics, status
    from rest_framework.response import Response
    from rest_framework.views import APIView

    from .filters import OrderFilter
    from .models import Order, Product, Staff
    from .customError import CustomValidation
    from .serializers import (
        OrderCreateSerializer,
        OrderSerializer,
        OrderUpdateSerializer,
        OrderWeekdayStatsResponseSerializer,
        ProductSerializer,
        TopContributingStaffStatsResponseSerializer,
    )

    # Initialize logger for error tracking
    logger = logging.getLogger(__name__)


    class OrdersListAPIView(generics.ListAPIView):
        """List orders with filtering and pagination support."""

        serializer_class = OrderSerializer
        filterset_class = OrderFilter
        filter_backends = [DjangoFilterBackend]

        @swagger_auto_schema(
            operation_description="Retrieve a paginated list of orders with filtering.",
            manual_parameters=[
                openapi.Parameter(
                    "customer_id",
                    openapi.IN_QUERY,
                    type=openapi.TYPE_INTEGER,
                    description="Filter by customer ID.",
                ),
                openapi.Parameter(
                    "store_id",
                    openapi.IN_QUERY,
                    type=openapi.TYPE_INTEGER,
                    description="Filter by store ID.",
                ),
                openapi.Parameter(
                    "staff_id",
                    openapi.IN_QUERY,
                    type=openapi.TYPE_INTEGER,
                    description="Filter by staff ID.",
                ),
                openapi.Parameter(
                    "start_date",
                    openapi.IN_QUERY,
                    type=openapi.TYPE_STRING,
                    format="date",
                    description="Filter orders from this date.",
                ),
                openapi.Parameter(
                    "end_date",
                    openapi.IN_QUERY,
                    type=openapi.TYPE_STRING,
                    format="date",
                    description="Filter orders until this date.",
                ),
                openapi.Parameter(
                    "order_status",
                    openapi.IN_QUERY,
                    type=openapi.TYPE_INTEGER,
                    enum=[1, 2, 3, 4],
                    description="Order status: 1=Pending, 2=Processing, 3=Rejected, 4=Completed",
                ),
                openapi.Parameter(
                    "min_amount",
                    openapi.IN_QUERY,
                    type=openapi.TYPE_NUMBER,
                    description="Minimum order amount.",
                ),
                openapi.Parameter(
                    "max_amount",
                    openapi.IN_QUERY,
                    type=openapi.TYPE_NUMBER,
                    description="Maximum order amount.",
                ),
                openapi.Parameter(
                    "delayed_orders",
                    openapi.IN_QUERY,
                    type=openapi.TYPE_BOOLEAN,
                    description="Show only delayed orders.",
                ),
                openapi.Parameter(
                    "premium_orders",
                    openapi.IN_QUERY,
                    type=openapi.TYPE_BOOLEAN,
                    description="Show only premium orders.",
                ),
            ],
        )
        def get(self, request, *args, **kwargs):
            """Handle GET request to fetch filtered orders."""
            return self.list(request, *args, **kwargs)

        def get_queryset(self):
            """Build optimized queryset with related data for orders."""
            # Use select_related for foreign keys and prefetch_related for many-to-many
            # to reduce database queries when accessing customer, store, staff, and order items
            return (
                Order.objects.select_related("customer", "store", "staff")
                .prefetch_related("order_items__product")
                .order_by("-order_date")  # Sort by most recent orders
            )

        def list(self, request, *args, **kwargs):
            """Customize response to include filter errors if validation fails."""
            # Get paginated response from parent class
            response = super().list(request, *args, **kwargs)
            # Add filter error to response if present, preserving original data structure
            if hasattr(self, "filter_error"):
                response.data = {"error": self.filter_error, "data": response.data}
            return response


    class OrdersWeekdayAnalysisAPIView(APIView):
        """Analyze order statistics by weekday with revenue metrics."""

        @swagger_auto_schema(
            operation_description="Retrieve order statistics by weekday with revenue and performance metrics.",
            manual_parameters=[
                openapi.Parameter(
                    "customer_id",
                    openapi.IN_QUERY,
                    type=openapi.TYPE_INTEGER,
                    description="Filter by customer ID.",
                ),
                openapi.Parameter(
                    "store_id",
                    openapi.IN_QUERY,
                    type=openapi.TYPE_INTEGER,
                    description="Filter by store ID.",
                ),
                openapi.Parameter(
                    "staff_id",
                    openapi.IN_QUERY,
                    type=openapi.TYPE_INTEGER,
                    description="Filter by staff ID.",
                ),
                openapi.Parameter(
                    "start_date",
                    openapi.IN_QUERY,
                    type=openapi.TYPE_STRING,
                    format="date",
                    description="Filter orders from this date.",
                ),
                openapi.Parameter(
                    "end_date",
                    openapi.IN_QUERY,
                    type=openapi.TYPE_STRING,
                    format="date",
                    description="Filter orders until this date.",
                ),
                openapi.Parameter(
                    "order_status",
                    openapi.IN_QUERY,
                    type=openapi.TYPE_INTEGER,
                    enum=[1, 2, 3, 4],
                    description="Order status: 1=Pending, 2=Processing, 3=Rejected, 4=Completed",
                ),
                openapi.Parameter(
                    "min_amount",
                    openapi.IN_QUERY,
                    type=openapi.TYPE_NUMBER,
                    description="Minimum order amount.",
                ),
                openapi.Parameter(
                    "max_amount",
                    openapi.IN_QUERY,
                    type=openapi.TYPE_NUMBER,
                    description="Maximum order amount.",
                ),
                openapi.Parameter(
                    "delayed_orders",
                    openapi.IN_QUERY,
                    type=openapi.TYPE_BOOLEAN,
                    description="Show only delayed orders.",
                ),
                openapi.Parameter(
                    "premium_orders",
                    openapi.IN_QUERY,
                    type=openapi.TYPE_BOOLEAN,
                    description="Show only premium orders.",
                ),
            ],
            responses={
                200: openapi.Response(
                    description="Weekday statistics with enhanced metrics.",
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
                                },
                            ],
                        },
                    },
                ),
                400: openapi.Response(
                    description="Bad Request - Invalid date format"
                ),
            },
        )
        def get(self, request):
            """Handle GET request to compute weekday order statistics."""

            # Validate and apply filters
            filtered_queryset = self._validate_filters(request)

            try:
                # Aggregate data by weekday
                weekday_data = self._aggregate_weekday_metrics(filtered_queryset)
                # Compute summary totals
                total_orders, total_revenue = self._compute_summary(weekday_data)
                # Serialize and return response
                return self._build_response(
                    weekday_data,
                    request.query_params.get("start_date"),
                    request.query_params.get("end_date"),
                    total_orders,
                    total_revenue,
                )
            except Exception as e:
                return Response(
                    {"error": f"An error occurred: {str(e)}"},
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR,
                )

        def _validate_filters(self, request):
            """Validate filter parameters and return filtered queryset."""
            # Apply OrderFilter to validate query parameters
            order_filter = OrderFilter(
                request.query_params, queryset=Order.objects.all()
            )
            if not order_filter.is_valid():
                # Return 400 response with validation errors
                raise CustomValidation(
                    detail=order_filter.errors,
                    field="filters",
                    status_code=status.HTTP_400_BAD_REQUEST,
                )
            return order_filter.qs

        def _aggregate_weekday_metrics(self, queryset):
            """Aggregate order metrics by weekday."""
            # Extract weekday and compute metrics: total orders, revenue, avg order value
            return (
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

        def _compute_summary(self, weekday_data):
            """Calculate total orders and revenue for summary."""
            # Sum orders and revenue, handling null values
            total_orders = sum(day["total_orders"] for day in weekday_data)
            total_revenue = sum(day["total_revenue"] or 0 for day in weekday_data)
            return total_orders, total_revenue

        def _build_response(
            self, weekday_data, start_date, end_date, total_orders, total_revenue
        ):
            """Serialize weekday data with summary information."""
            serializer = OrderWeekdayStatsResponseSerializer(
                weekday_data,
                start_date=start_date,
                end_date=end_date,
                total_orders=total_orders,
                total_revenue=total_revenue,
            )
            return Response(serializer.data, status=status.HTTP_200_OK)


    class StaffTopContributorsAPIView(APIView):
        """Rank top-performing staff based on order metrics."""

        @swagger_auto_schema(
            operation_description="Retrieve top contributing staff with performance metrics.",
            manual_parameters=[
                openapi.Parameter(
                    "limit",
                    openapi.IN_QUERY,
                    type=openapi.TYPE_INTEGER,
                    default=10,
                    description="Number of top staff to return (1-50).",
                ),
                openapi.Parameter(
                    "period",
                    openapi.IN_QUERY,
                    type=openapi.TYPE_STRING,
                    enum=["week", "month", "quarter", "year", "all"],
                    default="month",
                    description="Time period for analysis.",
                ),
                openapi.Parameter(
                    "min_orders",
                    openapi.IN_QUERY,
                    type=openapi.TYPE_INTEGER,
                    default=1,
                    description="Minimum orders to be included.",
                ),
            ],
            responses={
                200: openapi.Response(
                    description="Top contributing staff with enhanced metrics.",
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
                                },
                            ],
                        },
                    },
                ),
                400: openapi.Response(
                    description="Bad Request - Invalid parameters"
                ),
            },
        )
        def get(self, request):
            """Handle GET request to fetch top staff performance data."""
            try:
                # Validate query parameters
                limit, period, min_orders = self._validate_params(request)
                # Calculate date range for the period
                start_date = self._get_period_start_date(period)
                # Fetch staff performance data
                staff_data = self._fetch_staff_metrics(
                    start_date, min_orders, limit
                )
                # Serialize and return response
                return self._build_staff_response(staff_data, period, start_date)
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

        def _validate_params(self, request):
            """Validate limit, period, and minimum orders parameters."""
            try:
                limit = min(int(request.query_params.get("limit", 10)), 50)
                period = request.query_params.get("period", "month")
                min_orders = int(request.query_params.get("min_orders", 1))
                if limit < 1:
                    raise ValueError("Limit must be at least 1")
                return limit, period, min_orders
            except ValueError as e:
                raise ValueError(f"Invalid parameter: {str(e)}")

        def _get_period_start_date(self, period):
            """Calculate start date based on the selected time period."""
            period_map = {
                "week": 7,
                "month": 30,
                "quarter": 90,
                "year": 365,
                "all": 365 * 10,
            }
            if period not in period_map:
                raise ValueError(
                    "Invalid period. Use: week, month, quarter, year, or all"
                )
            return date.today() - timedelta(days=period_map[period])

        def _fetch_staff_metrics(self, start_date, min_orders, limit):
            """Fetch staff metrics with performance score calculation."""
            # Query active staff with orders in the period
            staff_data = (
                Staff.objects.filter(
                    active=True, orders__order_date__gte=start_date
                )
                .select_related("store")  # Optimize store foreign key lookup
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
                    # Calculate performance score: revenue/100 + 2*order_count
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
                .filter(order_count__gte=min_orders)  # Apply minimum orders filter
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
                .order_by("-performance_score")[:limit]  # Limit results
            )
            return staff_data

        def _build_staff_response(self, staff_data, period, start_date):
            """Serialize staff data with period information."""
            serializer = TopContributingStaffStatsResponseSerializer(
                staff_data,
                period=period,
                start_date=start_date.isoformat(),
                total_staff_analyzed=len(staff_data),
            )
            return Response(serializer.data, status=status.HTTP_200_OK)


    class BikesByBrandAPIView(generics.ListAPIView):
        """List bikes filtered by brand with additional query parameters."""

        serializer_class = ProductSerializer

        @swagger_auto_schema(
            operation_description="Retrieve bikes by brand with filtering options.",
            manual_parameters=[
                openapi.Parameter(
                    "min_price",
                    openapi.IN_QUERY,
                    type=openapi.TYPE_NUMBER,
                    description="Minimum price filter.",
                ),
                openapi.Parameter(
                    "max_price",
                    openapi.IN_QUERY,
                    type=openapi.TYPE_NUMBER,
                    description="Maximum price filter.",
                ),
                openapi.Parameter(
                    "category_id",
                    openapi.IN_QUERY,
                    type=openapi.TYPE_INTEGER,
                    description="Filter by category ID.",
                ),
                openapi.Parameter(
                    "model_year",
                    openapi.IN_QUERY,
                    type=openapi.TYPE_STRING,
                    description="Filter by model year.",
                ),
                openapi.Parameter(
                    "in_stock",
                    openapi.IN_QUERY,
                    type=openapi.TYPE_BOOLEAN,
                    description="Filter for in-stock items.",
                ),
            ],
        )
        def get(self, request, *args, **kwargs):
            """Handle GET request to fetch bikes by brand."""
            return super().get(request, *args, **kwargs)

        def get_queryset(self):
            """Build queryset for bikes filtered by brand and query parameters."""
            # Get brand ID from URL
            brand_id = self.kwargs.get("brand_id")
            # Start with base queryset, optimizing with select_related
            queryset = Product.objects.select_related("brand", "category").filter(
                brand_id=brand_id
            )

            # Apply additional filters
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
                # Return empty queryset for invalid filters
                return Product.objects.none()

            return queryset


    class OrderCreateAPIView(APIView):
        """Create a new order with associated order items."""

        @swagger_auto_schema(
            operation_description="Create a new order with order items.",
            request_body=OrderCreateSerializer,
            responses={
                201: OrderSerializer,
                400: "Bad Request - Validation errors",
                409: "Conflict - Insufficient stock",
            },
        )
        def post(self, request):
            """Handle POST request to create a new order."""
            # Validate request data with serializer
            serializer = OrderCreateSerializer(data=request.data)
            if serializer.is_valid(raise_exception=True):
                try:
                    # Save the validated order
                    order = serializer.save()
                    # Serialize created order for response
                    response_serializer = OrderSerializer(order)
                    return Response(
                        {
                            "message": "Order created successfully",
                            "order": response_serializer.data,
                        },
                        status=status.HTTP_201_CREATED,
                    )
                except Exception as e:
                    return Response(
                        {"error": f"Failed to create order: {str(e)}"},
                        status=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    )


    class OrderUpdateAPIView(APIView):
        """Update an existing order with partial changes."""

        @swagger_auto_schema(
            operation_description="Update an existing order.",
            request_body=OrderUpdateSerializer,
            responses={
                200: OrderSerializer,
                400: "Bad Request - Validation errors",
                404: "Order not found",
                409: "Conflict - Insufficient stock",
            },
        )
        def patch(self, request, pk):
            """Handle PATCH request to update an existing order."""
            # Fetch order or return 404 if not found
            order = get_object_or_404(Order, pk=pk)
            # Validate partial update data
            serializer = OrderUpdateSerializer(
                order, data=request.data, partial=True
            )
            if serializer.is_valid(raise_exception=True):
                # Save updated order
                updated_order = serializer.save()
                # Return serialized updated order
                return Response(
                    OrderSerializer(updated_order).data, status=status.HTTP_200_OK
                )
