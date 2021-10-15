from django.contrib import admin
from parler.admin import TranslatableAdmin
from parler.forms import TranslatableModelForm

from .models import *


class EstateTypeAdmin(TranslatableAdmin):
    form = TranslatableModelForm

    def get_prepopulated_fields(self, request, obj=None):
        return {
            "slug": ("title",)
        }


admin.site.register(EstateFacility, TranslatableAdmin)
admin.site.register(Estate, TranslatableAdmin)
admin.site.register(Currency, TranslatableAdmin)
admin.site.register(EstateType, EstateTypeAdmin)
admin.site.register(EstateBanner, admin.ModelAdmin)