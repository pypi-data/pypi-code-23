from pbraw.dispatcher import URLDispatcher

dispatcher = URLDispatcher()

def grab(url):
    return dispatcher.grab_url(url)

import pbraw.handlers
