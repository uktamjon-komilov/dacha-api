from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)

from api.check_creates import check_create_plans, check_create_regions_districts


from .views import *

router = DefaultRouter()
router.register("bookings", EstateBookingViewSet, basename="bookings")
router.register("ratings", EstateRatingViewSet, basename="ratings")
router.register("users", UserViewSet, basename="user")
router.register("estate", EstateViewSet, basename="estate")
router.register("estater", EstateRetrieveViewSet, basename="estater")
router.register("estatephotos", EstatePhotoViewSet, basename="estatephotos")
router.register("tempphoto", TempPhotoViewSet, basename="tempphoto")
router.register("sms", SmsOTP, basename="sms")
router.register("payment-links", PaymentLinkViewSet, basename="payment-links")
router.register("wishlist", WishlistViewSet, basename="wishlist")
router.register("messages", MessagingViewSet, basename="messages")
router.register("transactions", TransactionViewSet, basename="transactions")
router.register("services", ServiceViewSet, basename="services")
router.register("banners", BannersViewSet, basename="banners")
router.register("adsplus", EstateAdsPlusViewSet, basename="adsplus")
router.register("static-translations", StaticTranslationViewSet,
                basename="static-translations")


urlpatterns = [
    path("estate/topbanners/", TopBannersListView.as_view()),
    path("estate/ads/", AdsRandomView.as_view()),
    path("estate/myestates/", myestates),
    path("estate/<int:pk>/", estate_partial_update),
    path("estate/<str:slug>/myestates/", myestates_by_type),
    path("estate/last/", last_estate),
    path("estate/<str:slug>/top/", top_estates),
    path("estate/<str:slug>/simple/", simple_estates),
    path("estate/<str:slug>/<int:id>/", single_estate),
    path("estate/<str:slug>/", all_estates),
    path("mobile/home/", MobileAppHomepageAPIView.as_view()),
    path("", include(router.urls)),


    path("advertise/<str:slug>/<int:id>/", advertise),
    path("extrimal-prices/", get_extrimal_prices),
    path("advertising-plans/", AdvertisingPlansListView.as_view()),

    path("users/renew-password/", renew_password),

    path("estate-types/", EstateTypesApiView.as_view()),
    path("staticpages/", StaticPageListView.as_view()),
    path("facilities/", EstateFacilityListView.as_view()),
    path("currencies/", CurrencyListView.as_view()),
    path("views/", EstateViewsCreateView.as_view()),
    path("address/", AddressListView.as_view()),
    path("popular-places/", PopularPlacesListView.as_view()),
    path("feedback/", FeadbackCreateAPIView.as_view()),

    path("token/", TokenObtainPairView.as_view(), name="token_obtain_pair"),
    path("token/refresh/", TokenRefreshView.as_view(), name="token_refresh"),

    path("paycom/", PaycomView.as_view()),
    path("click/", ClickView.as_view()),
]


try:
    check_create_plans()
    # check_create_regions_districts()
except Exception as e:
    print(e)
