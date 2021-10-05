from rest_framework.serializers import ModelSerializer
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


class CustomAuthToken(ObtainAuthToken):

    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data, context={"request": request})
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data["user"]
        token, created = Token.objects.get_or_create(user=user)
        return Response({
            "token": token.key,
            "user_id": user.pk,
            "phone": user.phone,
            "first_name": user.first_name,
            "last_name": user.last_name,
            "balance": user.balance,
            "photo": user.photo or None,
        })


class EstateFacilitySerializer(TranslatableModelSerializer):
    translations = TranslatedFieldsField(shared_model=EstateFacility)

    class Meta:
        model = EstateFacility
        fields = ["id", "translations"]


class EstateSerializer(ModelSerializer):
    class Meta:
        model = Estate
        fields = "__all__"