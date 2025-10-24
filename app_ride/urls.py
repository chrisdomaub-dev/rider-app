"""
APP_RIDE URLS
"""

from django.urls import path
from django.urls.conf import include
from rest_framework import routers

from .views import RideView

router = routers.DefaultRouter()
router.register("ride", RideView, basename="ride")

urlpatterns = [
    path("", include(router.urls)),
]
