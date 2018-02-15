import os, json
from django.http import (HttpResponse,
    HttpResponseNotFound, HttpResponseForbidden)


def get_modules():
    path = os.path.dirname(
        os.path.abspath(__file__)
    )

    names = os.listdir(path = path)

    return list(filter(
        lambda name:
            os.path.isdir(os.path.join(path, name)) and '__' not in name,
        names
    ))


def json_response(data):
    return HttpResponse(
        json.dumps(data, ensure_ascii = False, sort_keys = True),
        content_type = 'application/json')


def make_vector(array, key):
    output = {}

    for item in array:
        output[item[key]] = item

    return output


def get_by_id(the_list, id):
    for item in the_list:
        if item['id'] == id:
            return item

    return None


def access_check(method):
    def wrapper(self, HttpRequest, **kwargs):
        user = HttpRequest.user

        # Анонимные запросы мимо
        if user.id == None:
            return HttpResponseForbidden()

        # Ограничение доступа к информации пользователям
        # с незаполненными профилями
        if not user.profile.is_completed:
            if not (user.is_staff or user.is_superuser):
                return HttpResponseForbidden()

        # Из Lazy в нормальный объект.
        HttpRequest.user = user

        return method(self, HttpRequest, **kwargs)

    return wrapper


def export_to_json(method):
    def wrapper(self, HttpRequest, **kwargs):
        data = method(self, HttpRequest, **kwargs)

        if isinstance(data, HttpResponse):
            return data

        if data == None:
            return HttpResponseNotFound()

        return json_response(data)

    return wrapper
