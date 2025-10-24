from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models
from django.db.models import F, Value

from utils.model_query_funcs.distance import Haversine


class RideQuerySet(models.QuerySet):
    def with_distance(self):
        """Annotate distance from pickup point to dropoff point"""
        return self.annotate(
            distance=Haversine(
                F("pickup_latitude"),
                F("pickup_longitude"),
                F("dropoff_latitude"),
                F("dropoff_longitude"),
            )
        )

    def with_pickup_distance(self, lat, lng):
        """Annotate distance from a specific point (e.g. driver's location)"""

        return self.annotate(
            pickup_distance=Haversine(
                Value(lat),
                Value(lng),
                F("pickup_latitude"),
                F("pickup_longitude"),
            )
        )


class RideManager(models.Manager.from_queryset(RideQuerySet)):
    """
    Appends custom distance helpers to the default model manager.
    """

    pass


class Ride(models.Model):
    objects = RideManager()

    STATUS_CHOICES = [
        ("pending", "Pending"),
        ("en-route", "En Route"),
        ("pickup", "Pickup"),
        ("dropoff", "Dropoff"),
    ]

    rider = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="rides_as_rider",
    )
    driver = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="rides_as_driver",
    )

    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="pending")

    pickup_latitude = models.FloatField()
    pickup_longitude = models.FloatField()
    dropoff_latitude = models.FloatField()
    dropoff_longitude = models.FloatField()

    pickup_time = models.DateTimeField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Ride"
        verbose_name_plural = "Rides"

    def __str__(self):
        return f"Ride #{self.pk} - {self.rider} ({self.status})"

    def clean(self):
        """Prevent admins from being assigned."""
        if self.rider.role == "admin":
            raise ValidationError("Rider must not be an admin user.")
        if self.driver.role == "admin":
            raise ValidationError("Driver must not be an admin user.")

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)
