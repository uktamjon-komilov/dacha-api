from api.models import Currency, District, Estate, EstateFacility, PopularPlace, Region
from django.db.models import Q
from django.utils import timezone

from django.conf import settings


LANGS = settings.LANGS


def get_estate_queryset(data, queryset=None, not_expired=True):
    if not queryset:
        queryset = Estate.objects.select_related(
            "popular_place").select_related("estate_type").select_related("price_type").prefetch_related("translations").prefetch_related("facilities")
    
    if not_expired:
        queryset = queryset.filter(expires_in__gte=timezone.now())

    place_id = data.get("place", None)
    if place_id:
        place = PopularPlace.objects.filter(id=place_id)
        if place.exists():
            place = place.first()
            queryset = queryset.filter(popular_place=place)

    region = data.get("region", None)
    if region:
        try:
            queryset = queryset.filter(translations__region=region)
        except Exception as e:
            print(e)

    district = data.get("district", None)
    if district:
        print(district)
        try:
            queryset = queryset.filter(translations__district=district)
            print(district)
            print(queryset)
        except Exception as e:
            print(e)

    address = data.get("address", None)
    if address:
        all_ids = []
        terms = address.split()
        if len(terms) > 1:
            for term in terms:
                termed = queryset.filter(
                    Q(address__icontains=term) |
                    Q(translations__region__icontains=term) |
                    Q(translations__district__icontains=term)
                )
                for item in termed:
                    all_ids.append(item.id)

        addressed = queryset.filter(
            Q(address__icontains=address) |
            Q(translations__region__icontains=address) |
            Q(translations__district__icontains=address)
        )
        for item in addressed:
            all_ids.append(item.id)

        queryset = Estate.objects.filter(id__in=all_ids)

    estate_type = data.get("estate_type", None)
    if estate_type and estate_type != "null":
        estate_type = str(estate_type)
        if estate_type.isnumeric():
            queryset = queryset.filter(estate_type__id=estate_type)
        else:
            queryset = queryset.filter(estate_type__slug=estate_type)

    fromDate = data.get("fromDate", None)
    toDate = data.get("toDate", None)
    if fromDate and toDate:
        empty_estate_ids = []
        for item in queryset:
            bookings = item.booked_days.all()
            empty = True
            for booking in bookings:
                from_year, from_month, from_day = list(
                    map(int, fromDate.split("-")))
                to_year, to_month, to_day = list(
                    map(int, toDate.split("-")))
                year, month, day = list(
                    map(int, str(booking.date).split("-")))
                empty = not (
                    (from_year <= year <= to_year)
                    and
                    (from_month <= month <= to_month)
                    and
                    (from_day <= day <= to_day)
                )
            if empty:
                empty_estate_ids.append(item.id)
        queryset = queryset.filter(id__in=empty_estate_ids)

    people = data.get("people", None)
    if people:
        queryset = queryset.filter(people__gte=int(people))

    price = data.get("price", None)
    if price:
        queryset = queryset.filter(
            Q(
                weekday_price__gte=float(price)
            ) |
            Q(
                weekend_price__gte=float(price)
            )
        )

    price_type = data.get("price_type", None)
    if price_type and price_type != "null":
        max_price = data.get("max_price", None)
        if max_price and float(max_price) != 0.0:
            max_price = float(max_price)
        else:
            max_price = 999999999

        min_price = data.get("min_price", None)
        if min_price:
            min_price = float(min_price)
        else:
            min_price = 0.0

        currency = Currency.objects.get(id=price_type)

        currency_related = queryset.filter(price_type=currency)
        currency_related = currency_related.filter(
            weekday_price__lte=max_price,
            weekday_price__gte=min_price
        )

        other_queryset = queryset.exclude(price_type=currency)
        other_currency_title = [
            Currency.objects.language(code)
            .exclude(id=currency.id)
            .first().title.lower()
            for code in LANGS
        ]

        if ("uzs" or "sum" or "so'm") in other_currency_title:
            other_queryset = other_queryset.filter(
                weekday_price__lte=max_price / settings.USD_TO_UZS,
                weekday_price__gte=min_price / settings.USD_TO_UZS
            )
        else:
            other_queryset = other_queryset.filter(
                weekday_price__lte=max_price * settings.USD_TO_UZS,
                weekday_price__gte=min_price * settings.USD_TO_UZS
            )

        joint_ids = [
            *[estate.id for estate in currency_related],
            *[estate.id for estate in other_queryset]
        ]

        queryset = queryset.filter(id__in=joint_ids)

    search_q = data.get("term", None)
    if search_q:
        all_ids = []
        terms = search_q.split()
        if len(terms) > 1:
            for term in terms:
                termed = queryset.filter(
                    Q(translations__title__icontains=term) |
                    Q(translations__description__icontains=term) |
                    Q(address__icontains=term) |
                    Q(translations__region__icontains=term) |
                    Q(translations__district__icontains=term)
                )
                for item in termed:
                    all_ids.append(item.id)

        searcheded = queryset.filter(
            Q(translations__title__icontains=search_q) |
            Q(translations__description__icontains=search_q) |
            Q(address__icontains=search_q) |
            Q(translations__region__icontains=search_q) |
            Q(translations__district__icontains=search_q)
        )
        for item in searcheded:
            all_ids.append(item.id)

        queryset = Estate.objects.filter(id__in=all_ids)

    facility_ids = data.get("facility_ids", None)
    if facility_ids:
        if "," in facility_ids:
            facility_ids = set(map(int, facility_ids.split(",")))
            filtered_ids = []
            for estate in queryset:
                items = estate.facilities.all()
                facilities = set(item.id for item in items)
                if facility_ids.issubset(facilities):
                    filtered_ids.append(estate.id)
            queryset = queryset.filter(id__in=filtered_ids)
        else:
            facility = EstateFacility.objects.filter(id=facility_ids)
            if facility.exists():
                facility = facility.first()
                queryset = queryset.filter(facilities__id__in=[facility.id])

    is_top = data.get("is_top", None)
    if is_top and is_top == "true":
        queryset = queryset.filter(is_top=True)

    is_all = data.get("is_all", None)
    if not is_all:
        is_simple = data.get("is_simple", None)
        if is_simple and is_simple == "true":
            queryset = queryset.filter(is_simple=True, is_top=False)

    is_ads_plus = data.get("is_ads_plus", None)
    if is_ads_plus and is_ads_plus == "true":
        queryset = queryset.filter(is_ads_plus=True)

    ordering = data.get("order_by", None)
    if ordering and ordering == "desc":
        queryset = queryset.order_by("-created_at")
    else:
        queryset = queryset.order_by("created_at")

    sorting = data.get("sorting", None)
    if sorting == "latest":
        queryset = queryset.order_by("-created_at")
    elif sorting == "cheapest":
        queryset = queryset.order_by("weekday_price", "weekend_price")
    elif sorting == "expensive":
        queryset = queryset.order_by("-weekday_price", "-weekend_price")
    else:
        queryset = queryset.order_by("-created_at")

    return queryset.distinct()
