from rest_framework import serializers

from app_ride.models import RideEvent


class RideEventDefaultSerializer(serializers.ModelSerializer):
    """RideEvent default serializer."""

    class Meta:
        model = RideEvent
        exclude = ["ride"]
