from rest_framework import serializers

from app_ride.models import Ride, RideEvent
from app_ride.serializers.ride_event import RideEventDefaultSerializer
from app_user.serializer import UserDefaultSerializer


class RideDefaultSerializer(serializers.ModelSerializer):
    """Ride default serializer."""

    rider = UserDefaultSerializer()
    driver = UserDefaultSerializer()

    # this will show if .with_distance() from RideManager is used.
    distance = serializers.FloatField(read_only=True)

    # this will show if .with_pickup_distance() from RiderManager is used.
    pickup_distance = serializers.FloatField(read_only=True)
    todays_ride_events = RideEventDefaultSerializer(many=True, read_only=True)

    class Meta:
        model = Ride
        fields = "__all__"


class RideCreateSerializer(serializers.ModelSerializer):
    """Ride create serializer."""

    class Meta:
        model = Ride
        exclude = ["status"]


class RideUpdateSerializer(serializers.ModelSerializer):
    """Ride update serializer. Updates basic Ride detail."""

    class Meta:
        model = Ride
        exclude = ["rider", "status"]


class RideStatusUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ride
        fields = ["status"]  # keep field for output
        extra_kwargs = {"status": {"read_only": True}}  # never expected from input

    def validate(self, attrs):
        new_status = self.context.get("status")

        # Defines valid status progression from pending -> en-route -> pickup -> dropoff.
        progression = ["pending", "en-route", "pickup", "dropoff"]
        current_index = progression.index(self.instance.status)
        new_index = progression.index(new_status)

        if new_index != current_index + 1:
            raise serializers.ValidationError(
                f"Cannot set status from {self.instance.status} to {new_status}."
            )

        # store internally for update()
        attrs["_status"] = new_status
        return attrs

    def update(self, instance, validated_data):
        new_status = validated_data.pop("_status")
        instance.status = new_status
        instance.save()

        # create RideEvent
        RideEvent.objects.create(
            ride=instance, description=f"Status changed to {new_status}."
        )
        return instance
