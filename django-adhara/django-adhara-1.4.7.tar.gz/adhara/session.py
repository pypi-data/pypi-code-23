from django.contrib.auth import logout as dj_logout
from .response_utils import ApiResponse
from .utilities import get_user_id_field
from django.conf import settings

AUTH_TOKEN_HEADER = "HTTP_APIKEY"


class Session:
    ADHARA_LOGGED_IN = "adhara_logged_in"
    USING_DB = "using_db"
    USER_ID = "user_id"

    @staticmethod
    def set_variable(request, key, value):
        if 'adhara' not in request.session:
            request.session['adhara'] = {}
        request.session['adhara'][key] = value

    @staticmethod
    def get_variable(request, key):
        # If any changes made here, must also be changed in middleware
        # as the same verification method is re written in middleware
        try:
            return request.session['adhara'][key]
        except KeyError:
            return Session.get_token(request, key)

    @staticmethod
    def set_token(request, key, value):
        if hasattr(request, 'adhara_authorization'):
            request.adhara_authorization = {}
        request.adhara_authorization[key] = value

    @staticmethod
    def get_token(request, key):
        try:
            return request.adhara_authorization[key]
        except AttributeError:
            return None

    @staticmethod
    def get_db(request):
        return Session.get_variable(request, Session.USING_DB)

    @staticmethod
    def get_user_id(request):
        return Session.get_variable(request, Session.USER_ID)

    @staticmethod
    def login(request, user_id=None, db=None):
        Session.set_variable(request, Session.ADHARA_LOGGED_IN, True)
        Session.set_variable(request, Session.USER_ID, user_id)
        Session.set_variable(request, Session.USING_DB, db)

    @staticmethod
    def token_login(request, user_id=None, db=None):
        Session.set_token(request, Session.ADHARA_LOGGED_IN, True)
        Session.set_token(request, Session.USER_ID, user_id)
        Session.set_token(request, Session.USING_DB, db)

    @staticmethod
    def is_logged_in(request):
        return Session.get_variable(request, Session.ADHARA_LOGGED_IN)

    @staticmethod
    def logout(request):
        dj_logout(request)


def is_logged_in(fn):

    def logged_in(request, *args, **kwargs):
        if Session.is_logged_in(request):
            return fn(request, *args, **kwargs)
        else:
            return ApiResponse.error("Not Logged In")
    return logged_in


def get_user_criteria(request):
    return {get_user_id_field(): Session.get_user_id(request)}


def fill_user_id(fn):

    def fnr(request, *args, **kwargs):
        if request.method == "POST":
            request.INPUT_JSON.update(get_user_criteria(request))
        return fn(request, *args, **kwargs)
    return fnr
