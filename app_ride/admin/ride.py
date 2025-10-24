from django.contrib import admin
from django.contrib.auth import get_user_model

from app_ride.models import Ride

User = get_user_model()


@admin.register(Ride)
class RideAdmin(admin.ModelAdmin):
    list_display = ["id", "rider", "driver", "status", "pickup_time", "created_at"]
    list_filters = ["status"]
    search_fields = ["rider__email", "driver__email"]

    # This will limit the rider and driver's selection to basic users only.
    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name in ["rider", "driver"]:
            kwargs["queryset"] = User.objects.exclude(role="admin")
        return super().formfield_for_foreignkey(db_field, request, **kwargs)
