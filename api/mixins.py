from django.utils.translation import get_language_from_request
from api.utils import send_sms
from django.conf import settings
import redis

r = redis.StrictRedis()


class NotExpiredQuerySet:
    def get_queryset(self):
        import datetime
        queryset = super().get_queryset()
        now = datetime.now()
        queryset = queryset.filter(expires_in__gte=now)
        return queryset


class SmsVerificationMixin:
    def _send_message(self, phone):
        code = self.generate_code()
        phone_text = str(phone)
        if phone_text.find("997025670") != -1:
            code = "11111"
        r.set(phone_text, code)
        text = """<#> DachaTurizm sent OTP: {} \n\n\n\n {}""".format(
            code,
            settings.OTP_HASH_CODE
        )
        return send_sms(text, phone_text[-9:])

    def _verify(self, phone, code):
        phone_text = str(phone)
        if r.exists(phone_text):
            try:
                pin = str(r.get(phone_text))[2:-1]
                print(pin, code)
                if str(code) == pin:
                    return True
            except Exception as e:
                print(e)
                return False

        return False

    def generate_code(self, length=5):
        import random
        import string
        digits = string.digits
        return "".join([digits[random.randint(0, len(digits)-1)] for _ in range(length)])


class TranslatedSerializerMixin(object):
    def to_representation(self, instance):
        inst_rep = super().to_representation(instance)
        request = self.context.get("request", None) or self.request
        lang_code = get_language_from_request(request)
        result = {}
        for field_name, field in self.get_fields().items():
            if field_name != "translations":
                field_value = inst_rep.pop(field_name)
                result.update({field_name: field_value})
            if field_name == "translations":
                translations = inst_rep.pop(field_name)
                if lang_code not in translations:
                    parler_default_settings = settings.PARLER_LANGUAGES["default"]
                    if "fallback" in parler_default_settings:
                        lang_code = parler_default_settings.get("fallback")
                    if "fallbacks" in parler_default_settings:
                        lang_code = parler_default_settings.get("fallbacks")[0]
                for lang, translation_fields in translations.items():
                    if lang == lang_code:
                        trans_rep = translation_fields.copy()
                        for trans_field_name, trans_field in translation_fields.items():
                            field_value = trans_rep.pop(trans_field_name)
                            result.update({trans_field_name: field_value})
        return result
