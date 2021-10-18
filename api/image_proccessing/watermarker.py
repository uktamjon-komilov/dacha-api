def add_watermark(image):
    from PIL import Image
    import os
    from uuid import uuid4

    background = Image.open(image, "r")
    bg_w, bg_h = background.size

    try:
        watermark = os.path.join(os.getcwd(), "api", "image_proccessing", "cover.png")
        img = Image.open(watermark, "r")
        img_w, img_h = img.size
    except Exception as e:
        print(e)
        print(watermark)
        return ""

    offset = ((bg_w - img_w) // 2, (bg_h - img_h) // 2)
    background.paste(img, offset, img)

    filename = "/images/{}.png".format(uuid4())
    background.save(str(os.getcwd()) + "/media" + filename)

    return filename