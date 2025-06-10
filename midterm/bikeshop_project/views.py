from datetime import datetime
from decimal import Decimal
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import generics, status
from rest_framework.pagination import PageNumberPagination
from django.shortcuts import get_object_or_404
from django.db.models import Count, F, Sum
from django.db.models.functions import ExtractWeekDay
from .models import Order, OrderItem, Staff, Product, Stock
from .serializers import (
    OrderSerializer,
    ProductSerializer,
    OrderCreateSerializer,
    OrderUpdateSerializer,
)


# Create your views here.
class OrderListAPIView(generics.ListAPIView):
    serializer_class = OrderSerializer

    def get_queryset(self):
        queryset = (
            Order.objects.select_related("customer", "store", "staff")
            .prefetch_related("order_items__product")
            .all()
        )

        customer_id = self.request.query_params.get("customer_id")
        store_id = self.request.query_params.get("store_id")
        staff_id = self.request.query_params.get("staff_id")
        start_date = self.request.query_params.get("start_date")
        end_date = self.request.query_params.get("end_date")
        order_status = self.request.query_params.get("order_status")
        min_amount = self.request.query_params.get("min_amount")
        max_amount = self.request.query_params.get("max_amount")

        try:
            if customer_id:
                queryset = queryset.filter(customer=customer_id)
            if store_id:
                queryset = queryset.filter(store=store_id)
            if staff_id:
                queryset = queryset.filter(staff=staff_id)
            if order_status:
                queryset = queryset.filter(order_status=order_status)
                # Date filtering with validation
            if start_date and end_date:
                start_date_obj = datetime.strptime(
                    start_date, "%Y-%m-%d"
                ).date()
                end_date_obj = datetime.strptime(end_date, "%Y-%m-%d").date()
                if start_date_obj > end_date_obj:
                    raise ValueError("Start date cannot be after end date")
                queryset = queryset.filter(
                    order_date__range=[start_date_obj, end_date_obj]
                )
            elif start_date:
                start_date_obj = datetime.strptime(
                    start_date, "%Y-%m-%d"
                ).date()
                queryset = queryset.filter(order_date__gte=start_date_obj)
            elif end_date:
                end_date_obj = datetime.strptime(end_date, "%Y-%m-%d").date()
                queryset = queryset.filter(order_date__lte=end_date_obj)

            # Amount filtering (calculated field)
            if min_amount:
                queryset = queryset.annotate(
                    total_amount=Sum(
                        F("order_items__quantity") * F("order_items__price")
                    )
                ).filter(total_amount__gte=Decimal(min_amount))

            if max_amount:
                if not queryset.query.annotations.get("total_amount"):
                    queryset = queryset.annotate(
                        total_amount=Sum(
                            F("order_items__quantity")
                            * F("order_items__price")
                        )
                    )
                queryset = queryset.filter(
                    total_amount__lte=Decimal(max_amount)
                )

        except (ValueError, TypeError) as e:
            self.filter_error = f"Invalid filter parameters: {e}"
            return Order.objects.none()
        return queryset.order_by("-order_date")

    def list(self, request, *args, **kwargs):
        response = super().list(request, *args, **kwargs)
        if hasattr(self, "filter_error"):
            response.data = {"error": self.filter_error, "data": response.data}
        return response


class OrdersByWeekdayAPIView(APIView):
    def get(self, request):
        data = (
            Order.objects.annotate(weekday=ExtractWeekDay("order_date"))
            .values("weekday")
            .annotate(total=Count("id"))
            .order_by("-total")
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

        for entry in data:
            entry["weekday"] = weekday_map[entry["weekday"]]

        return Response(data)


class TopContributingStaffAPIView(APIView):
    def get(self, request):
        data = (
            Staff.objects.annotate(order_count=Count("orders"))
            .values("first_name", "last_name", "order_count")
            .order_by("-order_count")
        )

        return Response(data)


class BikesByBrandAPIView(generics.ListAPIView):
    serializer_class = ProductSerializer

    def get_queryset(self):
        brand_id = self.kwargs.get("brand_id")
        data = Product.objects.all().filter(brand_id=brand_id)

        return data


class CreateNewOrderAPIView(APIView):
    """
    Create a new order with order items
    """

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
    def patch(self, request, pk):
        order = get_object_or_404(Order, pk=pk)
        serializer = OrderUpdateSerializer(
            order, data=request.data, partial=True
        )

        if serializer.is_valid():
            updated_order = serializer.save()
            return Response(OrderSerializer(updated_order).data)
        return Response(serializer.errors, status=400)
