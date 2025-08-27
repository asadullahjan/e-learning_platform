from ..models import User
from rest_framework import serializers
from django.contrib.auth.password_validation import validate_password
from drf_spectacular.utils import extend_schema_field


class UserRegistrationSerializer(serializers.ModelSerializer):
    """Serializer for user registration"""

    password = serializers.CharField(write_only=True, min_length=8)

    class Meta:
        model = User
        fields = [
            "username",
            "email",
            "password",
            "role",
        ]
        extra_kwargs = {
            "password": {"write_only": True},
        }

    def validate_password(self, value):
        validate_password(value)
        return value

    def create(self, validated_data):
        user = User.objects.create_user(**validated_data)
        return user


class UserLoginSerializer(serializers.Serializer):
    """Serializer for user login"""

    email = serializers.EmailField()
    password = serializers.CharField()

    def validate(self, attrs):
        email = attrs.get("email")
        password = attrs.get("password")

        if email and password:
            # Try to find user by email
            try:
                user = User.objects.get(email=email)
                if user.check_password(password):
                    if not user.is_active:
                        raise serializers.ValidationError(
                            "User account is disabled"
                        )
                    attrs["user"] = user
                else:
                    raise serializers.ValidationError("Invalid credentials")
            except User.DoesNotExist:
                raise serializers.ValidationError(
                    "User does not exist for this email"
                )
        else:
            raise serializers.ValidationError(
                "Must include email and password"
            )

        return attrs


class UserSerializer(serializers.ModelSerializer):
    """Serializer for user profile"""

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
            "updated_at",
            "is_active",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]


class UserDetailSerializer(UserSerializer):
    """Detailed user serializer with related data"""

    # These fields will be populated by the service layer
    courses_taught_count = serializers.SerializerMethodField()
    courses_enrolled_count = serializers.SerializerMethodField()

    class Meta(UserSerializer.Meta):
        fields = UserSerializer.Meta.fields + [
            "courses_taught_count",
            "courses_enrolled_count",
        ]

    @extend_schema_field(serializers.IntegerField())
    def get_courses_taught_count(self, obj):
        """Get courses taught count from service-populated field"""
        if hasattr(obj, "_courses_taught_count"):
            return obj._courses_taught_count
        return 0

    @extend_schema_field(serializers.IntegerField())
    def get_courses_enrolled_count(self, obj):
        """Get courses enrolled count from service-populated field"""
        if hasattr(obj, "_courses_enrolled_count"):
            return obj._courses_enrolled_count
        return 0
