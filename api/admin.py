from django import forms
from django.contrib import admin
from parler.admin import TranslatableAdmin
from parler.forms import TranslatableModelForm
from django_summernote.admin import SummernoteModelAdmin

from .models import *


admin.site.site_header = "Администрация ДачаТуризм"
admin.site.site_title = "Администрация ДачаТуризм"


class EstateTypeForm(TranslatableModelForm):
    class Meta:
        model = EstateType
        widgets = {
            "foreground_color": forms.TextInput(attrs={"type": "color"}),
            "background_color": forms.TextInput(attrs={"type": "color"}),
        }
        fields = "__all__"


class EstateTypeAdmin(TranslatableAdmin):
    form = EstateTypeForm

    def get_prepopulated_fields(self, request, obj=None):
        return {
            "slug": ("title",)
        }


class EstatePhotoAdmin(admin.StackedInline):
    model = EstatePhoto


class EstateAdmin(TranslatableAdmin):
    inlines = [EstatePhotoAdmin]
    list_display = ["id", "title", "is_simple", "is_top",
                    "is_banner", "is_topbanner", "is_ads", "weekday_price", "weekend_price", "price_type"]
    # list_filter = ["user"]


class StaticPageAdmin(TranslatableAdmin, SummernoteModelAdmin):
    summernote_fields = ("content",)

    def get_prepopulated_fields(self, request, obj=None):
        return {"slug": ("title",)}


class ServiceAdmin(TranslatableAdmin):
    def get_prepopulated_fields(self, request, obj=None):
        return {"slug": ("title",)}


class AdvertisingPlanAdmin(TranslatableAdmin):
    list_display = ["id", "slug", "price", "days"]
    list_display_links = ["id", "slug", "price", "days"]


class PopularPlaceAdmin(admin.ModelAdmin):
    list_display = ["id", "title"]


class UserAdmin(admin.ModelAdmin):
    list_display = ["id", "first_name", "last_name", "phone"]


class EstateFacilityAdmin(TranslatableAdmin):

    def get_prepopulated_fields(self, request, obj=None):
        return {"slug": ("title",)}


class MessageAdmin(admin.ModelAdmin):
    list_display = ["id", "estate", "sender", "receiver"]


class StaticTranslationAdmin(TranslatableAdmin):
    list_display = ["id", "key", "value"]


admin.site.register(EstateFacility, EstateFacilityAdmin)
admin.site.register(Estate, EstateAdmin)
admin.site.register(Currency, TranslatableAdmin)
admin.site.register(EstateType, EstateTypeAdmin)
admin.site.register(EstateBooking, admin.ModelAdmin)
admin.site.register(EstateRating, admin.ModelAdmin)
admin.site.register(EstatePhoto, admin.ModelAdmin)
admin.site.register(Message, MessageAdmin)
admin.site.register(User, admin.ModelAdmin)
admin.site.register(StaticPage, StaticPageAdmin)
admin.site.register(Service, ServiceAdmin)
admin.site.register(ServiceItem, TranslatableAdmin)
admin.site.register(AdvertisingPlan, AdvertisingPlanAdmin)
admin.site.register(Wishlist)
admin.site.register(BalanceCharge)
admin.site.register(Region, TranslatableAdmin)
admin.site.register(District, TranslatableAdmin)
admin.site.register(Feedback)
admin.site.register(TempPhoto)
admin.site.register(StaticTranslation, StaticTranslationAdmin)
admin.site.register(PopularPlace, PopularPlaceAdmin)
# admin.site.register(User, UserAdmin)
