from elearning.models import User
from rest_framework import serializers


class UserRegistrationSerializer(serializers.ModelSerializer):
    """Serializer for user registration"""

    password = serializers.CharField(write_only=True, min_length=8)

    class Meta:
        model = User
        fields = [
            "email",
            "password",
            "role",
        ]
        extra_kwargs = {
            "password": {"write_only": True},
        }

    def create(self, validated_data):
        # Set username to email for simplicity
        validated_data["username"] = validated_data["email"]
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
        ]
        read_only_fields = ["id", "created_at"]
