import cv2
import os


def __read(image_name):
    r = cv2.IMREAD_UNCHANGED if image_name.endswith('png') else cv2.IMREAD_COLOR
    return cv2.imread('{}/{}'.format(os.path.dirname(__file__), image_name), r)


def __get_images():
    extensions = ('jpg', 'png')
    return {x.rsplit('.')[0]: __read(x) for x in os.listdir(os.path.dirname(__file__)) if x.endswith(extensions)}


images = __get_images()