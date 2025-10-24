from django.db import models

from app_ride.models import Ride


class RideEvent(models.Model):
    ride = models.ForeignKey(
        Ride,
        on_delete=models.CASCADE,
        related_name="ride_events",
    )

    description = models.TextField()

    created_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Ride Event"
        verbose_name_plural = "Ride Events"

    def __str__(self):
        return f"Ride Event #{self.pk} - {self.description}"
