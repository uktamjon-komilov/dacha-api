def check_create_plans():
    from .constants import CONSTANTS
    from .models import AdvertisingPlan
    from django.contrib.contenttypes.models import ContentType
    AdvertisingPlanTranslation = ContentType(
        app_label="api", model="advertisingplantranslation").model_class()
    for _type in CONSTANTS:
        plan = AdvertisingPlan.objects.filter(slug=_type)
        if not plan.exists():
            plan = AdvertisingPlan(slug=_type, price=0.0, days=0)
            plan.save()


def check_create_regions_districts():
    from .models import Region, District
    from django.contrib.contenttypes.models import ContentType
    from django.conf import settings
    import os
    import json
    from .utils import translate_text
    RegionTranslation = ContentType(
        app_label="api", model="regiontranslation").model_class()
    DistrictTranslation = ContentType(
        app_label="api", model="districttranslation").model_class()
    LANGS = settings.LANGS
    DATA = json.load(
        open(os.path.join(settings.BASE_DIR, "api",
             "data", "regions_districts.json"), "r")
    )
    for i, item in enumerate(list(DATA.keys())):
        region = Region.objects.filter(translations__title__icontains=item)
        if not region.exists():
            region = Region(priority=i)
            region.save()
            for lang in LANGS:
                trans = RegionTranslation.objects.filter(
                    master_id=region.id, language_code=lang)
                if not trans.exists():
                    if lang != "uz":
                        title = translate_text(item, "uz", lang)
                    else:
                        title = item
                    RegionTranslation.objects.create(
                        master_id=region.id, language_code=lang, title=title)
            for j, child in enumerate(DATA[item]):
                district = District.objects.filter(
                    translations__title__icontains=child)
                if not district.exists():
                    district = District(priority=j, region=region)
                    district.save()
                    for lang in LANGS:
                        trans = DistrictTranslation.objects.filter(
                            master_id=district.id, language_code=lang)
                        if not trans.exists():
                            if lang != "uz":
                                title = translate_text(child, "uz", lang)
                            else:
                                title = child
                            DistrictTranslation.objects.create(
                                master_id=district.id, language_code=lang, title=title)
