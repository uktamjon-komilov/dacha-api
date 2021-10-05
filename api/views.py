from rest_framework.serializers import ModelSerializer
from rest_framework.viewsets import ModelViewSet

from .models import *
from .serializers import *


# class DachaViewSet(ModelViewSet):
#     serializer_class = DachaSerializer
#     queryset = Dacha.objects.all()


class UserViewSet(ModelViewSet):
    serializer_class = UserSerializer
    queryset = User.objects.all()