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