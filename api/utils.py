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