#!/usr/bin/env python
# -*- coding: utf-8 -*-

#from notmm.controllers.auth     import AuthCookieController
from notmm.controllers.wsgi import WSGIController
from notmm.utils.django_settings import LazySettings

__all__ = ['make_app']

def make_app(handlerClass=WSGIController, enable_oauth=True):
    
    # init the django settings subsystem
    settings = LazySettings()
    
    wsgi_app = handlerClass(
        settings=settings,
        app_conf={'django.settings_autoload': True,
                  'logging.disabled': False}
    )
    if enable_oauth:
        from wsgi_oauth2 import client
        google_client = client.GoogleClient(
            settings.OAUTH2_CLIENT_ID,
            access_token=settings.OAUTH2_ACCESS_TOKEN,
            scope='email', 
            redirect_url=settings.OAUTH2_REDIRECT_URL,
            login_path="/session_login/")
        wsgi_app = google_client.wsgi_middleware(wsgi_app, secret=settings.SECRET_KEY)
    
    return wsgi_app
