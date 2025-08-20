from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from ..models import User
from ..serializers.user_serializers import UserSerializer


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def get_user_by_username(request, username):
    """Get user profile by username"""
    user = get_object_or_404(User, username=username, is_active=True)
    serializer = UserSerializer(user)
    return Response(serializer.data, status=status.HTTP_200_OK)


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def search_users(request):
    """Search users by username, first name, or last name"""
    query = request.query_params.get("q", "")
    if not query:
        return Response({"results": []}, status=status.HTTP_200_OK)

    users = (
        User.objects.filter(is_active=True).filter(username__icontains=query)
        | User.objects.filter(is_active=True).filter(
            first_name__icontains=query
        )
        | User.objects.filter(is_active=True).filter(
            last_name__icontains=query
        )[:20]
    )

    serializer = UserSerializer(users, many=True)
    return Response({"results": serializer.data}, status=status.HTTP_200_OK)
