from rest_framework import generics
from .models import Order
from .serializers import OrderSerializer


# Create your views here.
class OrderListAPIView(generics.ListAPIView):
    serializer_class = OrderSerializer

    def get_queryset(self):
        queryset = Order.objects.all()

        customer_id = self.request.query_params.get("customer_id")
        store_id = self.request.query_params.get("store_id")
        start_date = self.request.query_params.get("start_date")
        end_date = self.request.query_params.get("end_date")

        if customer_id:
            queryset = queryset.filter(customer=customer_id)
        if store_id:
            queryset = queryset.filter(store=store_id)

        if start_date and end_date:
            queryset = queryset.filter(
                order_date__range=[start_date, end_date]
            )
        elif start_date:
            queryset = queryset.filter(order_date__gte=start_date)
        elif end_date:
            queryset = queryset.filter(order_date__lte=end_date)

        return queryset
