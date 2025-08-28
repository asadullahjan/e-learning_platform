from rest_framework import viewsets
from rest_framework.filters import OrderingFilter
from django_filters.rest_framework import DjangoFilterBackend
from django_filters import rest_framework as filters
from drf_spectacular.utils import (
    extend_schema,
    OpenApiParameter,
)
from drf_spectacular.types import OpenApiTypes
from rest_framework.response import Response

from ..models import Status
from ..permissions.users.status_permissions import StatusPermission
from ..serializers.status_serializers import (
    StatusSerializer,
    StatusListSerializer,
    StatusCreateUpdateSerializer,
)
from ..services.status_service import StatusService


class StatusFilter(filters.FilterSet):
    """
    Filter for status updates

    Filters status updates by user, username, and content.
    """

    user = filters.NumberFilter(field_name="user__id")
    username = filters.CharFilter(
        field_name="user__username", lookup_expr="icontains"
    )
    content = filters.CharFilter(lookup_expr="icontains")

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


@extend_schema(
    tags=["Status Updates"],
    parameters=[
        OpenApiParameter(
            name="id",
            type=OpenApiTypes.INT,
            location=OpenApiParameter.PATH,
            description="Status ID",
        ),
    ],
)
class StatusViewSet(viewsets.ModelViewSet):
    """
    ViewSet for status updates

    Users can view all statuses, create their own, and edit/delete their own.

    **Actions:**
    - list: View all statuses
    - retrieve: View a specific status
    - create: Create a new status
    - update: Update an existing status
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
        elif self.action == "retrieve":
            return StatusSerializer
        else:
            return StatusListSerializer

    def perform_create(self, serializer):
        """Create status using service layer"""
        content = serializer.validated_data["content"]
        status = StatusService.create_status(self.request.user, content)
        serializer.instance = status

    def retrieve(self, request, *args, **kwargs):
        """Override retrieve to use service for permission checking"""
        status_id = kwargs.get("pk")
        instance = StatusService.get_status_with_permission_check(
            int(status_id), request.user
        )
        serializer = self.get_serializer(instance)
        return Response(serializer.data)

    def perform_update(self, serializer):
        """Update status using service layer"""
        content = serializer.validated_data["content"]
        updated_status = StatusService.update_status(
            serializer.instance, self.request.user, content
        )
        serializer.instance = updated_status

    def perform_destroy(self, instance):
        """Delete status using service layer"""
        StatusService.delete_status(instance, self.request.user)
