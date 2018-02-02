# -*- coding: utf-8 -*-
import json

from typing import Any  # noqa

from flask import Response, g


def unauthorized():
    # type: () -> Response
    data = {
        'message': 'Unauthorized',
        'status': 401
    }
    return Response(
        json.dumps(data),
        data['status'],
        {'content-type': 'application/json'}
    )


def save_user(user):
    # type: (Any) -> Any
    '''Save user to the flask global object.

    :param user: currently logged user
    :returns: user
    '''
    g.user = user
    return user
