"""
User serializers for managing user accounts and profiles.

This module contains serializers for user registration, authentication,
and profile management with proper validation and data handling.
"""

from ..models import User
from rest_framework import serializers
from django.contrib.auth.password_validation import validate_password


class UserReadOnlySerializer(serializers.ModelSerializer):
    """
    Read-only serializer for user data.
    All fields are read-only by default.
    """

    class Meta:
        model = User
        fields = [
            "id",
            "username",
            "email",
            "first_name",
            "last_name",
            "role",
            "profile_picture",
            "created_at",
            "is_active",
        ]
        read_only_fields = fields


class UserDetailReadOnlySerializer(UserReadOnlySerializer):
    """
    Detailed user serializer with service-populated fields.
    """

    courses_taught_count = serializers.SerializerMethodField()
    courses_enrolled_count = serializers.SerializerMethodField()

    class Meta(UserReadOnlySerializer.Meta):
        fields = UserReadOnlySerializer.Meta.fields + [
            "courses_taught_count",
            "courses_enrolled_count",
        ]
        read_only_fields = fields

    def get_courses_taught_count(self, obj):
        return getattr(obj, "_courses_taught_count", 0)

    def get_courses_enrolled_count(self, obj):
        return getattr(obj, "_courses_enrolled_count", 0)


class UserRegistrationSerializer(serializers.ModelSerializer):
    """
    Serializer for user registration.
    """

    password = serializers.CharField(write_only=True, min_length=8)

    class Meta:
        model = User
        fields = ["username", "email", "password", "role"]

    def validate_password(self, value):
        validate_password(value)
        return value

    def create(self, validated_data):
        return User.objects.create_user(**validated_data)


class UserLoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField()

    def validate(self, attrs):
        email = attrs.get("email")
        password = attrs.get("password")

        if not email or not password:
            raise serializers.ValidationError(
                {"non_field_errors": ["Must include email and password"]}
            )

        try:
            user = User.objects.get(email=email)
            if not user.check_password(password):
                raise serializers.ValidationError(
                    {"non_field_errors": ["Invalid credentials"]}
                )
            if not user.is_active:
                raise serializers.ValidationError(
                    {"non_field_errors": ["User account is disabled"]}
                )
            attrs["user"] = user
        except User.DoesNotExist:
            raise serializers.ValidationError(
                {"email": ["User does not exist"]}
            )

        return attrs


class UserUpdateSerializer(serializers.ModelSerializer):
    """
    Serializer for updating user profile.
    Allows updating username, email, first/last name, role,
    profile picture, and password.
    """

    password = serializers.CharField(
        write_only=True, required=False, min_length=8
    )

    class Meta:
        model = User
        fields = [
            "username",
            "email",
            "first_name",
            "last_name",
            "role",
            "profile_picture",
            "is_active",
            "password",
        ]
        read_only_fields = []

    def validate_password(self, value):
        """Validate password if provided"""
        if value:
            validate_password(value)
        return value
