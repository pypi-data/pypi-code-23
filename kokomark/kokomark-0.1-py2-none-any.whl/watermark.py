from PIL import Image
from io import BytesIO


def watermark_image(img_path, watermark_path, format='png', scale=2.0):
    i = Image.open(img_path)
    w = Image.open(watermark_path)
    image = i.convert('RGBA')
    watermark = w.convert('RGBA')

    i_x, i_y = image.size
    w_x, w_y = watermark.size

    w_scale = max(i_x/(scale*w_x), i_y /(scale*w_y))
    new_size = (int(w_x*w_scale), int(w_y*w_scale))

    watermark = watermark.resize(new_size, resample=Image.ANTIALIAS)

    watermark_mask = watermark.convert("L").point(lambda x: min(x, 25))
    watermark.putalpha(watermark_mask)

    w_x, w_y = watermark.size

    image.paste(watermark, ((i_x-w_x)//2, (i_y-w_y)//2), watermark_mask)

    newfile = BytesIO()
    image.save(newfile, format='png')

    return newfile
