from django.urls import path
from . import views
from rest_framework import permissions
from drf_yasg.views import get_schema_view
from drf_yasg import openapi

schema_view = get_schema_view(
    openapi.Info(
        title="Bikes Shop API",
        default_version="v1",
        description="API documentation for the bike shop project",
    ),
    public=True,
    permission_classes=(permissions.AllowAny,),
)

urlpatterns = [
    path(
        "",
        schema_view.with_ui("swagger", cache_timeout=0),
        name="schema-swagger-ui",
    ),
    path("api/orders/", views.OrderListAPIView.as_view(), name="order-list"),
    path(
        "api/ordersByWeekday/",
        views.OrdersByWeekdayAPIView.as_view(),
        name="order-list-by-weekday",
    ),
    path(
        "api/topContributingStaff/",
        views.TopContributingStaffAPIView.as_view(),
        name="top-contributing-staff",
    ),
    path(
        "api/BikesByBrand/<int:brand_id>",
        views.BikesByBrandAPIView.as_view(),
        name="bikes-by-brand",
    ),
    path(
        "api/createOrder",
        views.CreateNewOrderAPIView.as_view(),
        name="create-order",
    ),
    path(
        "api/updateOrder/<int:pk>/",
        views.UpdateOrderAPIView.as_view(),
        name="update-order",
    ),
]
