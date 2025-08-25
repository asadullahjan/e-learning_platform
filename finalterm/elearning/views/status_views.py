from rest_framework import viewsets
from rest_framework.filters import OrderingFilter
from django_filters.rest_framework import DjangoFilterBackend
from django_filters import rest_framework as filters

from ..models import Status
from ..permissions import StatusPermission
from ..serializers.status_serializers import (
    StatusSerializer,
    StatusCreateUpdateSerializer,
)


class StatusFilter(filters.FilterSet):
    """Filter for status updates"""

    # Filter by user (username or ID)
    user = filters.NumberFilter(field_name="user__id")
    username = filters.CharFilter(
        field_name="user__username", lookup_expr="icontains"
    )

    # Filter by content
    content = filters.CharFilter(lookup_expr="icontains")

    # Filter by date range
    created_after = filters.DateTimeFilter(
        field_name="created_at", lookup_expr="gte"
    )
    created_before = filters.DateTimeFilter(
        field_name="created_at", lookup_expr="lte"
    )

    class Meta:
        model = Status
        fields = [
            "user",
            "username",
            "content",
            "created_after",
            "created_before",
        ]


class StatusViewSet(viewsets.ModelViewSet):
    """
    ViewSet for status updates.
    Users can view all statuses, create their own, and edit/delete their own.
    """

    permission_classes = [StatusPermission]

    # Enable built-in filtering, search, ordering
    filter_backends = [OrderingFilter, DjangoFilterBackend]

    # Allow ordering by these fields
    ordering_fields = ["created_at", "updated_at"]
    ordering = ["-created_at"]

    # Add the custom filter
    filterset_class = StatusFilter

    def get_queryset(self):
        """Return all statuses with automatic filtering"""
        return Status.objects.select_related("user")

    def get_serializer_class(self):
        """Return appropriate serializer based on action"""
        if self.action in ["create", "update", "partial_update"]:
            return StatusCreateUpdateSerializer
        return StatusSerializer
