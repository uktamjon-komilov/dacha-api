def translate_text(text, from_lang, to_lang):
    from googletrans import Translator
    translator = Translator()
    result = translator.translate(str(text), src=from_lang, dest=to_lang)
    return result.text


def get_available_lang(translations):
    active = None
    for lang, values in translations.items():
        empty = False
        for key, value in values.items():
            if value.strip() == "":
                empty = True
                break

        if not empty:
            active = {lang: values}

    return active


def encode_joint_ids(sender_id, reciever_id):
    import base64
    text = f"{sender_id * 5}:{reciever_id * 7}"
    return base64.b64encode(text.encode("ascii"))


def decode_joint_ids(id):
    import base64
    text = base64.b64decode(id)
    result = list(map(int, str(text)[2:-1].split(":")))
    return (result[0] // 5, result[1] // 7)


def smart_truncate(content, length=100, suffix="..."):
    if len(content) <= length:
        return content
    else:
        return " ".join(content[:length+1].split(" ")[0:-1]) + suffix


def send_sms(text, phone):
    import requests as r
    from django.conf import settings
    url = "http://91.204.239.44/broker-api/send/"
    data = {
        "messages":
        [
            {
                "recipient": "998{}".format(phone),
                "message-id": "abc000000001",
                "sms": {
                    "originator": "3700",
                    "content": {
                        "text": str(text)
                    }
                }
            }
        ]
    }
    res = r.post(
        url,
        headers={
            "Content-type": "application/json",
            "Authorization": "Basic {}".format(settings.SMS_AUTH_TOKEN)
        },
        json=data
    )
    if res.status_code == 200:
        return True

    return False


def get_file_path(instance, filename):
    import uuid
    import os
    ext = filename.split(".")[-1]
    filename = "%s.%s" % (uuid.uuid4(), ext)
    return os.path.join("images/", filename)


def clear_date(date):
    return str(date).replace('"', "").replace("'", "")


def charge_user(user_id, amount, reason, _type):
    from django.db import transaction
    from api.models import User, BalanceCharge
    user = User.objects.get(id=user_id)
    if not user or user.balance < amount:
        return False

    with transaction.atomic():
        user.balance -= amount
        user.save()
        charge = BalanceCharge(
            user=user,
            amount=amount,
            reason=reason,
            type=_type,
            completed=True
        )
        charge.save()
        return charge


def roundup(x):
    import math
    return int(math.ceil(x / 100.0)) * 100


def rounddown(x):
    import math
    return int(math.floor(x / 100.0)) * 100
