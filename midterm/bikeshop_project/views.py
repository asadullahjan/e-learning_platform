from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import generics

from django.db.models import Count
from django.db.models.functions import ExtractWeekDay
from .models import Order
from .serializers import OrderSerializer


# Create your views here.
class OrderListAPIView(generics.ListAPIView):
    serializer_class = OrderSerializer

    def get_queryset(self):
        queryset = Order.objects.all()

        customer_id = self.request.query_params.get("customer_id")
        store_id = self.request.query_params.get("store_id")
        staff_id = self.request.query_params.get("staff_id")
        start_date = self.request.query_params.get("start_date")
        end_date = self.request.query_params.get("end_date")

        if customer_id:
            queryset = queryset.filter(customer=customer_id)
        if store_id:
            queryset = queryset.filter(store=store_id)
        if staff_id:
            queryset = queryset.filter(staff=staff_id)
        if start_date and end_date:
            queryset = queryset.filter(
                order_date__range=[start_date, end_date]
            )
        elif start_date:
            queryset = queryset.filter(order_date__gte=start_date)
        elif end_date:
            queryset = queryset.filter(order_date__lte=end_date)

        return queryset


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
