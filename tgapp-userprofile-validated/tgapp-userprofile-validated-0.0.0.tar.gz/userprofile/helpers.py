# -*- coding: utf-8 -*-
"""WebHelpers used in userprofile."""


def user_avatar(user):
    if user is None:
        return None

    from .lib import get_user_data
    _, avatar = get_user_data(user)
    return avatar