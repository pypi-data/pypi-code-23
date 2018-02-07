import hmac
import os
from threading import Thread

from .jim.config import ENCODING

HASH_SALT = b'MPwWyL4K7Av5q98f'
APP_PATH = os.path.dirname(os.path.abspath(__file__))


def start_thread(target, name, *args):
    """Launch thread."""
    t = Thread(target=target, args=args)
    t.name = name
    t.daemon = True
    t.start()
    return t


def get_hash(text):
    """Make encrypted text."""
    hashed = hmac.new(HASH_SALT, text.encode(ENCODING))
    return hashed.hexdigest()


def get_square_box(big, small):
    """
    :param big: Bigger side
    :param small: Smaller side
    :return: tuple(x1,x2,y1,y2) if big is width and (y1,y2,x1,x2) if big is height
    """
    b1 = (big - small) / 2
    b2 = b1 + small
    s1 = 0
    s2 = small

    return b1, b2, s1, s2


def get_square_image(image):
    """
    :param image: Loaded image by PIL.image.open()
    :return: Cropped to square image
    """
    img = image.copy()
    width = img.width
    height = img.height
    if width == height:
        return img
    elif width > height:
        x1, x2, y1, y2 = get_square_box(width, height)
    else:
        y1, y2, x1, x2 = get_square_box(height, width)

    return image.crop((x1, y1, x2, y2))


def get_full_path(file, path):
    full_path = os.path.dirname(os.path.abspath(file))
    return os.path.join(full_path, path)