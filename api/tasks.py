from celery import shared_task
from django.contrib.contenttypes.models import ContentType
import json

from .models import *
from .utils import *

from base64 import b64decode
from django.core.files.base import ContentFile
import uuid
# from PIL import Image
# from io import BytesIO
# from base64 import b64decode


# def save_image_from_base64_string(imagestr, path):
#     imagestr = 'data:image/png;base64,...base 64 stuff....'
#     im = Image.open(BytesIO(b64decode(imagestr.split(',')[1])))
#     im.save("image.png")


@shared_task
def create_estate(data):
    from pprint import pprint
    pprint(data)
    if isinstance(data["facilities"], str):
        facility_ids = list(map(int, data["facilities"][1:-1].split(",")))
    else:
        facility_ids = data["facilities"]

    if isinstance(data["translations"], list):
        translations = json.loads(data["translations"][0])
    else:
        translations = json.loads(data["translations"])

    if data.get("user", None):
        user = User.objects.get(id=data["user"])

    estate_type = EstateType.objects.get(id=data["estate_type"])
    price_type = Currency.objects.get(id=data["price_type"])
    facilities = EstateFacility.objects.filter(id__in=facility_ids)

    estate = Estate(
        beds=data["beds"],
        pool=data["pool"],
        people=data["people"],
        weekday_price=data["weekday_price"],
        weekend_price=data["weekend_price"],
        address=data["address"],
        longtitute=data["longtitute"],
        latitute=data["latitute"],
        announcer=data["announcer"],
        phone=data["phone"],
        is_published=(data["is_published"] == "true")
    )

    if data.get("photo", None):
        try:
            temp_photo_id = int(data["photo"])
            temp_photo = TempPhoto.objects.filter(id=temp_photo_id)
            if temp_photo.exists():
                estate.photo = temp_photo.first().photo
                estate.thumbnail = temp_photo.first().photo
        except:
            estate.photo = data["photo"]
            estate.thumbnail = data["photo"]
    estate.user = user
    estate.estate_type = estate_type
    estate.price_type = price_type
    estate.save()

    popular_place_id = data.get("popular_place_id", None)
    popular_place = PopularPlace.objects.filter(id=popular_place_id)
    if popular_place.exists():
        popular_place = popular_place.first()
        estate.popular_place = popular_place
        estate.save()

    try:
        temp_photo.delete()
    except:
        pass

    for facility in facilities:
        estate.facilities.add(facility)

    available_lang = get_available_lang(translations)
    if available_lang:
        akeys = list(available_lang.keys())[0]
        avalues = list(available_lang.values())[0]
        EstateTranslation = ContentType.objects.get(
            app_label="api",
            model="estatetranslation"
        ).model_class()
        for key, values in translations.items():
            testate = EstateTranslation(
                language_code=key, master_id=estate.id
            )
            if key == akeys:
                for vkey, vvalue in values.items():
                    if hasattr(testate, vkey):
                        setattr(testate, vkey, vvalue)
            else:
                for vkey in values.keys():
                    if hasattr(testate, vkey):
                        if vkey != "title":
                            vvalue = translate_text(avalues[vkey], akeys, key)
                        else:
                            vvalue = avalues[vkey]
                        setattr(testate, vkey, vvalue)
            testate.save()

    booked_days = data.get("booked_days", None)
    if booked_days:
        dates = list(filter(lambda date: len(date) >
                     5, booked_days[1:-1].split(",")))
        booked_days = list(map(lambda x: clear_date(x.strip()), dates))
        for date in booked_days:
            try:
                print(date)
                EstateBooking.objects.create(
                    estate=estate,
                    user=user,
                    date=str(date)
                )
            except Exception as e:
                print(e)

    i = 1
    while True:
        photo = data.get(f"photo{i}", None)
        if not photo:
            print(i)
            break
        estate_photo = EstatePhoto(estate=estate)
        estate_photo.photo = photo
        estate_photo.save()
        i += 1

    photos = data.get("photos", None)
    if photos:
        # try:
        #     old_photos = EstatePhoto.objects.filter(estate=estate)
        #     old_photos.delete()
        # except:
        #     pass
        photo_ids = str(photos[1:-1]).split(",")
        for _id in photo_ids:
            try:
                estate_photo = EstatePhoto.objects.get(id=_id)
                if not estate_photo.estate:
                    estate_photo.estate = estate
                    estate_photo.save()
            except:
                pass


@shared_task
def update_estate(id, data):
    estate = Estate.objects.get(id=id)

    from pprint import pprint
    pprint(data)

    simple_fields = ["beds", "pool", "people", "weekday_price", "weekend_price",
                     "address", "longtitute", "latitute", "announcer", "phone"]
    for field in simple_fields:
        if data.get(field, None) and hasattr(estate, field):
            setattr(estate, field, data[field])

    # try:
    #     photo = data.get("photo", None)
    #     if photo and not str(photo).startswith("http"):
    #         estate.photo = photo
    # except Exception as e:
    #     print(e)

    if data.get("photo", None):
        try:
            temp_photo_id = int(data["photo"])
            temp_photo = TempPhoto.objects.filter(id=temp_photo_id)
            if temp_photo.exists():
                estate.photo = temp_photo.first().photo
                estate.thumbnail = temp_photo.first().photo
        except:
            estate.photo = data["photo"]
            estate.thumbnail = data["photo"]

    if data.get("is_published", None):
        estate.is_published = (data["is_published"] == "true")

    if data.get("user", None):
        user = User.objects.get(id=data["user"])
        estate.user = user

    if data.get("estate_type", None):
        estate_type = EstateType.objects.get(id=data["estate_type"])
        estate.estate_type = estate_type

    if data.get("price_type", None):
        price_type = Currency.objects.get(id=data["price_type"])
        estate.price_type = price_type

    popular_place_id = data.get("popular_place_id", None)
    popular_place = PopularPlace.objects.filter(id=popular_place_id)
    if popular_place.exists():
        popular_place = popular_place.first()
        estate.popular_place = popular_place
        estate.save()

    estate.save()

    if data.get("facilities", None):
        if isinstance(data["facilities"], str):
            facility_ids = list(map(int, data["facilities"][1:-1].split(",")))
        facilities = EstateFacility.objects.filter(id__in=facility_ids)
        estate.facilities.clear()
        for facility in facilities:
            estate.facilities.add(facility)

    if data.get("translations", None):
        translations = json.loads(data["translations"])
        available_lang = get_available_lang(translations)
        if available_lang:
            akeys = list(available_lang.keys())[0]
            avalues = list(available_lang.values())[0]
            EstateTranslation = ContentType.objects.get(
                app_label="api", model="estatetranslation").model_class()
            for key, values in translations.items():
                try:
                    testate = EstateTranslation.objects.get(
                        language_code=key, master_id=estate.id)
                    if key == akeys:
                        for vkey, vvalue in values.items():
                            if hasattr(testate, vkey):
                                setattr(testate, vkey, vvalue)
                    else:
                        for vkey in values.keys():
                            if hasattr(testate, vkey):
                                if vkey != "title":
                                    vvalue = translate_text(
                                        avalues[vkey], akeys, key)
                                else:
                                    vvalue = avalues[vkey]
                                setattr(testate, vkey, vvalue)
                    testate.save()
                except:
                    testate = EstateTranslation(
                        language_code=key, master_id=estate.id)
                    if key == akeys:
                        for vkey, vvalue in values.items():
                            if hasattr(testate, vkey):
                                setattr(testate, vkey, vvalue)
                    else:
                        for vkey in values.keys():
                            if hasattr(testate, vkey):
                                if vkey != "title":
                                    vvalue = translate_text(
                                        avalues[vkey], akeys, key)
                                else:
                                    vvalue = avalues[vkey]
                                setattr(testate, vkey, vvalue)
                    testate.save()

    booked_days = data.get("booked_days", None)
    if booked_days:
        dates = booked_days[1:-1].split(",")
        dates = list(filter(lambda date: len(date) >
                     5, booked_days[1:-1].split(",")))
        print(dates)
        booked_days = list(map(lambda x: clear_date(x.strip()), dates))
        booking_ids = []
        for date in booked_days:
            try:
                booking = EstateBooking.objects.filter(
                    estate=estate, date=date)
                if booking.exists():
                    booking = booking.first()
                else:
                    booking = EstateBooking.objects.create(
                        estate=estate, user=user, date=str(date)
                    )
                booking_ids.append(booking.id)
            except Exception as e:
                print(e)

        bookings = EstateBooking.objects.filter(
            estate=estate).exclude(id__in=booking_ids)
        bookings.delete()

    try:
        i = 1
        while True:
            photo = data.get(f"photo{i}", None)
            if not photo or str(photo).startswith("http"):
                break
            estate_photo = EstatePhoto(estate=estate)
            print(photo)
            estate_photo.photo = photo
            estate_photo.save()
            i += 1
    except Exception as e:
        print(e)

    photos = data.get("photos", None)
    if photos:
        # try:
        #     old_photos = EstatePhoto.objects.filter(estate=estate)
        #     old_photos.delete()
        # except:
        #     pass
        photo_ids = str(photos[1:-1]).split(",")
        for _id in photo_ids:
            try:
                estate_photo = EstatePhoto.objects.get(id=_id)
                estate_photo.estate = estate
                estate_photo.save()
            except Exception as e:
                print(e)
