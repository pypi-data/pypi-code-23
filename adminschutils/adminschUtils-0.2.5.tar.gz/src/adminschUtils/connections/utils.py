from ..webserver.webserver import Webserver


def prepare_query(data, wrap=True):
    if wrap:
        data = {'access_token': Webserver().service_token, 'data': data}
    else:
        data['access_token'] = Webserver().service_token
    return data
