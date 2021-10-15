from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)


from .views import *


router = DefaultRouter()
router.register("users", UserViewSet, basename="user")
router.register("estate", EstateViewSet, basename="estate")
router.register("sms", SmsOTP, basename="sms")


urlpatterns = [
    path("", include(router.urls)),
    path("estate-types/", EstateTypesApiView.as_view()),
    path("banners/<slug>/", BannerListApiView.as_view()),
    path("facilities/", EstateFacilityListView.as_view()),

    path("token/", TokenObtainPairView.as_view(), name="token_obtain_pair"),
    path("token/refresh/", TokenRefreshView.as_view(), name="token_refresh"),
]