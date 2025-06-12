from django.urls import path

from rest_framework import permissions
from drf_yasg.views import get_schema_view
from drf_yasg import openapi

from . import views

schema_view = get_schema_view(
    openapi.Info(
        title="Bike Shop API",
        default_version="v1",
        description="API for managing orders, products, and staff in the bike shop project",
        contact=openapi.Contact(email="support@bikeshop.example.com"),
        license=openapi.License(name="MIT License"),
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
    path(
        "api/orders/",
        views.OrdersListAPIView.as_view(),
        name="order-list",
    ),
    path(
        "api/orders/by-weekday/",
        views.OrdersWeekdayAnalysisAPIView.as_view(),
        name="order-list-by-weekday",
    ),
    path(
        "api/staff/top-contributors/",
        views.StaffTopContributorsAPIView.as_view(),
        name="top-contributing-staff",
    ),
    path(
        "api/bikes/brand/<int:brand_id>/",
        views.BikesByBrandAPIView.as_view(),
        name="bikes-by-brand",
    ),
    path(
        "api/orders/create/",
        views.OrderCreateAPIView.as_view(),
        name="create-order",
    ),
    path(
        "api/orders/update/<int:pk>/",
        views.OrderUpdateAPIView.as_view(),
        name="update-order",
    ),
]
