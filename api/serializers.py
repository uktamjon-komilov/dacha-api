from re import search
from django.db.models.query_utils import select_related_descend
from rest_framework import serializers
from rest_framework.serializers import ModelSerializer, Serializer
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.authtoken.models import Token
from rest_framework.response import Response
from parler_rest.serializers import TranslatableModelSerializer, TranslatedFieldsField

from .models import *


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


class EstateSerializer(ModelSerializer):
    class Meta:
        model = Estate
        fields = "__all__"


class SendOTPSerializer(Serializer):
    phone = serializers.CharField(required=True)
    code = serializers.CharField(required=False)