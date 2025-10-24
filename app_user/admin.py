from django.contrib import admin

from app_user.models import User


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ["id", "email", "role", "is_active", "is_staff", "is_superuser"]
    search_fields = ["email"]
    list_filter = ["role"]
