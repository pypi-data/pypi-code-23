# -*- coding: utf-8 -*-

"""WebHelpers used in tgapp-categories."""


def images_with_image_name(category, image_name):
    return [c for c in category.images if c.image_name == image_name]


def content_of_first_small_image(category):
    try:
        print(images_with_image_name(category, 'image_small'))
        return images_with_image_name(category, 'image_small')[0].content
    except IndexError:
        return None


def content_of_first_big_image(category):
    try:
        return images_with_image_name(category, 'image_big')[0].content
    except IndexError:
        return None


from tgext.pluggable.utils import instance_primary_key