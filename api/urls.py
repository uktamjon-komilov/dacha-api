from django.urls import path, include

from rest_framework.routers import DefaultRouter

from .views import *


router = DefaultRouter()
router.register("users", UserViewSet, basename="user")
router.register("estate", EstateViewSet, basename="estate")


urlpatterns = [
    path("", include(router.urls)),
    path("login/", CustomAuthToken.as_view()),
    path("facilities/", EstateFacilityListView.as_view()),
]