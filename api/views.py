from datetime import datetime
from django.db.models import Q
from django.contrib.contenttypes.models import ContentType
from rest_framework.viewsets import ModelViewSet, ViewSet
from rest_framework.generics import ListAPIView, CreateAPIView, DestroyAPIView
from rest_framework.views import APIView
from rest_framework import status
from rest_framework.decorators import action, parser_classes
from rest_framework.parsers import JSONParser, MultiPartParser
from django.conf import settings
import redis
import json
from django.core.files import File
import os

from .models import *
from .serializers import *
from .pagination import CustomPagination
from .utils import *


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
            
            count = ratings.count()
            if count == 0:
                result["average_rating"] = 0.0
            else:
                result["average_rating"] = sum_rating / ratings.count()
                
                    
            return Response(result, status=status.HTTP_200_OK)
        else:
            return Response([], status=status.HTTP_200_OK)


class EstateViewsCreateView(CreateAPIView):
    serializer_class = EstateViewsSerializer
    queryset = EstateViews.objects.all()

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
    queryset = Estate.objects.all()

    def get(self, request):
        addresses = []
        queryset = Estate.objects.all()
        q = self.request.query_params.get("q", None)
        if q:
            queryset = queryset.filter(address__contains=q)
    
        for item in queryset:
            if not item.address in addresses:
                addresses.append(item.address)
        return Response(addresses, status=status.HTTP_200_OK)


class EstateViewSet(ModelViewSet):
    serializer_class = EstateSerializer
    queryset = Estate.objects.all()
    pagination_class = CustomPagination
    parser_classes = [JSONParser, MultiPartParser]
    languages_codes = settings.PARLER_LANGUAGES[None]

    def get_queryset(self):
        queryset = super().get_queryset()
        now = datetime.now()
        queryset = queryset.filter(
            expires_in__year=now.year,
            expires_in__month=now.month,
            expires_in__day__gte=now.day,
        )

        address = self.request.query_params.get("address", None)
        if address:
            queryset = queryset.filter(address__contains=address)
        
        fromDate = self.request.query_params.get("fromDate", None)
        toDate = self.request.query_params.get("toDate", None)
        if fromDate and toDate:
            empty_estate_ids = []
            for item in queryset:
                bookings = item.booked_days.all()
                empty = True
                for booking in bookings:
                    from_year, from_month, from_day = list(map(int, fromDate.split("-")))
                    to_year, to_month, to_day = list(map(int, toDate.split("-")))
                    year, month, day = list(map(int, str(booking.date).split("-")))
                    empty = not (
                        (from_year <= year <= to_year)
                        and
                        (from_month <= month <= to_month)
                        and
                        (from_day <= day <= to_day)
                    )
                if empty:
                    empty_estate_ids.append(item.id)
            queryset = queryset.filter(id__in=empty_estate_ids)

        
        people = self.request.query_params.get("people", None)
        if people:
            queryset = queryset.filter(people__gte=int(people))
        
        price = self.request.query_params.get("price", None)
        if price:
            queryset = queryset.filter(price__gte=float(price))

        term = self.request.query_params.get("term", None)
        if term:
            queryset = queryset.filter(
                Q(title__contains=term) |
                Q(description__contains=term) |
                Q(address__contains=term)
            )

        facility_ids = self.request.query_params.get("facility_ids", None)
        if facility_ids:
            facility_ids = list(map(int, facility_ids.split(",")))
            queryset = queryset.filter(facilities__id__in=facility_ids)

        return queryset
    
    
    def create(self, request, *args, **kwargs):
        data = request.data

        facility_ids = list(map(int, data["facilities"][1:-1].split(",")))
        translations = json.loads(request.data["translations"])
        
        user = User.objects.get(id=data["user"])
        estate_type = EstateType.objects.get(id=data["estate_type"])
        price_type = Currency.objects.get(id=data["price_type"])
        facilities = EstateFacility.objects.filter(id__in=facility_ids)
        
        estate = Estate(
            beds = data["beds"],
            pool = data["pool"],
            people = data["people"],
            weekday_price = data["weekday_price"],
            weekend_price = data["weekend_price"],
            address = data["address"],
            longtitute = data["longtitute"],
            latitute = data["latitute"],
            announcer = data["announcer"],
            phone = data["phone"],
            photo = data["photo"],
            is_published = (data["is_published"] == "true")
        )
        estate.user = user
        estate.estate_type = estate_type
        estate.price_type = price_type
        estate.save()

        for facility in facilities:
            estate.facilities.add(facility)

        available_lang = get_available_lang(translations)
        if available_lang:
            akeys = list(available_lang.keys())[0]
            avalues = list(available_lang.values())[0]
            EstateTranslation = ContentType.objects.get(app_label="api", model="estatetranslation").model_class()
            for key, values in translations.items():
                testate = EstateTranslation(language_code=key, master_id=estate.id)
                if key == akeys:
                    for vkey, vvalue in values.items():
                        if hasattr(testate, vkey):
                            setattr(testate, vkey, vvalue)
                else:
                    for vkey in values.keys():
                        if hasattr(testate, vkey):
                            vvalue = translate_text(avalues[vkey], akeys, key)
                            setattr(testate, vkey, vvalue)
                testate.save()
        
        i = 1
        while True:
            photo = data.get(f"photo{i}", None)
            if not photo:
                print(i)
                break
            estate_photo = EstatePhoto(estate=estate, photo=photo)
            estate_photo.save()
            i += 1
 
        serializer = self.serializer_class(estate)
        return Response(serializer.data, status=status.HTTP_200_OK)
    

    def partial_update(self, request, pk=None, *args, **kwargs):
        estate = Estate.objects.get(id=pk)
        data = request.data

        simple_fields = ["beds", "pool", "people", "weekday_price", "weekend_price", "address", "longtitute", "latitute", "announcer", "phone", "photo"]
        for field in simple_fields:
            if data.get(field, None) and hasattr(estate, field):
                setattr(estate, field, data[field])

        if data.get("is_published", None):
            estate.is_published = (data["is_published"] == "true")
        
        if data.get("user", None):
            user = User.objects.get(id=data["user"])
            estate.user = user
        
        if data.get("estate_type", None):
            estate_type = EstateType.objects.get(id=data["estate_type"])
            estate.estate_type = estate_type
        
        if data.get("price_type", None):
            price_type = Currency.objects.get(id=data["price_type"])
            estate.price_type = price_type
        
        estate.save()

        if data.get("facilities", None):
            facility_ids = list(map(int, data["facilities"][1:-1].split(",")))
            facilities = EstateFacility.objects.filter(id__in=facility_ids)
            estate.facilities.clear()
            for facility in facilities:
                estate.facilities.add(facility)

        if data.get("translations", None):
            translations = json.loads(data["translations"])
            available_lang = get_available_lang(translations)
            if available_lang:
                akeys = list(available_lang.keys())[0]
                avalues = list(available_lang.values())[0]
                EstateTranslation = ContentType.objects.get(app_label="api", model="estatetranslation").model_class()
                for key, values in translations.items():
                    try:
                        testate = EstateTranslation.objects.get(language_code=key, master_id=estate.id)
                        if key == akeys:
                            for vkey, vvalue in values.items():
                                if hasattr(testate, vkey):
                                    setattr(testate, vkey, vvalue)
                        else:
                            for vkey in values.keys():
                                if hasattr(testate, vkey):
                                    vvalue = translate_text(avalues[vkey], akeys, key)
                                    setattr(testate, vkey, vvalue)
                        testate.save()
                    except:
                        testate = EstateTranslation(language_code=key, master_id=estate.id)
                        if key == akeys:
                            for vkey, vvalue in values.items():
                                if hasattr(testate, vkey):
                                    setattr(testate, vkey, vvalue)
                        else:
                            for vkey in values.keys():
                                if hasattr(testate, vkey):
                                    vvalue = translate_text(avalues[vkey], akeys, key)
                                    setattr(testate, vkey, vvalue)
                        testate.save()
        
        i = 1
        while True:
            photo = data.get(f"photo{i}", None)
            if not photo:
                print(i)
                break
            estate_photo = EstatePhoto(estate=estate, photo=photo)
            estate_photo.save()
            i += 1
 
        serializer = self.serializer_class(estate)
        return Response(serializer.data, status=status.HTTP_200_OK)
        

    @action(detail=False, methods=["get"], url_name="top")
    def top(self, request):
        queryset = self.get_queryset().filter(is_top=True)
        estate_type = self.request.query_params.get("estate_type", None)
        if estate_type:
            queryset = queryset.filter(estate_type__id=estate_type)
        serializer = self.serializer_class(queryset, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


    @action(detail=False, methods=["get"], url_name="simple")
    def simple(self, request):
        queryset = self.get_queryset().filter(is_top=False)
        estate_type = self.request.query_params.get("estate_type", None)
        if estate_type:
            queryset = queryset.filter(estate_type__id=estate_type)
        serializer = self.serializer_class(queryset, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    

    @action(detail=True, methods=["get"], url_name="similar")
    def similar(self, request, pk=None):
        estate = Estate.objects.get(id=pk)
        estates = Estate.objects.filter(Q(beds=estate.beds) | Q(pool=estate.pool) | Q(people=estate.people)).exclude(id=estate.id)
        serializer = self.serializer_class(estates, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class MyChatsListView(ListAPIView):
    serializer_class = ChatSerializer
    queryset = Message.objects.all()

    def get(self, request):
        chats = Message.objects.filter(sender=request.user)
        if settings.DEBUG:
            distinct_chat_ids = []
            for chat in chats:
                if chat.id not in distinct_chat_ids:
                    distinct_chat_ids.append(chat.id)
            chats = Message.objects.filter(id__in=distinct_chat_ids)
        else:
            chats = chats.distinct("reciever")
        serializer = self.serializer_class(chats, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class DeleteChatView(DestroyAPIView):
    serializer_class = ChatSerializer
    queryset = Message.objects.all()

    def delete(self, request, *args, **kwargs):
        data = request.query_params
        if not data.get("id", None):
            return Response({
                "detail": "You must provide chat id as 'id' query param. (e.g. ?id=MTA6Nw==)"
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # sender_id, reciever_id = decode_joint_ids(data["id"])
        sender_id, reciever_id = data["id"].split(":")
        messages = Message.objects.filter(sender_id=sender_id, reciever_id=reciever_id)
        if not messages.exists():
            return Response({
                "detail": "Chat does not exist."
            }, status=status.HTTP_400_BAD_REQUEST)

        messages.delete()
        return Response({
            "detail": "Chat has been deleted!"
        }, status=status.HTTP_200_OK)


class MessagesViewSet(ModelViewSet):
    serializer_class = MessageSerializer
    queryset = Message.objects.all()


    def create(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return self.default_response(serializer)
        
        return Response({
            "detail": "You have not provided enough information"
        }, status=status.HTTP_400_BAD_REQUEST)
    

    def update(self, request, *args, **kwargs):
        super().update(request, *args, **kwargs)
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return self.default_response(serializer)

        return Response({
            "detail": "You have not provided enough information"
        }, status=status.HTTP_400_BAD_REQUEST) 
        
    
    def default_response(self, serializer):
        sender = serializer.validated_data["sender"]
        reciever = serializer.validated_data["reciever"]

        messages = Message.objects.filter(sender=sender, reciever=reciever)
        serializer = self.serializer_class(messages, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)




class UserViewSet(ModelViewSet):
    serializer_class = UserSerializer
    queryset = User.objects.all()


class SmsOTP(ViewSet):
    serializer_class = SendOTPSerializer

    @action(detail=False, methods=["post"], url_path="send-message")
    def send_message(self, request):
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            phone = serializer.validated_data["phone"]
            self._send_message(phone)


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