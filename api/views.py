from django.utils import timezone
from django.db.models import Q, F, Func
from rest_framework.viewsets import ModelViewSet, ViewSet, GenericViewSet, mixins
from rest_framework.generics import ListAPIView, CreateAPIView
from rest_framework.views import APIView
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page
from django.views.decorators.vary import vary_on_headers
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.parsers import JSONParser, MultiPartParser
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from paycomuz import Paycom
from clickuz import ClickUz
import random
from django.conf import settings

from .models import *
from .serializers import *
from .pagination import CustomPagination, OneItemPagination
from .utils import *
from .func_views import *
from .mixins import SmsVerificationMixin
from .permissions import *
from . import tasks
from .payments.paycom import *
from .payments.click import *


import redis
r = redis.StrictRedis()


class EstateTypesApiView(APIView):
    queryset = EstateType.objects.all().order_by("priority")
    serializer_class = EstateTypeSerializer

    def get(self, request):
        queryset = self.get_queryset()
        serializer = self.serializer_class(queryset, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def get_queryset(self):
        return self.queryset.all()


class BannersViewSet(
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    GenericViewSet
):
    queryset = Estate.objects.select_related("estate_type") \
        .select_related("price_type") \
        .prefetch_related("facilities") \
        .prefetch_related("booked_days") \
        .prefetch_related("translations") \
        .filter(
        is_published=True,
        is_banner=True,
        expires_in__gte=timezone.now()
    )
    serializer_class = EstateSerializer

    def get(self, request):
        serializer = EstateSerializer(self.queryset, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def retrieve(self, request, slug=None, *args, **kwargs):
        queryset = self.queryset.filter(estate_type__slug=slug)
        serializer = EstateSerializer(queryset, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class EstateFacilityListView(ListAPIView):
    serializer_class = EstateFacilitySerializer
    queryset = EstateFacility.objects.all()

    def get(self, request):
        queryset = self.get_queryset()
        params = request.query_params
        category_id = params.get("category", None)
        if category_id:
            category = EstateType.objects.filter(
                Q(id=category_id) | Q(slug=category_id)
            )
            if category.exists():
                category = category.first()
                queryset = queryset.filter(category=category).distinct()
        serializer = self.serializer_class(queryset, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class CurrencyListView(ListAPIView):
    serializer_class = CurrencySerializer
    queryset = Currency.objects.all()

    def get(self, request):
        queryset = self.get_queryset()
        serializer = self.serializer_class(queryset, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class EstateBookingViewSet(ModelViewSet):
    serializer_class = EstateBookingSerializer
    queryset = EstateBooking.objects.all()

    @action(detail=True, methods=["get"], url_path="related")
    def related(self, request, pk=None):
        estate = Estate.objects.filter(id=pk)
        if estate.exists():
            estate = estate.first()
            bookings = EstateBooking.objects.filter(estate=estate)
            serializer = self.serializer_class(bookings, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
        else:
            return Response([], status=status.HTTP_200_OK)


class EstateRatingViewSet(ModelViewSet):
    serializer_class = EstateRatingSerializer
    queryset = EstateRating.objects.all()

    def create(self, request):
        request_serializer = self.serializer_class(data=request.data)
        if request_serializer.is_valid():
            validated_data = request_serializer.validated_data
            rating = EstateRating.objects.filter(
                estate=validated_data["estate"],
                user=validated_data["user"]
            )
            if rating.exists():
                rating = rating.first()
                rating.rating = validated_data["rating"]
            else:
                rating = EstateRating(
                    estate=validated_data["estate"],
                    user=validated_data["user"],
                    rating=validated_data["rating"]
                )
            rating.save()
        serializer = EstateRatingSerializer(rating)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(detail=False, methods=["get"], url_path="mine")
    def rated_estates(self, request):
        estateratings = EstateRating.objects.filter(
            user=request.user).distinct("estate__id")
        serializer = self.serializer_class(estateratings, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(detail=True, methods=["get"], url_path="related")
    def related(self, request, pk=None):
        estate = Estate.objects.filter(id=pk)
        if estate.exists():
            estate = estate.first()
            ratings = EstateRating.objects.filter(estate=estate)
            result = {
                "total": ratings.count(),
                "average_rating": 0.0,
                "5": {
                    "percent": 0.0,
                    "count": 0
                },
                "4": {
                    "percent": 0.0,
                    "count": 0
                },
                "3": {
                    "percent": 0.0,
                    "count": 0
                },
                "2": {
                    "percent": 0.0,
                    "count": 0
                },
                "1": {
                    "percent": 0.0,
                    "count": 0
                }
            }
            sum_rating = 0.0
            for rating in ratings:
                key = str(rating.rating)
                if key != "0":
                    result[key]["count"] += 1
                    result[key]["percent"] = round(
                        100 * result[key]["count"] / ratings.count(), 2)
                    sum_rating += rating.rating

            count = ratings.count()
            if count == 0:
                result["average_rating"] = 0.0
            else:
                result["average_rating"] = round(
                    sum_rating / ratings.count(), 2)

            return Response(result, status=status.HTTP_200_OK)
        else:
            return Response([], status=status.HTTP_200_OK)


class EstateViewsCreateView(CreateAPIView):
    serializer_class = EstateViewsSerializer
    queryset = EstateViews.objects.all()
    authentication_classes = []
    permission_classes = []

    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            ip = serializer.validated_data["ip"]
            estate = serializer.validated_data["estate"]
            views = EstateViews.objects.filter(ip=ip, estate=estate)
            if not views.exists():
                view = EstateViews(ip=ip, estate=estate)
                view.save()
            else:
                view = views.first()
            serializer = self.serializer_class(view)
            return Response(serializer.data, status=status.HTTP_200_OK)
        else:
            return Response({}, status=status.HTTP_400_BAD_REQUEST)


class AddressListView(ListAPIView):
    serializer_class = RegionSerializer
    queryset = Region.objects.all()

    def get(self, request):
        queryset = self.get_queryset()
        serializer = self.serializer_class(queryset, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class PopularPlacesListView(ListAPIView):
    serializer_class = PopularPlaceSerializer
    queryset = PopularPlace.objects.all()

    def get(self, request):
        queryset = self.get_queryset()
        serializer = self.serializer_class(queryset, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class EstateRetrieveViewSet(
    mixins.RetrieveModelMixin,
    mixins.DestroyModelMixin,
    GenericViewSet
):
    serializer_class = EstateSerializer
    queryset = Estate.objects.all()

    def get_serializer_class(self):
        if self.action == "retrieve":
            return EstateGetSerializer
        return self.serializer_class
    

    def get_queryset(self):
        queryset = self.queryset
        data = self.request.data

        category = data.get("category", None)
        if category:
            try:
                category_id = int(category)
                queryset = queryset.filter(estate__type__id=category_id)
            except:
                category_slug = category
                queryset = queryset.filter(estate__type__slug=category_slug)
        
        return queryset
    

    @action(detail=False, methods=["get"], url_path="all-random")
    def all_random(self, request, *args, **kwargs):
        response = Response()
        response.data = {}

        queryset = self.get_queryset()
        queryset = get_estate_queryset(request.query_params, queryset)

        top_estates = list(queryset.filter(is_top=True).order_by("?"))
        simple_estates = list(queryset.filter(is_simple=True).order_by("-created_at"))

        estates = []
        for simple_index, simple_estate in enumerate(simple_estates):
            num = random.choice([3, 2])
            if simple_index % num == 0 and len(top_estates) > 0:
                top_estate = top_estates.pop()
                estates.append(top_estate)
            estates.append(simple_estate)
        
        if len(top_estates) > 0:
            for i in range(len(estates)):
                if estates[i].is_simple and estates[i + 1].is_simple and len(top_estates) > 0:
                    top_estate = top_estates.pop()
                    estates.insert(i + 1, top_estate)
        
        if len(top_estates) > 0:
            estates.insert(len(estates) // 2, top_estates)
        
        freq = set()
        result = []
        for estate in estates:
            if estate.id not in freq:
                result.append(estate)
                freq.add(estate.id)

        estates_serializer = self.serializer_class(
            result,
            many=True,
            context={
                "request": request
            }
        )
        response.data["estates"] = [*estates_serializer.data]

        ads = self.get_queryset().filter(is_ads_plus=True).order_by("?")
        ads_serializer = self.serializer_class(
            ads,
            many=True,
            context={
                "request": request
            }
        )
        response.data["ads"] = [*ads_serializer.data]

        return response


class EstateViewSet(ModelViewSet):
    serializer_class = EstateSerializer
    queryset = Estate.objects.all()
    pagination_class = CustomPagination
    parser_classes = [JSONParser, MultiPartParser]
    languages_codes = settings.PARLER_LANGUAGES[None]
    permission_classes = []

    def get_serializer_context(self):
        return {
            "request": self.request,
            "format": self.format_kwarg,
            "view": self
        }

    def get_queryset(self):
        queryset = super().get_queryset()
        data = self.request.query_params
        queryset = get_estate_queryset(data, queryset)
        return queryset

    def create(self, request, *args, **kwargs):
        data = {**request.data}
        for key in data.keys():
            data[key] = data[key][0]
        if not data.get("user", None):
            data["user"] = request.user.id
        tasks.create_estate(data)
        return Response({}, status=status.HTTP_200_OK)

    def partial_update(self, request, pk=None, *args, **kwargs):
        print(request.data)
        data = {**request.data}
        for key in data.keys():
            data[key] = data[key][0]
        if not data.get("user", None):
            data["user"] = request.user.id
        tasks.update_estate(pk, data)
        return Response({}, status=status.HTTP_200_OK)

    @action(detail=True, methods=["get"], url_path="similar")
    def similar(self, request, pk=None):
        estate = Estate.objects.get(id=pk)
        estates = Estate.objects.all()[:3]
        serializer = self.serializer_class(
            estates,
            many=True,
            context={"request": request}
        )
        return Response(serializer.data, status=status.HTTP_200_OK)
        estates = Estate.objects.select_related("estate_type") \
            .select_related("price_type") \
            .select_related("popular_place") \
            .prefetch_related("translations") \
            .prefetch_related("facilities") \
            .annotate(
                price_diff=Func(
                    F("weekday_price") - estate.weekday_price
                ),
                function="ABS"
        ) \
            .order_by("-price_diff") \
            .exclude(id=estate.id)
        greater = estates.filter(weekday_price__gte=estate.weekday_price)
        _all = None
        if greater.count() < 3:
            smaller = estates.order_by("price_diff").filter(
                weekday_price__lte=estate.weekday_price)
            if smaller.count() < 3:
                _all = greater | smaller
            else:
                _all = smaller
        else:
            _all = greater
        if _all.count() < 3:
            _all = estates[:3]
        serializer = self.serializer_class(
            _all,
            many=True,
            context={"request": request}
        )
        return Response(serializer.data, status=status.HTTP_200_OK)


class EstateAdsPlusViewSet(
    mixins.ListModelMixin,
    GenericViewSet
):
    serializer_class = EstateAdsPlusSerializer
    queryset = Estate.objects.filter(
        is_ads_plus=True,
        expires_in__gte=timezone.now()
    )
    pagination_class = OneItemPagination

    def get_serializer_context(self):
        return {
            "request": self.request,
            "format": self.format_kwarg,
            "view": self
        }

    def get_queryset(self):
        queryset = super().get_queryset()
        estate_type = self.request.query_params.get("estate_type", None)
        if estate_type:
            try:
                _id = int(estate_type)
                queryset = queryset.filter(estate_type__id=_id)
            except:
                queryset = queryset.filter(estate_type__slug=estate_type)

        return queryset.defer("id", "photo", "thumbnail", "translations", "weekday_price").distinct()


class WishlistViewSet(ModelViewSet):
    serializer_class = WishlistSaveSerializer
    queryset = Wishlist.objects.all()

    def get_serializer_context(self):
        return {
            "request": self.request,
            "format": self.format_kwarg,
            "view": self
        }

    @action(detail=False, methods=["post"], url_path="mywishlist")
    def my_wishlist(self, request):
        queryset = Wishlist.objects.filter(user=request.user)
        serializer = WishlistSerializer(queryset, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(detail=False, methods=["post"], url_path="add-to-wishlist")
    def add_to_wishlist(self, request):
        if request.user.is_authenticated:
            user = request.user
            data = request.data
            serializer = self.serializer_class(data=request.data)
            if serializer.is_valid():
                wishlist = Wishlist.objects.filter(
                    user=user,
                    estate__id=data["estate"]
                )
                if not wishlist.exists():
                    estate = Estate.objects.get(id=data["estate"])
                    wishlist = Wishlist(user=user, estate=estate)
                    wishlist.save()
                else:
                    wishlist = wishlist.first()
                serializer = WishlistSerializer(wishlist)
                return Response(serializer.data, status=status.HTTP_200_OK)
            else:
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response({
                "detail": "Only registered users can add to their wishlist."
            }, status=status.HTTP_401_UNAUTHORIZED)

    @action(detail=False, methods=["post"], url_path="remove-from-wishlist")
    def remove_from_wishlist(self, request):
        if request.user.is_authenticated:
            user = request.user
            data = request.data
            wishlist = Wishlist.objects.filter(
                user=user,
                estate__id=data["estate"]
            )
            if wishlist.exists():
                wishlist.delete()
            return Response({
                "detail": "Removed from wishlist"
            }, status=status.HTTP_200_OK)
        else:
            return Response({
                "detail": "Only registered users can modify their wishlist."
            }, status=status.HTTP_401_UNAUTHORIZED)


class UserViewSet(ModelViewSet, SmsVerificationMixin):
    serializer_class = UserSerializer
    queryset = User.objects.all()
    permission_classes = []
    authentication_classes = []

    @action(detail=False, methods=["post"], url_path="estates")
    def estates(self, request):
        data = request.data
        estates = Estate.objects.filter(user__id=data["user"])
        serializer = EstateSerializer(estates, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(detail=False, methods=["post"], url_path="reset-password/step1")
    def reset_password_step1(self, request):
        data = request.data
        phone = data["phone"].strip().replace(" ", "")
        user = User.objects.filter(phone=phone)
        if user.exists():
            user = user.first()
            self._send_message(user.phone)
            return Response({"result": True}, status=status.HTTP_200_OK)
        return Response({"result": False}, status=status.HTTP_200_OK)

    @action(detail=False, methods=["post"], url_path="reset-password/step2")
    def reset_password_step2(self, request):
        data = request.data
        phone = data["phone"].strip().replace(" ", "")
        code = data["code"]
        if self._verify(phone, code):
            return Response({"result": True}, status=status.HTTP_200_OK)
        return Response({"result": False}, status=status.HTTP_200_OK)

    @action(detail=False, methods=["post"], url_path="reset-password/step3")
    def reset_password_step3(self, request):
        data = request.data
        phone = data["phone"].strip().replace(" ", "")
        code = data["code"]
        password = str(data["new_password"])
        if self._verify(phone, code):
            user = User.objects.filter(phone=phone)
            if user.exists():
                user = user.first()
                user.set_password(password)
                print(password)
                user.save()
                r.set(phone, "")
                return Response({"result": True}, status=status.HTTP_200_OK)
        return Response({"result": False}, status=status.HTTP_200_OK)


class SmsOTP(ViewSet, SmsVerificationMixin):
    serializer_class = SendOTPSerializer
    authentication_classes = []
    permission_classes = []

    @action(detail=False, methods=["post"], url_path="send-message")
    def send_message(self, request):
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            phone = serializer.validated_data["phone"]
            phone_check = phone.replace("+", "")
            if not User.objects.filter(phone__contains=phone_check).exists():
                sent = self._send_message(phone)
                if sent:
                    return Response({
                        "message": "OTP has been sent.",
                        "status": sent,
                        "phone": phone
                    })
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        return Response({
            "message": "OTP has not been sent.",
            "status": False,
            "phone": None
        })

    @action(detail=False, methods=["post"], url_path="verify")
    def verify(self, request):
        serializer = self.serializer_class(data=request.data)
        result = False
        if serializer.is_valid():
            phone = serializer.validated_data["phone"]
            code = serializer.validated_data["code"]
            result = self._verify(phone, code)
            r.set(phone, "")
            if result:
                return Response({
                    "message": "Verifiction is successful.",
                    "status": result,
                    "phone": phone
                })

        return Response({
            "message": "Verifiction isn't successful.",
            "status": result,
            "phone": None
        })


class StaticPageListView(ListAPIView):
    serializer_class = StaticPageSerializer
    queryset = StaticPage.objects.all()

    def get(self, request):
        queryset = self.get_queryset()
        serializer = self.serializer_class(queryset, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class ServiceViewSet(
    mixins.ListModelMixin,
    GenericViewSet
):
    serializer_class = ServiceSerializer
    items_serializer_class = ServiceItemSerializer
    queryset = Service.objects.all()

    def list(self, request):
        queryset = self.get_queryset()
        serializer = self.serializer_class(queryset, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(detail=True, methods=["get"], url_path="items")
    def service_items(self, request, pk=None):
        service_items = ServiceItem.objects.filter(service__id=pk)
        serializer = self.items_serializer_class(service_items, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class PaymentLinkViewSet(ViewSet):
    serializer_class = PaymentLinkSerializer
    authentication_classes = []
    permission_classes = []

    @action(detail=False, methods=["post"], url_path="click")
    def click(self, request):
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            data = serializer.validated_data
            user = User.objects.get(id=data["user"])
            amount = data["amount"]
            return_url = data["return_url"]
            charge = BalanceCharge(
                user=user,
                amount=amount,
                reason="click",
                type="in"
            )
            charge.save()
            url = ClickUz.generate_url(
                order_id=str(charge.id),
                amount=str(charge.amount),
                return_url=return_url
            )
            return Response({
                "link": url
            }, status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=["post"], url_path="payme")
    def payme(self, request):
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            data = serializer.validated_data
            user = User.objects.get(id=data["user"])
            amount = data["amount"]
            return_url = data["return_url"]
            charge = BalanceCharge(
                user=user,
                amount=amount,
                reason="click",
                type="in"
            )
            charge.save()
            paycom = Paycom()
            url = paycom.create_initialization(
                amount=charge.amount * 100,
                order_id=str(charge.id),
                return_url=return_url
            )
            return Response({
                "link": url
            }, status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class EstatePhotoViewSet(ModelViewSet):
    queryset = EstatePhoto.objects.all()
    serializer_class = EstatePhotoSerializer

    def create(self, request, *args, **kwargs):
        serializer = EstatePhotoSerializer(data=request.data)
        if serializer.is_valid():
            estate_photo = EstatePhoto(
                photo=serializer.validated_data["photo"]
            )
            estate_photo.save()
            serializer = EstatePhotoSerializer(estate_photo)
            return Response(
                serializer.data,
                status=status.HTTP_200_OK
            )
        return Response(serializer.errors)


class TempPhotoViewSet(ModelViewSet):
    queryset = TempPhoto.objects.all()
    serializer_class = TempPhotoSerializer

    def update(self, request):
        return Response(status=status.HTTP_404_NOT_FOUND)

    def partial_update(self, request):
        return Response(status=status.HTTP_404_NOT_FOUND)


class TopBannersListView(ListAPIView):
    queryset = Estate.objects.filter(is_topbanner=True)
    serializer_class = EstateSerializer


class AdsRandomView(APIView):
    queryset = Estate.objects.select_related("estate_type").select_related(
        "price_type").prefetch_related("translations").prefetch_related("facilities").filter(is_ads=True)
    serializer_class = EstateSerializer

    def get(self, request):
        queryset = self.get_queryset()
        if queryset.count() == 0:
            return Response(status=status.HTTP_200_OK)
        elif queryset.count() == 1:
            estate = queryset.first()
        elif queryset.count() > 1:
            estate = queryset.order_by("?").first()
        serializer = self.serializer_class(estate)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def get_queryset(self):
        return self.queryset.all()


class AdvertisingPlansListView(ListAPIView):
    queryset = AdvertisingPlan.objects.all()
    serializer_class = AdvertisingPlanSerializer


class MessagingViewSet(ViewSet):
    @action(detail=False, methods=["post"], url_path="make-read")
    def make_read(self, request):
        data = request.data
        messages = Message.objects.filter(
            estate__id=data["estate"],
            sender__id=data["sender"],
            is_read=False
        )
        messages.update(is_read=True)
        return Response({})

    @action(detail=False, methods=["post"], url_path="send-message")
    def send_message(self, request):
        serializer = MessageSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(sender=request.user)
            data = serializer.validated_data
            messages = Message.objects.filter(estate=data["estate"]).filter(
                Q(
                    Q(sender=request.user) &
                    Q(receiver=data["receiver"])
                )
                |
                Q(
                    Q(sender=data["receiver"]) &
                    Q(receiver=request.user)
                )
            )
            messages = messages.order_by("id")
            estate = data["estate"]
            all_serializer = AllMessageSerializer(
                messages, many=True, context={"request": request})
            messages = all_serializer.data
            estate_dict = EstateShortSerializer(estate).data
            result = {
                "estate": estate_dict,
                "results": messages
            }
            return Response(result, status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=["get"], url_path="mychats")
    def my_chats(self, request):
        result = []

        messages1 = Message.objects.filter(
            receiver=request.user,
            estate__user=request.user
        ).distinct("sender")

        messages2 = Message.objects.filter(
            receiver=request.user
        ).exclude(estate__user=request.user).distinct("estate")

        messages3 = Message.objects.filter(
            sender=request.user
        ).exclude(estate__user=request.user).distinct("sender")

        messages = [*messages1, *messages2, *messages3]
        freq = set()

        for item in messages:
            if item.sender.id == request.user.id:
                sender_id = item.receiver.id
            else:
                sender_id = item.sender.id

            try:
                unique_id = "{}-{}".format(sender_id, item.estate.id)
                if unique_id not in freq:
                    freq.add(unique_id)
                    result.append(item)
            except:
                pass

        all_serializer = AllMessageSerializer(
            result, many=True, context={"request": request})
        return Response(all_serializer.data, status=status.HTTP_200_OK)

    @action(detail=False, methods=["post"], url_path="delete-chat")
    def delete_chat(self, request):
        messages = Message.objects.filter(Q(sender=request.user) | Q(
            receiver=request.user)).filter(estate=request.data["estate"])
        messages.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=False, methods=["post"], url_path="get-messages")
    def get_messages(self, request):
        data = request.data
        estate = Estate.objects.get(id=data["estate"])
        messages = Message.objects.filter(estate=data["estate"]).filter(
            Q(
                Q(sender=request.user) &
                Q(receiver=data["receiver"])
            )
            |
            Q(
                Q(sender=data["receiver"]) &
                Q(receiver=request.user)
            )
        )
        messages = messages.order_by("id")
        all_serializer = AllMessageSerializer(
            messages, many=True, context={"request": request})
        messages = all_serializer.data
        estate_dict = {**EstateShortSerializer(estate).data}
        result = {
            "estate": estate_dict,
            "results": messages
        }
        return Response(result, status=status.HTTP_200_OK)


class TransactionViewSet(ViewSet):
    serializer_class = BalanceChargeSerializer
    queryset = BalanceCharge.objects.filter(completed=True)
    authentication_classes = [JWTAuthentication]

    @action(detail=False, methods=["get"], url_path="in")
    def input_transaction(self, request):
        if not request.user.is_authenticated:
            return Response(status=status.HTTP_401_UNAUTHORIZED)
        charges = self.queryset.filter(
            type="in",
            user=request.user,
        ).order_by("-date")
        serializer = self.serializer_class(charges, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(detail=False, methods=["get"], url_path="out")
    def output_transaction(self, request):
        if not request.user.is_authenticated:
            return Response(status=status.HTTP_401_UNAUTHORIZED)
        charges = self.queryset.filter(
            type="out",
            user=request.user
        ).order_by("-date")
        serializer = self.serializer_class(charges, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class FeadbackCreateAPIView(CreateAPIView):
    queryset = Feedback.objects.all()
    serializer_class = FeedbackSerializer
    authentication_classes = []
    permission_classes = []


class StaticTranslationViewSet(mixins.ListModelMixin, GenericViewSet):
    queryset = StaticTranslation.objects.all()
    serializer_class = StaticTranslationSerializer

    @method_decorator(cache_page(60*60*2))
    @method_decorator(vary_on_headers("Accept-Language"))
    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        instance_result = self.serializer_class(
            queryset,
            many=True,
            context={"request": request}
        ).data
        result = {}
        for instance in list(instance_result):
            result[instance["key"]] = instance["value"]
        return Response(result, status=status.HTTP_200_OK)



class MobileAppHomepageAPIView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticatedOrReadOnly]

    def get(self, request):
        # response content description
        data = {
            "banners": [],
            "categories": [
                {
                    "id": 1,
                    "title": "Dacha",
                    "icon": "",
                    "estates": [],
                    "banners": []
                }
            ]
        }

        # detecting the language code
        lang_code = request.LANGUAGE_CODE

        # getting the current datetime
        now = timezone.now()

        # retrieving all the top banners from the database
        top_banners = Estate.objects.language(lang_code).filter(is_topbanner=True, expires_in__gt=now).only("id", "photo", "thumbnail")

        # iterating over the top banners list, and serializing
        # each top banner with only required info
        for top_banner in top_banners:
            data["banners"].append({
                "id": top_banner.id,
                "photo": top_banner.photo,
                "thumbnail": top_banner.thumbnail,
            })

        # retrieving all the categories from the database
        categories = EstateType.objects.language(lang_code).prefetch_related("estates").all()
        if request.user.is_authenticated:
            wishlist_estate_ids = Wishlist.objects.filter(user=request.user) \
                .values_list("estate_id", flat=True)
        else:
            wishlist_estate_ids = []

        for category in categories:
            estates = category.estates.filter(is_top=True, expires_in__gt=now) \
                .only("id", "photo", "title", "average_rating", "weekday_price")
            estates_data = []
            for estate in estates:
                estates_data.append({
                    "id": estate.id,
                    "photo": estate.photo.url,
                    "title": estate.title,
                    "liked": estate.id in wishlist_estate_ids,
                    "average_rating": estate.rating_average,
                    "weekday_price": estate.weekday_price
                })

            estates = category.estates.filter(is_banner=True, expires_in__gt=now) \
                .only("id", "photo", "title", "average_rating", "weekday_price")
            banners_data = []

            data["categories"].append({
                "id": category.id,
                "title": category.title,
                "icon": category.icon.url,
                "estates": estates_data,
                "banners": banners_data
            })
        
        return Response(data=data)