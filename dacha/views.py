from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import status
from django.conf import settings

class HomeApiView(APIView):

    def url_for(self, path):
        hostname = self.request.META.get("HTTP_HOST")
        if settings.DEBUG:
            return "http://{}/api/{}/".format(hostname, path)
        else:
            return "https://{}/api/{}/".format(hostname, path)


    def get(self, request):
        return Response(
            [
                {
                    "url": self.url_for("estate-types"),
                    "description": "Lists all the estate types (dacha, mehmonxona, ...)",
                },
                {
                    "url": self.url_for("banners/<estate-type-slug>"),
                    "description": "Lists latest banners according to its estate type."
                },
                {
                    "url": self.url_for("facilities"),
                    "description": "Lists all the available estate facilities."
                },
                {
                    "url": self.url_for("currencies"),
                    "description": "Lists available currencies."
                },
                {
                    "url": self.url_for("bookings"),
                    "description": "Endpoints branch for working bookings of estates."
                },
                {
                    "url": self.url_for("ratings"),
                    "description": "With this starting endpoint, you can play aroud with estate ratings."
                }
            ],
            status=status.HTTP_200_OK
        )