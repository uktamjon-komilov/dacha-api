from rest_framework.serializers import ModelSerializer
from rest_framework.viewsets import ModelViewSet
from rest_framework.generics import ListAPIView

from .models import *
from .serializers import *


class UserViewSet(ModelViewSet):
    serializer_class = UserSerializer
    queryset = User.objects.all()


class EstateViewSet(ModelViewSet):
    serializer_class = EstateSerializer
    queryset = Estate.objects.all()


class EstateFacilityListView(ListAPIView):
    serializer_class = EstateFacilitySerializer
    queryset = EstateFacility.objects.all()

    def get(self, request):
        queryset = self.get_queryset()
        serializer = self.serializer_class(queryset, many=True)
        return Response(serializer.data)