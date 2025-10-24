import django_filters
from django.db.models import Q

from app_ride.models.ride import Ride


class RideFilter(django_filters.FilterSet):
    search = django_filters.CharFilter(method="filter_search")
    status = django_filters.ChoiceFilter(
        choices=[
            ("pending", "pending"),
            ("en-route", "en-route"),
            ("pickup", "pickup"),
            ("dropoff", "dropoff"),
        ]
    )

    class Meta:
        model = Ride
        fields = ["search", "status"]

    def filter_search(self, queryset, name, value):
        return queryset.filter(
            Q(rider__email__icontains=value) | Q(driver__email__icontains=value)
        )
