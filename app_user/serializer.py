from django.contrib.auth import get_user_model
from rest_framework import serializers

User = get_user_model()


class UserDefaultSerializer(serializers.ModelSerializer):
    """User default serializer."""

    class Meta:
        model = User
        fields = [
            "id",
            "first_name",
            "last_name",
            "email",
            "phone_number",
            "role",
            "is_active",
        ]
