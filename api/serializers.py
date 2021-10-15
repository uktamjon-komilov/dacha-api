from re import search
from django.db.models.query_utils import select_related_descend
from rest_framework import fields, serializers
from rest_framework.serializers import ModelSerializer, Serializer
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.authtoken.models import Token
from rest_framework.response import Response
from parler_rest.serializers import TranslatableModelSerializer, TranslatedFieldsField

from .models import *


class EstateTypeSerializer(TranslatableModelSerializer):
    translations = TranslatedFieldsField(shared_model=EstateType)
    
    class Meta:
        model = EstateType
        fields = ["id", "translations", "slug"]


class CurrencySerializer(TranslatableModelSerializer):
    translations = TranslatedFieldsField(shared_model=Currency)

    class Meta:
        model = Currency
        fields = ["id", "translations"]


class UserSerializer(ModelSerializer):
    class Meta:
        model = User
        fields = ["id", "phone", "password", "first_name", "last_name", "photo", "balance"]
        extra_kwargs = {
            "password": {
                "write_only": True,
            }
        }
    

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
        fields = ["id", "translations"]


class EstateSerializer(TranslatableModelSerializer):
    price_type = CurrencySerializer()

    class Meta:
        model = Estate
        fields = ["id", "price_type"]


class EstateShortSerializer(TranslatableModelSerializer):
    translations = TranslatedFieldsField(shared_model=Estate)
    price_type = CurrencySerializer()

    class Meta:
        model = Estate
        fields = ["id", "photo", "weekday_price", "weekend_price", "price_type", "translations"]


class EstateBannerSerializer(TranslatableModelSerializer):
    estate = EstateShortSerializer()

    class Meta:
        model = EstateBanner
        fields = ["id", "estate"]



class SendOTPSerializer(Serializer):
    phone = serializers.CharField(required=True)
    code = serializers.CharField(required=False)