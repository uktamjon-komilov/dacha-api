from datetime import timedelta, datetime
from PIL import Image
from django.conf import settings
from django.db import models
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from django.contrib.auth import get_user_model
from django.db.models.fields import DateTimeField
from django.utils.translation import gettext as _
from parler.models import TranslatableModel, TranslatedFields

from io import BytesIO
from PIL import Image
from django.core.files import File
from django_resized import ResizedImageField
import requests
import json

from api.image_proccessing.watermarker import add_watermark
from .managers import UserManager
from .utils import *


class User(AbstractBaseUser, PermissionsMixin):
    phone = models.CharField(max_length=25, unique=True,
                             verbose_name=_("Телефонный номер"))
    first_name = models.CharField(
        null=True, blank=True, max_length=50, verbose_name=_("Имя"))
    last_name = models.CharField(
        null=True, blank=True, max_length=50, verbose_name=_("Фамилия"))
    photo = models.FileField(upload_to="user/", default="d.png")
    balance = models.FloatField(default=0.0, verbose_name=_("Баланс"))
    fcm_token = models.TextField(null=True, blank=True)

    is_staff = models.BooleanField(default=True)
    is_admin = models.BooleanField(default=False)

    USERNAME_FIELD = "phone"
    REQUIRED_FIELDS = []

    objects = UserManager()

    class Meta:
        verbose_name = _("Пользователь")
        verbose_name_plural = _("Пользователи")

    def __str__(self):
        return "{} {}".format(self.first_name, self.last_name)


User = get_user_model()


def has_changed(instance, field):
    if not instance.pk:
        return False
    old_value = instance.__class__._default_manager.filter(
        pk=instance.pk).values(field).get()[field]
    return not getattr(instance, field) == old_value


def compress(image, resize=True):
    im = Image.open(image)
    im_io = BytesIO()
    if resize and im.size[0] > 600 or im.size[1] > 500:
        r = 500 / im.size[0]
        width = int(r * im.size[0])
        height = int(r * im.size[1])
        im.resize((width, height))
    im.save(im_io, "PNG", quality=80)
    new_image = File(im_io, name=image.name)
    return new_image


class DateTimeMixin:
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


class Currency(TranslatableModel):
    translations = TranslatedFields(
        title=models.CharField(_("Заголовок"), max_length=200)
    )

    class Meta:
        verbose_name = _("Валюта")
        verbose_name_plural = _("Валюты")

    def __str__(self):
        return self.safe_translation_getter("title", any_language=True)


class EstateType(TranslatableModel):
    translations = TranslatedFields(
        title=models.CharField(_("Заголовок"), max_length=200)
    )
    slug = models.CharField(
        _("Короткое имя"), max_length=255, null=True, blank=True)
    icon = models.FileField(
        _("Значок"), upload_to="icons/", null=True, blank=True)
    priority = models.IntegerField(_("Позиция"), default=1)
    foreground_color = models.CharField(
        _("Цвет"), max_length=8, null=True, blank=True)
    background_color = models.CharField(
        _("Фоновый цвет"), max_length=8, null=True, blank=True)

    class Meta:
        verbose_name = _("Категория")
        verbose_name_plural = _("Категории")

    def __str__(self):
        return self.safe_translation_getter("title", any_language=True)


class EstateFacility(TranslatableModel):
    translations = TranslatedFields(
        title=models.CharField(_("Заголовок"), max_length=200)
    )
    category = models.ManyToManyField(EstateType, related_name="facilities")
    slug = models.SlugField(_("Короткое имя"), max_length=255)

    class Meta:
        verbose_name = _("Удобство")
        verbose_name_plural = _("Удобства")

    def __str__(self):
        return self.safe_translation_getter("title", any_language=True)


class BalanceCharge(models.Model):
    CHARGE_TYPE = [
        ("in", _("Доход")),
        ("out", _("Расходы"))
    ]
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    amount = models.FloatField(verbose_name=_("Количество"))
    date = models.DateTimeField(auto_now_add=True, verbose_name=_("Дата"))
    reason = models.CharField(max_length=255, verbose_name=_("Причина"))
    type = models.CharField(
        max_length=100, choices=CHARGE_TYPE, verbose_name=_("Тип"))
    completed = models.BooleanField(
        default=False, verbose_name=_("Завершенный?"))

    class Meta:
        verbose_name = _("Трансфер")
        verbose_name_plural = _("Трансферы")


class PopularPlace(models.Model):
    title = models.CharField(max_length=255, verbose_name=_("Заголовок"))

    class Meta:
        verbose_name = _("Известное место")
        verbose_name_plural = _("Знаменитые места")


class Estate(TranslatableModel):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name=_("Профиль рекламодателя")
    )

    translations = TranslatedFields(
        title=models.CharField(_("Заголовок"), max_length=200),
        description=models.TextField(verbose_name=_("Описание")),
        region=models.CharField(max_length=255, verbose_name=_("Провинция")),
        district=models.CharField(max_length=255, verbose_name=_("Район"))
    )

    estate_type = models.ForeignKey(
        EstateType,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name=_("Тип недвижимости"),
        related_name="estates"
    )
    photo = ResizedImageField(
        size=[3000, 1800],
        quality=100,
        upload_to="images",
        force_format="jpeg",
        keep_meta=False,
        verbose_name=_("Главное фото")
    )
    thumbnail = ResizedImageField(
        size=[1000, 600],
        quality=100,
        upload_to="images",
        force_format="jpeg",
        null=True,
        keep_meta=False,
        verbose_name=_("Миниатюра")
    )

    beds = models.IntegerField(
        default=5, blank=True, verbose_name=_("Количество кроватей"))
    pool = models.IntegerField(
        default=1, blank=True, verbose_name=_("Количество бассейнов"))
    people = models.IntegerField(
        default=5, blank=True, verbose_name=_("Количество человек"))

    facilities = models.ManyToManyField(
        EstateFacility, blank=True, verbose_name=_("Удобства"))

    price_type = models.ForeignKey(
        Currency,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name=_("Тип цены")
    )
    weekday_price = models.FloatField(
        verbose_name=_("Цены в будние дни")
    )
    weekend_price = models.FloatField(
        verbose_name=_("Цены выходного дня")
    )

    address = models.CharField(max_length=255, verbose_name=_("Адрес"))
    popular_place = models.ForeignKey(
        PopularPlace,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name=_("Знаменитое место")
    )

    longtitute = models.FloatField(
        null=True,
        blank=True,
        verbose_name=_("Долгота")
    )
    latitute = models.FloatField(
        null=True,
        blank=True,
        verbose_name=_("Широта")
    )

    announcer = models.CharField(
        max_length=255,
        verbose_name=_("Рекламодатель")
    )
    phone = models.CharField(max_length=20, verbose_name="Телефонный номер")

    is_published = models.BooleanField(
        default=True,
        verbose_name=_("Это напечатано?")
    )
    expires_in = models.DateField(
        blank=True,
        null=True,
        verbose_name=_("Срок годности")
    )

    is_topbanner = models.BooleanField(
        default=False,
        null=True,
        blank=True,
        verbose_name=_("Топ баннер")
    )
    is_banner = models.BooleanField(
        default=False,
        null=True,
        blank=True,
        verbose_name=_("Баннер")
    )
    is_top = models.BooleanField(
        default=False,
        null=True,
        blank=True,
        verbose_name=_("ТОП объявление")
    )
    is_ads = models.BooleanField(
        default=False,
        null=True,
        blank=True,
        verbose_name=_("Реклама")
    )
    is_ads_plus = models.BooleanField(
        default=False,
        null=True,
        blank=True,
        verbose_name=_("Реклама+")
    )
    is_simple = models.BooleanField(
        default=True,
        null=True,
        blank=True,
        verbose_name=_("Простое объявление")
    )

    rating_average = models.FloatField(default=0.0)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = _("Объявления")
        verbose_name_plural = _("Объявленияи")

    def save(self, *args, **kwargs):
        if has_changed(self, "photo"):
            super(Estate, self).save(*args, **kwargs)
            self.photo = add_watermark(self.photo)
            self.thumbnail = add_watermark(self.thumbnail)

        if not self.id:
            super(Estate, self).save(*args, **kwargs)
            self.photo = add_watermark(self.photo)
            self.thumbnail = add_watermark(self.thumbnail)
            now = datetime.now()
            plan = AdvertisingPlan.objects.get(slug="simple")
            next = now + timedelta(days=plan.days)
            year, month, day = next.year, next.month, next.day
            self.expires_in = "{}-{}-{}".format(year, month, day)

        super(Estate, self).save(*args, **kwargs)

    def get_title(self):
        return self.safe_translation_getter("title", any_language=True)

    def __str__(self):
        return str(self.safe_translation_getter("title", any_language=True))

    @property
    def estate_photo(self):
        return "{}".format(self.photo.url)


class EstatePhoto(models.Model, DateTimeMixin):
    estate = models.ForeignKey(
        Estate,
        on_delete=models.CASCADE,
        related_name="photos",
        null=True,
        blank=True
    )
    photo = ResizedImageField(
        size=[1500, 900],
        quality=100,
        upload_to="images",
        force_format="jpeg"
    )

    class Meta:
        verbose_name = _("Дополнительное изображение")
        verbose_name_plural = _("Дополнительные изображения")

    def save(self, *args, **kwargs):
        if not self.id or has_changed(self, "photo"):
            super(EstatePhoto, self).save(*args, **kwargs)
            self.photo = add_watermark(self.photo)
        super(EstatePhoto, self).save(*args, **kwargs)


class TempPhoto(models.Model, DateTimeMixin):
    photo = models.ImageField()


class EstateBooking(models.Model, DateTimeMixin):
    estate = models.ForeignKey(
        Estate,
        on_delete=models.CASCADE,
        related_name="booked_days",
        verbose_name=_("Объявления")
    )
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="bookings",
        verbose_name=_("Пользователь")
    )
    date = models.DateField(null=True, blank=True)

    def __str__(self):
        return str(self.date)


class EstateRating(models.Model, DateTimeField):
    estate = models.ForeignKey(
        Estate, on_delete=models.CASCADE, related_name="ratings")
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="rating")
    rating = models.IntegerField()

    def __str__(self):
        return "{} - {} - {}".format(self.user, self.estate, self.rating)

    def save(self, *args, **kwargs):
        if self.rating < 0:
            self.rating = 0
        elif self.rating > 5:
            self.rating = 5
        estate = Estate.objects.get(id=self.estate.id)
        estate.rating_average = self.calculate_average_rating()
        estate.save()
        super(EstateRating, self).save(*args, **kwargs)
    

    def calculate_average_rating(self):
        ratings = EstateRating.objects.filter(estate=self.estate).only("rating").values_list("rating", flat=True)
        sum_rating = 0
        for rating in ratings:
            sum_rating += rating

        count = len(ratings)
        if count == 0:
            return 0.0

        return int((sum_rating / count) * 10) / 10


class EstateViews(models.Model, DateTimeMixin):
    estate = models.ForeignKey(
        Estate, on_delete=models.CASCADE, related_name="views")
    ip = models.CharField(max_length=255)


class Wishlist(models.Model):
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="wishlist")
    estate = models.ForeignKey(Estate, on_delete=models.CASCADE)


class StaticPage(TranslatableModel):
    translations = TranslatedFields(
        title=models.CharField(_("Заголовок"), max_length=200),
        content=models.TextField(verbose_name=_("Контент"))
    )

    slug = models.CharField(max_length=255, null=True, blank=True)

    class Meta:
        verbose_name = _("Статическая страница")
        verbose_name_plural = _("Статические страницы")

    def __str__(self):
        return self.safe_translation_getter("title", any_language=True)


class Service(TranslatableModel):
    translations = TranslatedFields(
        title=models.CharField(_("Заголовок"), max_length=200),
        content=models.TextField(verbose_name=_("Контент"))
    )

    slug = models.CharField(max_length=255, null=True,
                            blank=True, verbose_name=_("Слизняк"))
    image = models.FileField(upload_to="images/")
    phone1 = models.CharField(max_length=25, null=True,
                              blank=True, verbose_name=_("Телефон 1"))
    phone2 = models.CharField(max_length=25, null=True,
                              blank=True, verbose_name=_("Телефон 2"))
    email = models.CharField(max_length=200, null=True,
                             blank=True, verbose_name=_("Эл. адрес"))

    class Meta:
        verbose_name = _("Тип сервиса")
        verbose_name_plural = _("Типы сервиса")

    def __str__(self):
        return self.safe_translation_getter("title", any_language=True)


class ServiceItem(TranslatableModel):
    service = models.ForeignKey(
        Service, on_delete=models.SET_NULL, null=True, verbose_name=_("Типы сервиса"))
    image = models.ImageField()
    translations = TranslatedFields(
        title=models.TextField(verbose_name=_("Заголовок")),
    )

    phone = models.CharField(max_length=25, null=True,
                             blank=True, verbose_name=_("Телефонный номер"))

    class Meta:
        verbose_name = _("Услуга")
        verbose_name_plural = _("Услуги")

    def __str__(self):
        return self.safe_translation_getter("title", any_language=True)


class AdvertisingPlan(TranslatableModel):
    translations = TranslatedFields(
        title=models.CharField(_("Заголовок"), max_length=200),
        content=models.TextField(verbose_name=_("Контент"))
    )

    slug = models.CharField(max_length=255, verbose_name=_("Слизняк"))
    price = models.FloatField(verbose_name=_("Цена"))
    days = models.IntegerField(verbose_name=_("Дни"))
    limit = models.BooleanField(default=False, verbose_name=_("Ограничение"))
    limit_count = models.IntegerField(
        default=0, verbose_name=_("Количество ограничений"))

    class Meta:
        verbose_name = _("Тип рекламы")
        verbose_name_plural = _("Типы рекламы")

    def __str__(self):
        return self.safe_translation_getter("title", any_language=True)


class Message(models.Model):
    estate = models.ForeignKey(
        Estate, on_delete=models.SET_NULL, null=True, related_name="related_messages")
    sender = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, related_name="sender_messages")
    receiver = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, related_name="receiver_messages")
    text = models.TextField()
    is_read = models.BooleanField(default=False)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        try:
            self.send_fcm()
        except Exception as e:
            print(e)

    def send_fcm(self):
        token = self.receiver.fcm_token
        print(token)
        if token and len(str(token)) > 0:
            headers = {
                "Content-Type": "application/json",
                "Authorization": "key=" + settings.FCM_SERVICE_TOKEN,
            }
            message = self.text
            if len(message) > 30:
                message = self.text[:30] + "..."
            body = {
                "notification": {
                    "title": str(self.sender),
                    "body": message
                },
                "to": token,
                "priority": "high",
                "data": {
                    "user_id": self.sender.id,
                    "estate": self.estate.id
                },
            }
            response = requests.post(
                "https://fcm.googleapis.com/fcm/send",
                headers=headers,
                data=json.dumps(body)
            )
            print(response.status_code)
            print(response.content)


class Region(TranslatableModel):
    translations = TranslatedFields(
        title=models.CharField(_("Заголовок"), max_length=200),
    )
    priority = models.IntegerField()

    class Meta:
        verbose_name = _("Область")
        verbose_name_plural = _("Области")

    def __str__(self):
        return self.safe_translation_getter("title", any_language=True) or ""

    def __unicode__(self):
        return self.safe_translation_getter("title", any_language=True) or ""


class District(TranslatableModel):
    translations = TranslatedFields(
        title=models.CharField(_("Заголовок"), max_length=200),
    )
    region = models.ForeignKey(
        Region, on_delete=models.CASCADE, related_name="districts")
    priority = models.IntegerField()

    class Meta:
        verbose_name = _("Район")
        verbose_name_plural = _("Районы")

    def __str__(self):
        return self.safe_translation_getter("title", any_language=True) or ""

    def __unicode__(self):
        return self.safe_translation_getter("title", any_language=True) or ""


class Feedback(models.Model):
    phone = models.CharField(max_length=25, verbose_name=_("Телефонный номер"))
    name = models.CharField(max_length=50, verbose_name=_("Заголовок"))
    text = models.TextField(verbose_name=_("Обратная связь"))

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = _("Обратная связь")
        verbose_name_plural = _("Обратная связь")


class StaticTranslation(TranslatableModel):
    key = models.CharField(max_length=255)

    translations = TranslatedFields(
        value=models.TextField(),
    )

    def __str__(self):
        return self.key
