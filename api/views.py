from rest_framework.viewsets import ModelViewSet

from .models import Dacha
from .serializers import DachaSerializer


class DachaViewSet(ModelViewSet):
    serializer_class = DachaSerializer
    queryset = Dacha.objects.all()