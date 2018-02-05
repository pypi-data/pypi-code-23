from connection import api_get


def get_app_url(app):
    return api_get('/app/url?name={0}'.format(app))
