from django.utils import timezone
from rest_framework.response import Response
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes, renderer_classes, authentication_classes
from rest_framework.renderers import JSONRenderer
from rest_framework_simplejwt.authentication import JWTAuthentication
from api import tasks
from api.models import AdvertisingPlan, Currency, Estate
from api.pagination import CustomPagination, OneItemPagination
from api.utils import charge_user, roundup
from django.contrib.auth import get_user_model
from django.conf import settings

from .serializers import EstateAdsPlusSerializer, EstateGetSerializer, EstateSerializer
from .filters import get_estate_queryset


LANGS = settings.LANGS


User = get_user_model()


@api_view(("GET",))
@renderer_classes((JSONRenderer,))
def top_estates(request, slug):
    queryset = get_estate_queryset(request.GET).filter(is_top=True)
    if queryset.count() == 0:
        queryset = get_estate_queryset(request.GET)
    if slug:
        queryset = queryset.filter(estate_type__slug=slug)
    paginator = CustomPagination()
    queryset = paginator.paginate_queryset(queryset, request)
    serializer = EstateSerializer(
        queryset,
        many=True,
        context={
            "request": request
        }
    )
    return paginator.get_paginated_response(serializer.data)


@api_view(("GET",))
@renderer_classes((JSONRenderer,))
def all_estates(request, slug):
    queryset = get_estate_queryset(request.GET)
    ad_queryset = Estate.objects.filter(
        is_ads_plus=True,
        expires_in__gte=timezone.now()
    )
    if slug:
        queryset = queryset.filter(estate_type__slug=slug)
        ad_queryset = ad_queryset.filter(estate_type__slug=slug)
    paginator = CustomPagination()
    queryset = paginator.paginate_queryset(queryset, request)
    serializer = EstateSerializer(
        queryset,
        many=True,
        context={
            "request": request
        }
    )
    one_item_paginator = OneItemPagination()
    ad_queryset = one_item_paginator.paginate_queryset(
        ad_queryset,
        request
    )
    if len(ad_queryset) > 0:
        ad_serializer = EstateAdsPlusSerializer(
            ad_queryset[0],
            many=False,
            context={
                "request": request
            }
        )
        return paginator.get_paginated_response(serializer.data, ad_serializer.data)
    return paginator.get_paginated_response(serializer.data)


@api_view(("GET",))
@renderer_classes((JSONRenderer,))
def last_estate(request):
    estates = get_estate_queryset(request.GET).filter(
        user=request.user).order_by("-id")
    serializer = EstateSerializer(
        estates.first(),
        context={"request": request}
    )
    return Response(serializer.data, status=status.HTTP_200_OK)


@api_view(("GET",))
@renderer_classes((JSONRenderer,))
def simple_estates(request, slug):
    queryset = get_estate_queryset(request.GET).filter(
        is_top=False,
        is_simple=True
    )
    ad_queryset = Estate.objects.filter(
        is_ads_plus=True,
        expires_in__gte=timezone.now()
    )
    if slug:
        queryset = queryset.filter(estate_type__slug=slug)
        ad_queryset = ad_queryset.filter(estate_type__slug=slug)
    paginator = CustomPagination()
    queryset = paginator.paginate_queryset(queryset, request)
    serializer = EstateGetSerializer(
        queryset,
        many=True,
        context={
            "request": request
        }
    )
    one_item_paginator = OneItemPagination()
    ad_queryset = one_item_paginator.paginate_queryset(
        ad_queryset,
        request
    )
    if len(ad_queryset) > 0:
        ad_serializer = EstateAdsPlusSerializer(
            ad_queryset[0],
            many=False,
            context={
                "request": request
            }
        )
        return paginator.get_paginated_response(serializer.data, ad_serializer.data)
    return paginator.get_paginated_response(serializer.data)


@api_view(("GET",))
@renderer_classes((JSONRenderer,))
def single_estate(request, slug, id):
    queryset = get_estate_queryset(request.GET)
    if slug:
        queryset = queryset.filter(estate_type__slug=slug, id=id)
    if queryset.exists():
        estate = queryset.first()
        serializer = EstateGetSerializer(estate, context={"request": request})
        return Response(serializer.data, status=status.HTTP_200_OK)
    return Response({
        "detail": "There is something wrong with this request."
    }, status=status.HTTP_400_BAD_REQUEST)


@api_view(("GET",))
@authentication_classes((JWTAuthentication,))
@renderer_classes((JSONRenderer,))
def myestates_by_type(request, slug):
    estates = get_estate_queryset(request.GET, not_expired=False).filter(
        user=request.user,
        estate_type__slug=slug
    )
    serializer = EstateGetSerializer(estates, many=True)
    return Response(serializer.data, status=status.HTTP_200_OK)


@api_view(("GET",))
@authentication_classes((JWTAuthentication,))
@renderer_classes((JSONRenderer,))
def myestates(request):
    estates = get_estate_queryset(request.GET, not_expired=False).filter(
        user=request.user).order_by("-id")
    serializer = EstateGetSerializer(
        estates,
        many=True,
        context={"request": request}
    )
    return Response(serializer.data, status=status.HTTP_200_OK)


@api_view(("PATCH", "GET"))
@authentication_classes((JWTAuthentication,))
@renderer_classes((JSONRenderer,))
def estate_partial_update(request, pk=None):
    print(request.method)
    if request.method == "GET":
        try:
            estate = Estate.objects.get(id=pk)
        except:
            return Response({}, status=status.HTTP_200_OK)

        serializer = EstateGetSerializer(estate, context={"request": request})
        return Response(serializer.data, status=status.HTTP_200_OK)

    data = {**request.data}
    for key in data.keys():
        data[key] = data[key][0]
    if not data.get("user", None):
        data["user"] = request.user.id
    tasks.update_estate(pk, data)
    return Response({}, status=status.HTTP_200_OK)


@api_view(("POST",))
@authentication_classes((JWTAuthentication,))
@renderer_classes((JSONRenderer,))
def advertise(request, slug, id):
    from api.constants import CONSTANTS, BANNER
    from datetime import datetime, timedelta
    plan = AdvertisingPlan.objects.get(slug=slug)
    print(plan)
    estates = Estate.objects.all()
    advertised_estates_count = len(
        list(
            filter(
                lambda e: getattr(e, f"is_{plan.slug}"),
                estates
            )
        )
    )
    if plan.limit:
        if plan.limit_count != 0 and advertised_estates_count >= plan.limit_count:
            return Response(status=status.HTTP_400_BAD_REQUEST)

    estate = Estate.objects.get(id=id)
    next = datetime.now() + timedelta(days=plan.days)
    estate.expires_in = "{}-{}-{}".format(next.year, next.month, next.day)
    charge = charge_user(request.user.id, plan.price, plan.slug, "out")
    if charge:
        for _type in CONSTANTS:
            print(_type, _type == plan.slug)
            print(getattr(estate, "is_{}".format(plan.slug)))
            if _type == plan.slug:
                setattr(estate, "is_{}".format(_type), True)
                break

        if plan.slug == "simple":
            estate.is_simple = True
        else:
            estate.is_simple = False
        print(getattr(estate, "is_{}".format(plan.slug)))
        estate.save()
        serializer = EstateSerializer(estate, context={"request": request})
        return Response(serializer.data, status=status.HTTP_200_OK)

    return Response(status=status.HTTP_400_BAD_REQUEST)


@api_view(("POST",))
@authentication_classes((JWTAuthentication,))
@renderer_classes((JSONRenderer,))
def renew_password(request):
    data = request.data
    old_password = data.get("old_password", None)
    if not old_password:
        return Response({"status": False, "detail": "OLD_PASSWORD_NOT_PROVIDED"})
    new_password = data.get("new_password", None)
    if not new_password:
        return Response({"status": False, "detail": "NEW_PASSWORD_NOT_PROVIDED"})
    user = User.objects.get(id=request.user.id)
    if not user.check_password(old_password):
        return Response({"status": False, "detail": "OLD_PASSWORD_WRONG"})
    user.set_password(str(new_password))
    user.save()
    return Response({"status": True, "detail": "SUCCESS"})


@api_view(("POST",))
@authentication_classes(tuple())
@permission_classes(tuple())
@renderer_classes((JSONRenderer,))
def get_extrimal_prices(request):
    data = request.data
    price_type_id = data.get("price_type", None)
    if not price_type_id:
        return Response({"status": False, "detail": "PRICE_TYPE_NOT_PROVIDED"})

    estates = Estate.objects.all()

    category = data.get("category", None)
    if category:
        estates = estates.filter(estate_type__id=category)

    if not estates.exists():
        return Response({
            "max": 1000.0,
            "min": 0.0,
            "divisions": 200
        })

    chosen_currency = Currency.objects.get(id=price_type_id)
    other_currency = Currency.objects.exclude(id=price_type_id)

    currency_related_estates = estates.filter(price_type=chosen_currency)
    max_prices = []
    min_prices = []
    max_prices.append(
        currency_related_estates.order_by(
            "-weekday_price"
        ).first().weekday_price
    )
    max_prices.append(
        currency_related_estates.order_by(
            "-weekend_price"
        ).first().weekend_price
    )
    min_prices.append(
        currency_related_estates.order_by(
            "weekday_price"
        ).first().weekday_price
    )
    min_prices.append(
        currency_related_estates.order_by(
            "weekend_price"
        ).first().weekend_price
    )

    other_currency_estates = estates.filter(
        price_type=other_currency.first()
    )
    other_max_prices = []
    other_min_prices = []
    other_max_prices.append(
        other_currency_estates.order_by(
            "-weekday_price"
        ).first().weekday_price
    )
    other_max_prices.append(
        other_currency_estates.order_by(
            "-weekend_price"
        ).first().weekend_price
    )
    other_min_prices.append(
        other_currency_estates.order_by(
            "weekday_price"
        ).first().weekday_price
    )
    other_min_prices.append(
        other_currency_estates.order_by(
            "weekend_price"
        ).first().weekend_price
    )

    other_currency_title = [
        other_currency.language(code).first().title.lower()
        for code in LANGS
    ]
    divider = 5
    if ("uzs" or "sum" or "so'm") in other_currency_title:
        other_max_prices = list(
            map(lambda price: price / settings.USD_TO_UZS, other_max_prices))
        other_min_prices = list(
            map(lambda price: price / settings.USD_TO_UZS, other_min_prices))
    else:
        other_max_prices = list(
            map(lambda price: price * settings.USD_TO_UZS, other_max_prices))
        other_min_prices = list(
            map(lambda price: price * settings.USD_TO_UZS, other_min_prices))
        divider = 100000

    max_prices = [*max_prices, *other_max_prices]
    min_prices = [*min_prices, *other_min_prices]

    max_price = roundup(max(max_prices))
    min_price = roundup(max(min_prices))

    return Response({
        "max": float(max_price),
        "min": float(min_price),
        "divisions": (max_price - min_price) // divider
    })
