from datetime import datetime
from django.db.models import query
from rest_framework.viewsets import ModelViewSet, ViewSet
from rest_framework.generics import ListAPIView
from rest_framework.views import APIView
from rest_framework import status
from rest_framework.decorators import action
from django.conf import settings
import redis

from .models import *
from .serializers import *
from .pagination import CustomPagination


r = redis.StrictRedis()

class EstateTypesApiView(APIView):
    queryset = EstateType.objects.all()
    serializer_class = EstateTypeSerializer

    def get(self, request):
        queryset = self.get_queryset()
        serializer = self.serializer_class(queryset, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    

    def get_queryset(self):
        return self.queryset.all()


class BannerListApiView(ListAPIView):
    queryset = EstateBanner.objects.all()

    def get_queryset(self):
        queryset = super().get_queryset()
        now = datetime.now()
        queryset = queryset.filter(
            expires_in__year=now.year,
            expires_in__month=now.month,
            expires_in__day__gte=now.day,
        )
        return queryset


    def get(self, request, slug=None):
        queryset = self.get_queryset()
        if slug:
            estate_type = EstateType.objects.filter(slug=slug)
            if estate_type.exists():
                estate_type = estate_type.first()
                queryset = queryset.filter(estate__estate_type=estate_type)
                serializer = EstateBannerSerializer(queryset, many=True)
                return Response(serializer.data, status=status.HTTP_200_OK)
            else:
                return Response(
                    {
                        "status": False,
                        "error": "Any bannner does not exist.",
                        "result": []
                    },
                    status=status.HTTP_200_OK
                )


class EstateFacilityListView(ListAPIView):
    serializer_class = EstateFacilitySerializer
    queryset = EstateFacility.objects.all()

    def get(self, request):
        queryset = self.get_queryset()
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

    @action(detail=True, methods=["get"], url_name="related")
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

    @action(detail=True, methods=["get"], url_name="related")
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
                result[key]["count"] += 1
                result[key]["percent"] = 100 * result[key]["count"] / ratings.count()
                sum_rating = rating.rating
            result["average_rating"] = sum_rating / ratings.count()
                    
            return Response(result, status=status.HTTP_200_OK)
        else:
            return Response([], status=status.HTTP_200_OK)


class EstateViewSet(ModelViewSet):
    serializer_class = EstateSerializer
    queryset = Estate.objects.all()
    pagination_class = CustomPagination

    def get_queryset(self):
        queryset = super().get_queryset()
        now = datetime.now()
        queryset = queryset.filter(
            expires_in__year=now.year,
            expires_in__month=now.month,
            expires_in__day__gte=now.day,
        )
        return queryset




class UserViewSet(ModelViewSet):
    serializer_class = UserSerializer
    queryset = User.objects.all()


class SmsOTP(ViewSet):
    serializer_class = SendOTPSerializer


    @action(detail=False, methods=["post"], url_path="send-message")
    def send_message(self, request):
        serializer = self.serializer_class(data=request.data)

        result = False

        if serializer.is_valid():
            phone = serializer.validated_data["phone"]

            pin = self.generate_code()

            r.set(phone, pin)
            r.expire(phone, settings.SMS_EXPIRE_SECONDS)

            result = self._send_message(phone, pin)

            if result:
                return Response({
                    "message": "Verifiction code has been sent.",
                    "status": result,
                    "phone": phone,
                    "expire_in": settings.SMS_EXPIRE_SECONDS
                })

        return Response({
            "message": "Verifiction code has not been sent.",
            "status": result,
            "phone": phone,
            "expire_in": None
        })


    @action(detail=False, methods=["post"], url_path="verify")
    def verify(self, request):
        serializer = self.serializer_class(data=request.data)

        result = False

        if serializer.is_valid():
            phone = serializer.validated_data["phone"]
            code = serializer.validated_data["code"]
            result = self._verify(phone, code)
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


    def _send_message(self, phone, code):
        print(phone, code)
        return True
    

    def _verify(self, phone, code):
        if r.exists(phone):
            try:
                pin = str(r.get(phone))[2:-1]
                print(pin, code)
                if str(code) == pin:
                    r.set(phone, None)
                    return True
            except Exception as e:
                print(e)
                return False
        
        return False
    

    def generate_code(self):
        import random
        import string
        digits = string.digits
        return "".join([digits[random.randint(0, len(digits)-1)] for _ in range(5)])