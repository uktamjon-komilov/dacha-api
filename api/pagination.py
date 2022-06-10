from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response
from api import serializers

from api.models import Estate, EstateType
from api.serializers import EstateTypeSerializer


class CustomPagination(PageNumberPagination):
    page_size = 6
    page_size_query_param = "page_size"
    max_page_size = 10000

    def get_paginated_response(self, data, ad=None):
        result = {
            "links": {
                "next": self.get_next_link(),
                "previous": self.get_previous_link()
            },
            "count": self.page.paginator.count,
            "results": data,
            "ad": None
        }

        if ad:
            result["ad"] = ad

        estate_type = self.request.query_params.get("estate_type", None)
        if estate_type:
            try:
                estate_type = EstateType.objects.get(id=estate_type)
                serializer = EstateTypeSerializer(estate_type)
                result["estate_type"] = serializer.data
            except:
                pass

        return Response(result)


class OneItemPagination(PageNumberPagination):
    page_size = 1

    def paginate_queryset(self, queryset, request, view=None):
        page_size = self.get_page_size(request)
        if not page_size:
            return None

        paginator = self.django_paginator_class(queryset, page_size)
        page_number = self.get_page_number(request, paginator)

        try:
            self.page = paginator.page(page_number)
        except:
            return []

        if paginator.num_pages > 1 and self.template is not None:
            # The browsable API should display pagination controls.
            self.display_page_controls = True

        self.request = request
        return list(self.page)
