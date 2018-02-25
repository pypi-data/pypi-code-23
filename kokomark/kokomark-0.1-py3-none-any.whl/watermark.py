from PIL import Image
from io import BytesIO


def watermark_image(img_path, watermark_path, img_format='png', scale=2.0):
    # Open images with Pillow
    i = Image.open(img_path)
    w = Image.open(watermark_path)

    # Convert them to RGBA
    image = i.convert('RGBA')
    watermark = w.convert('RGBA')

    # Get sizes of both images
    i_x, i_y = image.size
    w_x, w_y = watermark.size

    # Scale watermark image
    w_scale = max(i_x/(scale*w_x), i_y /(scale*w_y))
    new_size = (int(w_x*w_scale), int(w_y*w_scale))

    # Resize watermark image
    watermark = watermark.resize(new_size, resample=Image.ANTIALIAS)

    # Do some masking stuff
    watermark_mask = watermark.convert("L").point(lambda x: min(x, 25))
    watermark.putalpha(watermark_mask)

    # Paste watermark on original image
    w_x, w_y = watermark.size
    image.paste(watermark, ((i_x-w_x)//2, (i_y-w_y)//2), watermark_mask)

    # Save new file
    newfile = BytesIO()
    image.save(newfile, format=img_format)

    return newfile
