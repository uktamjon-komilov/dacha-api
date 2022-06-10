def add_watermark(image):
    from PIL import Image
    import os
    from uuid import uuid4
    from django.conf import settings

    filepath = os.path.join(str(os.getcwd()) + "/media/" +
                            str(image).split("/media/")[-1])
    background = Image.open(filepath, "r")
    bg_w, bg_h = background.size
    smaller_length = bg_w if bg_w < bg_h else bg_h

    try:
        watermark = os.path.join(
            os.getcwd(), "api", "image_proccessing", "cover.png")
        img = Image.open(watermark, "r")
        img_w, img_h = (int(smaller_length / 6.5), int(smaller_length / 6))
        img = img.resize((img_w, img_h), Image.ANTIALIAS)
    except Exception as e:
        print(e)
        print(watermark)
        return ""

    offset = ((bg_w - img_w) // 2, (bg_h - img_h) // 2)
    background.paste(img, offset, img)

    try:
        print(background.mode)
        background = background.convert("RGB")
    except Exception as e:
        print("Backgorund: {}".format(e))

    filename = "/images/{}.jpeg".format(uuid4())
    background.save(str(os.getcwd()) + "/media" + filename)

    return filename
