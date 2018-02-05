from __future__ import print_function
# -*- coding: utf-8 -*-
import requests


def upload_files(api_key, images):
    files = []
    image_number = 0

    try:
        for image in images:
            image_number += 1

            file = ('media{image_number}'.format(image_number=image_number), open(image, 'rb'))
            files.append(file)

        data = {'ACCESS-KEY': '{api_key}'.format(api_key=api_key)}

        r = requests.post('http://52.14.99.66:8010/image_recognition', data=data, files=files)
        return r.text
    except:
        return 'Some fields are incorrect'


def upload_urls(api_key, images):
    try:
        data = {'ACCESS-KEY': '{api_key}'.format(api_key=api_key),
                'URLs': images}

        r = requests.post('http://52.14.99.66:8010/image_recognition', data=data)
        return r.text
    except Exception:
        return 'Some fields are incorrect'


def hello():
    return("Identifai was install correctly")


def say_hello():
    print(hello())
