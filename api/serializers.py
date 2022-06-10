from django.db.models import fields
from parler_rest.serializers import TranslatableModelSerializer, TranslatedFieldsField
from rest_framework.decorators import authentication_classes
from rest_framework.serializers import ModelSerializer, Serializer
from rest_framework import serializers

from api.mixins import TranslatedSerializerMixin

from .models import *
from .utils import *


class EstateTypeSerializer(TranslatableModelSerializer):
    translations = TranslatedFieldsField(shared_model=EstateType)

    class Meta:
        model = EstateType
        fields = ["id", "translations", "slug",
                  "foreground_color", "background_color", "icon"]


class CurrencySerializer(TranslatableModelSerializer):
    translations = TranslatedFieldsField(shared_model=Currency)

    class Meta:
        model = Currency
        fields = ["id", "translations"]


class EstateShortSerializer(TranslatableModelSerializer):
    translations = TranslatedFieldsField(shared_model=Estate)
    price_type = CurrencySerializer()
    photo = serializers.SerializerMethodField()

    class Meta:
        model = Estate
        fields = ["id", "photo", "weekday_price",
                  "weekend_price", "price_type", "translations"]

    def get_photo(self, obj):
        return obj.photo.url


class UserSerializer(ModelSerializer):
    estate_ads_count = serializers.SerializerMethodField()
    photo = serializers.FileField(use_url=True, required=False)

    class Meta:
        model = User
        fields = ["id", "phone", "password", "first_name",
                  "last_name", "photo", "fcm_token", "phone", "balance", "estate_ads_count"]
        extra_kwargs = {
            "password": {
                "write_only": True,
            }
        }

    def get_estate_ads_count(self, obj):
        estates = Estate.objects.filter(user=obj)
        return estates.count()

    def create(self, validated_data):
        user = User.objects.create_user(**validated_data)
        return user

    def update(self, instance, validated_data):
        if "password" in validated_data:
            password = validated_data.pop("password")
            instance.set_password(password)

        return super().update(instance, validated_data)


class EstateFacilitySerializer(TranslatableModelSerializer):
    translations = TranslatedFieldsField(shared_model=EstateFacility)

    class Meta:
        model = EstateFacility
        fields = ["id", "translations", "slug"]


class EstateBookingSerializer(serializers.ModelSerializer):
    class Meta:
        model = EstateBooking
        fields = ["id", "date", "estate", "user"]
        extra_kwargs = {
            "estate": {
                "write_only": True
            },
            "user": {
                "write_only": True
            }
        }


class EstateRatingSerializer(serializers.ModelSerializer):
    class Meta:
        model = EstateRating
        fields = ["id", "rating", "estate", "user"]


class EstatePhotoSerializer(serializers.ModelSerializer):
    photo = serializers.FileField(use_url=True)

    class Meta:
        model = EstatePhoto
        fields = ["id", "photo", "estate"]


class TempPhotoSerializer(serializers.ModelSerializer):
    photo = serializers.FileField(use_url=True)

    class Meta:
        model = TempPhoto
        fields = ["id", "photo"]


class EstateViewsSerializer(serializers.ModelSerializer):
    class Meta:
        model = EstateViews
        fields = ["id", "ip", "estate"]


class PopularPlaceSerializer(serializers.ModelSerializer):
    class Meta:
        model = PopularPlace
        fields = ["id", "title"]


class EstateSerializer(TranslatableModelSerializer):
    translations = TranslatedFieldsField(shared_model=Estate)
    price_type = CurrencySerializer()
    booked_days = EstateBookingSerializer(many=True)
    facilities = EstateFacilitySerializer(many=True)
    photos = EstatePhotoSerializer(many=True)
    rating = serializers.SerializerMethodField()
    views = serializers.SerializerMethodField()
    user_ads_count = serializers.SerializerMethodField()
    user_photo = serializers.SerializerMethodField()
    is_liked = serializers.SerializerMethodField()
    popular_place_id = serializers.IntegerField(required=False)
    popular_place_title = serializers.SerializerMethodField()

    class Meta:
        model = Estate
        fields = "__all__"
        extra_kwargs = {
            "popular_place_id": {
                "required": False
            }
        }

    def get_rating(self, obj=None):
        ratings = obj.ratings.all()
        sum_rating = 0
        for rating in ratings:
            sum_rating += rating.rating

        count = ratings.count()
        if count == 0:
            return 0.0

        return int((sum_rating / count) * 10) / 10

    def get_views(self, obj=None):
        return obj.views.count()

    def get_user_ads_count(self, obj=None):
        return Estate.objects.filter(user=obj.user).count()

    def get_user_photo(self, obj=None):
        if obj.user.photo:
            return obj.user.photo.url
        return None

    def get_is_liked(self, obj):
        request = self.context.get("request", None)
        if request and request.user.is_authenticated:
            wishlist = Wishlist.objects.filter(
                user=request.user,
                estate=obj
            )
            return wishlist.exists()
        return False

    def get_popular_place_title(self, obj=None):
        try:
            if obj.popular_place:
                return obj.popular_place.title
        except:
            pass
        return None


class EstateGetSerializer(EstateSerializer):
    announcer = serializers.SerializerMethodField()

    def get_announcer(self, obj=None):
        return str(obj.user)


class EstateAdsPlusSerializer(TranslatableModelSerializer):
    translations = TranslatedFieldsField(shared_model=Estate)
    type_id = serializers.SerializerMethodField()
    slug = serializers.SerializerMethodField()
    price_type = CurrencySerializer()

    class Meta:
        model = Estate
        fields = ["id", "photo", "thumbnail",
                  "translations", "weekday_price", "price_type", "type_id", "slug"]

    def get_type_id(self, obj):
        return obj.estate_type.id

    def get_slug(self, obj):
        return obj.estate_type.slug


class SendOTPSerializer(Serializer):
    phone = serializers.CharField(required=True)
    code = serializers.CharField(required=False)


class WishlistSaveSerializer(Serializer):
    class Meta:
        model = Wishlist
        fields = ["estate", "user"]


class WishlistSerializer(ModelSerializer):
    estate = EstateSerializer(many=False)

    class Meta:
        model = Wishlist
        fields = ["id", "estate", "user"]


class StaticPageSerializer(TranslatableModelSerializer):
    translations = TranslatedFieldsField(shared_model=StaticPage)

    class Meta:
        model = StaticPage
        fields = ["id", "translations", "slug"]


class ServiceSerializer(TranslatableModelSerializer):
    translations = TranslatedFieldsField(shared_model=Service)

    class Meta:
        model = Service
        fields = ["id", "translations", "slug",
                  "image", "phone1", "phone2", "email"]


class ServiceItemSerializer(TranslatableModelSerializer):
    translations = TranslatedFieldsField(shared_model=ServiceItem)

    class Meta:
        model = ServiceItem
        fields = ["id", "translations", "phone", "image"]


class PaymentLinkSerializer(Serializer):
    user = serializers.CharField(required=True)
    amount = serializers.FloatField(required=True)
    return_url = serializers.CharField(required=False)


class AdvertisingPlanSerializer(TranslatableModelSerializer):
    translations = TranslatedFieldsField(shared_model=AdvertisingPlan)
    available = serializers.SerializerMethodField()

    class Meta:
        model = AdvertisingPlan
        fields = ["id", "slug", "price", "days", "translations", "available"]

    def get_available(self, obj):
        if obj.limit:
            estates = Estate.objects.all()
            advertised_estates_count = len(
                list(
                    filter(
                        lambda e: getattr(e, f"is_{obj.slug}"),
                        estates
                    )
                )
            )
            if obj.limit_count != 0 and advertised_estates_count >= obj.limit_count:
                return False
        return True


class MessageSerializer(ModelSerializer):
    class Meta:
        model = Message
        fields = ["estate", "receiver", "text"]


class UserShortSerializer(ModelSerializer):
    class Meta:
        model = User
        fields = ["id", "first_name", "last_name", "phone", "balance", "photo"]


class AllMessageSerializer(ModelSerializer):
    sender = UserShortSerializer(many=False)
    receiver = UserShortSerializer(many=False)
    estate_detail = serializers.SerializerMethodField()
    unread_messages_count = serializers.SerializerMethodField()
    time = serializers.SerializerMethodField()

    class Meta:
        model = Message
        fields = ["id", "sender", "receiver",
                  "text", "estate", "estate_detail", "unread_messages_count", "time"]

    def get_estate_detail(self, obj):
        estate = Estate.objects.get(id=obj.estate.id)
        serialzier = EstateSerializer(estate)
        data = serialzier.data
        return dict(data)

    def get_unread_messages_count(self, obj):
        user = self.context["request"].user

        if obj.receiver == user:
            messages = Message.objects.filter(
                estate=obj.estate,
                sender=obj.sender,
                receiver=user,
                is_read=False
            )
        else:
            messages = Message.objects.filter(
                estate=obj.estate,
                sender=user,
                receiver=obj.receiver,
                is_read=False
            )

        return messages.count()

    def get_time(self, obj):
        return "{}:{}".format(
            str(obj.created_at.hour).zfill(2),
            str(obj.created_at.minute).zfill(2)
        )


class DistrictSerializer(TranslatableModelSerializer):
    translations = TranslatedFieldsField(shared_model=District)

    class Meta:
        model = District
        fields = ["id", "translations"]


class RegionSerializer(TranslatableModelSerializer):
    translations = TranslatedFieldsField(shared_model=Region)
    districts = DistrictSerializer(many=True)

    class Meta:
        model = Region
        fields = ["id", "translations", "districts"]


class BalanceChargeSerializer(serializers.ModelSerializer):
    date = serializers.SerializerMethodField()

    class Meta:
        model = BalanceCharge
        fields = ["id", "amount", "date", "reason", "completed"]

    def get_date(self, obj):
        return "{}-{}-{}".format(
            obj.date.year,
            obj.date.month,
            obj.date.day
        )


class FeedbackSerializer(serializers.ModelSerializer):
    class Meta:
        model = Feedback
        fields = ["id", "phone", "name", "text"]


class StaticTranslationSerializer(
    TranslatedSerializerMixin,
    TranslatableModelSerializer
):
    translations = TranslatedFieldsField(shared_model=StaticTranslation)

    class Meta:
        model = StaticTranslation
        fields = ["id", "key", "translations"]
