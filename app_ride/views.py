from django.db.models import Prefetch
from django.utils.timezone import now, timedelta
from rest_framework import viewsets
from rest_framework.decorators import action

from app_ride.filters.ride_filter import RideFilter
from app_ride.models import Ride, RideEvent
from app_ride.serializers.ride import (
    RideCreateSerializer,
    RideDefaultSerializer,
    RideStatusUpdateSerializer,
    RideUpdateSerializer,
)
from utils.mixins.rest_view_mixin import RestViewMixin
from utils.pagination import StandardResultsSetPagination
from utils.permissions import IsAdminUserRole


class RideView(RestViewMixin, viewsets.ModelViewSet):
    queryset = Ride.objects.all()

    http_method_names = ["get", "post", "patch", "delete"]
    permission_classes = [IsAdminUserRole]
    serializer_class = RideDefaultSerializer
    filterset_class = RideFilter
    pagination_class = StandardResultsSetPagination

    action_serializers = {
        "create": RideCreateSerializer,
        "partial_update": RideUpdateSerializer,
        "set_enroute": RideStatusUpdateSerializer,
        "set_pickup": RideStatusUpdateSerializer,
        "set_dropoff": RideStatusUpdateSerializer,
    }
    ordering_fields = [
        "pk",
        "created_at",
        "status",
        "distance",
        "pickup_distance",
        "pickup_time",
    ]
    ordering = ["-pk"]

    def get_queryset(self):
        """
        Dynamically annotates distance and pickup_distance:
            1. `distance` will be annotated if `ordering` parameter has 'distance' or '-distance'.
            2. `pickup_distance` will be annotated if `current_latitude` and `current_longitude` has valid values.

        Prefetches RideEvents
        """
        queryset = super().get_queryset()
        request = getattr(self, "request", None)

        if not request:
            return queryset

        ordering_param = request.GET.get("ordering", "")
        ordering_fields = [f.strip() for f in ordering_param.split(",") if f.strip()]
        current_lat = request.GET.get("current_latitude")
        current_lng = request.GET.get("current_longitude")

        # Annotate distance if requested
        if any(f.lstrip("-") == "distance" for f in ordering_fields):
            queryset = queryset.with_distance()

        # Annotate pickup_distance if coordinates are provided
        if current_lat and current_lng:
            try:
                lat = float(current_lat)
                lng = float(current_lng)
                queryset = queryset.with_pickup_distance(lat, lng)
            except ValueError:
                # Invalid coordinates, fallback silently
                pass

        # Prefetch only today's RideEvents (last 24 hours)
        last_24h = now() - timedelta(hours=24)
        queryset = queryset.prefetch_related(
            Prefetch(
                "ride_events",
                queryset=RideEvent.objects.filter(created_at__gte=last_24h),
                to_attr="todays_ride_events",
            )
        )
        return queryset

    def list(self, request, *args, **kwargs):
        """
        List of Rides

        - PARAMS:
            - search (str, rider__email, driver__email)
            - ordering (str, ["pk", "created_at", "status", "distance", "pickup_distance", "pickup_time"])
            - status (str) ["pending", "en-route", "pickup", "dropoff"]
            - page (int)
            - limit (int)

        - NOTE:
            1. Ordering by `distance` will automatically appends `distance` data to result.
            - It is the calculated distance from the pickup location to the dropoff location.
                e.g https://localhost:8000/?ordering=-distance
            2. Adding valid `current_latitude` and `current_longitude` values to the query_params will automatically appends `pickup_distance` data to result.
            - It is the calculated distance from current location to the pickup location, useful for getting distance of driver's current distance.
            - It also enables ordering by `pickup_distance`
                e.g https://localhost:8000/?current_latitude=7.449681&current_longitude=125.780084&ordering=-pickup_distance
        """

        try:
            queryset = self.filter_queryset(self.get_queryset())

            paginator = self.pagination_class()
            page = paginator.paginate_queryset(queryset, request, view=self)
            serializer = self.get_serializer(page, many=True)

            return self.RestResponse(
                data=paginator.get_paginated_data(serializer.data),
                status=200,
            )

        except Exception as ex:
            return self.RestResponse(errors=str(ex), status=400)

    def retrieve(self, request, *args, **kwargs):
        """
        Retrieve a Ride detail
        {id} refers to the Ride.id
        """
        try:
            return self.RestResponse(
                data=self.get_serializer(self.get_object()).data, status=200
            )
        except Exception as ex:
            return self.RestResponse(errors=str(ex), status=400)

    def create(self, request, *args, **kwargs):
        """
        Create Ride

        - REQUIRED:
            - rider (int, user__id) # non-admin user
            - driver (int, user__id) # non-admin user
            - pickup_latitude (float)
            - pickup_longitude (float)
            - dropoff_latitude (float)
            - dropoff_longitude (float)
            - pickup_time (str, datetime)
        """
        try:
            serializer = self.get_serializer(data=request.data)

            if serializer.is_valid():
                return self.RestResponse(
                    message="Successfully created a Ride record.",
                    data=RideDefaultSerializer(serializer.save()).data,
                    status=201,
                )

            return self.RestResponse(
                message="Invalid data", errors=serializer.errors, status=400
            )

        except Exception as ex:
            return self.RestResponse(errors=str(ex), status=400)

    def partial_update(self, request, *args, **kwargs):
        """
        Update Ride
        {id} refers to the Ride.id

        - OPTIONAL:
            - driver (int, user__id)
            - pickup_latitude (float)
            - pickup_longitude (float)
            - dropoff_latitude (float)
            - dropoff_longitude (float)
            - pickup_time (str, datetime)
        """
        try:
            instance = self.get_object()

            serializer = self.get_serializer(instance, data=request.data, partial=True)

            if serializer.is_valid():
                return self.RestResponse(
                    message="Successfully updated the Ride record.",
                    data=RideDefaultSerializer(serializer.save()).data,
                    status=200,
                )

            return self.RestResponse(
                message="Invalid data", errors=serializer.errors, status=400
            )

        except Exception as ex:
            return self.RestResponse(errors=str(ex), status=400)

    @action(detail=True, methods=["post"], url_path="set/en-route")
    def set_enroute(self, request, *args, **kwargs):
        """
        Update Ride's status to en-route
        {id} refers to the Ride.id
        """
        try:
            instance = self.get_object()

            serializer = self.get_serializer(
                instance,
                data={},
                partial=True,
                context={"status": "en-route"},
            )

            if serializer.is_valid():
                return self.RestResponse(
                    message="Successfully set the Ride as en-route.",
                    data=RideDefaultSerializer(serializer.save()).data,
                    status=200,
                )

            return self.RestResponse(
                message="Invalid data", errors=serializer.errors, status=400
            )

        except Exception as ex:
            return self.RestResponse(errors=str(ex), status=400)

    @action(detail=True, methods=["post"], url_path="set/pickup")
    def set_pickup(self, request, *args, **kwargs):
        """
        Update Ride's status to pickup
        {id} refers to the Ride.id
        """
        try:
            instance = self.get_object()

            serializer = self.get_serializer(
                instance,
                data={},
                partial=True,
                context={"status": "pickup"},
            )

            if serializer.is_valid():
                return self.RestResponse(
                    message="Successfully set the Ride as picked-up.",
                    data=RideDefaultSerializer(serializer.save()).data,
                    status=200,
                )

            return self.RestResponse(
                message="Invalid data", errors=serializer.errors, status=400
            )

        except Exception as ex:
            return self.RestResponse(errors=str(ex), status=400)

    @action(detail=True, methods=["post"], url_path="set/dropoff")
    def set_dropoff(self, request, *args, **kwargs):
        """
        Update Ride's status to drop-off
        {id} refers to the Ride.id
        """
        try:
            instance = self.get_object()

            serializer = self.get_serializer(
                instance,
                data={},
                partial=True,
                context={"status": "dropoff"},
            )

            if serializer.is_valid():
                return self.RestResponse(
                    message="Successfully set the Ride as dropped-off.",
                    data=RideDefaultSerializer(serializer.save()).data,
                    status=200,
                )

            return self.RestResponse(
                message="Invalid data", errors=serializer.errors, status=400
            )

        except Exception as ex:
            return self.RestResponse(errors=str(ex), status=400)

    def destroy(self, request, *args, **kwargs):
        """
        Delete specific Ride
        {id} refers to the Ride.id
        """

        try:
            self.perform_destroy(self.get_object())

            return self.RestResponse(
                message="Successfully deleted the Ride record.",
                status=204,
            )

        except Exception as ex:
            return self.RestResponse(errors=str(ex), status=400)
