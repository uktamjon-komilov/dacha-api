from datetime import timedelta
from django.utils import timezone
from django.db import models
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from django.contrib.auth import get_user_model
from django.db.models.fields import DateTimeField
from django.utils.translation import gettext as _
from parler.models import TranslatableModel, TranslatedFields
from django.db.models.signals import post_save
from django.dispatch import receiver

from .managers import UserManager


class User(AbstractBaseUser, PermissionsMixin):
    phone = models.CharField(max_length=25, unique=True, verbose_name=_("Telefon raqam"))
    first_name = models.CharField(null=True, blank=True, max_length=50, verbose_name=_("Ismi"))
    last_name = models.CharField(null=True, blank=True, max_length=50, verbose_name=_("Familiyasi"))
    photo = models.FileField(null=True, blank=True, upload_to="user/")
    balance = models.FloatField(default=0.0)

    is_staff = models.BooleanField(default=True)
    is_admin = models.BooleanField(default=False)

    USERNAME_FIELD = "phone"
    REQUIRED_FIELDS = []

    objects = UserManager()


    def __str__(self):
        return "{} {}".format(self.first_name, self.last_name)


User = get_user_model()


class DateTimeMixin:
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


class Currency(TranslatableModel):
    translations = TranslatedFields(
        title = models.CharField(_("Nomi"), max_length=200)
    )

    def __str__(self):
        return self.safe_translation_getter("title", any_language=True)


class EstateFacility(TranslatableModel):
    translations = TranslatedFields(
        title = models.CharField(_("Nomi"), max_length=200)
    )

    def __str__(self):
        return self.safe_translation_getter("title", any_language=True)


class EstateType(TranslatableModel):
    translations = TranslatedFields(
        title = models.CharField(_("Nomi"), max_length=200)
    )
    slug = models.CharField(max_length=255, null=True, blank=True)

    def __str__(self):
        return self.safe_translation_getter("title", any_language=True)


class Estate(TranslatableModel, DateTimeMixin):
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name=_("E'lon beruvchi profili"))

    translations = TranslatedFields(
        title = models.CharField(_("Nomi"), max_length=200)
    )
    
    estate_type = models.ForeignKey(EstateType, on_delete=models.SET_NULL, null=True, blank=True, verbose_name=_("Mulk turi"))
    photo = models.FileField(upload_to="images/", verbose_name=_("Asosiy rasm"))

    beds = models.IntegerField(default=0, blank=True)
    pool = models.IntegerField(default=0, blank=True)
    people = models.IntegerField(default=0, blank=True)

    facilities = models.ManyToManyField(EstateFacility, blank=True)

    description = models.TextField(verbose_name=_("Tavsif"))

    price_type = models.ForeignKey(Currency, on_delete=models.SET_NULL, null=True, blank=True)
    weekday_price = models.FloatField(verbose_name=_("Begim kunlaridagi narxi"))
    weekend_price = models.FloatField(verbose_name=_("Dam olish kunlari narxi"))

    region = models.CharField(max_length=50, verbose_name=_("Viloyat"))
    district = models.CharField(max_length=50, verbose_name=_("Tuman"))

    longtitute = models.FloatField(null=True, blank=True, verbose_name=_("Longtitute"))
    latitute = models.FloatField(null=True, blank=True, verbose_name=_("Latitute"))

    announcer = models.CharField(max_length=255, verbose_name=_("E'lon beruvchi"))
    phone = models.CharField(max_length=20, verbose_name="Telefon raqam")

    is_published = models.BooleanField(default=True, verbose_name=_("Chop etilishi"))
    expires_in = models.DateTimeField(blank=True, null=True)


    # def save(self, *args, **kwargs):
    #     if not self.id:
    #         self.expires_in = self.created_at + timedelta(days=30)
    #     super(Estate, self).save(*args, **kwargs)

    def get_title(self):
        return self.safe_translation_getter("title", any_language=True)



class EstatePhoto(models.Model, DateTimeMixin):
    estate = models.ForeignKey(Estate, on_delete=models.CASCADE, related_name="photos")
    photo = models.FileField(upload_to="images/")


class EstateBanner(models.Model, DateTimeMixin):
    days = models.IntegerField(default=30)
    estate = models.ForeignKey(Estate, on_delete=models.CASCADE)
    expires_in = models.DateTimeField(blank=True, null=True)

    def save(self, *args, **kwargs):
        # super(EstateBanner, self).save(*args, **kwargs)
        # if not self.expires_in:
        #     print(self.created_at)
        #     self.expires_in = self.created_at + timezone.timedelta(days=30)
        super(EstateBanner, self).save(*args, **kwargs)