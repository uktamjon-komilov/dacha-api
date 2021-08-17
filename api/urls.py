from django.urls import path, include

from rest_framework.routers import DefaultRouter

from .views import DachaViewSet


router = DefaultRouter()
router.register("dacha", DachaViewSet, basename="dacha")


urlpatterns = [
    path("", include(router.urls)),
]