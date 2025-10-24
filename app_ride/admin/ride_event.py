from django.contrib import admin

from app_ride.models.ride_event import RideEvent


@admin.register(RideEvent)
class RideEventAdmin(admin.ModelAdmin):
    list_display = ["id", "ride", "description", "created_at"]
    search_fields = ["description", "ride__rider__email", "ride__driver__email"]
