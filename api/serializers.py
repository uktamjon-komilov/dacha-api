from django.db.models import fields
from rest_framework.serializers import ModelSerializer

from .models import Dacha


class DachaSerializer(ModelSerializer):
    class Meta:
        model = Dacha
        fields = "__all__"