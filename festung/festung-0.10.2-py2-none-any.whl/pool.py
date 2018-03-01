import requests


class SessionPool(object):
    """Pool to manage connections to festung.

    This pool expects the session connection to be managed externally. It
    doesn't create nor close the TCP connection to festung.

    Args:
        session (requests.Session): A pre-created, externally managed `Session`
            from the requests library.

    Attributes:
        session (requests.Session): The requests' session that this pool use to
            connect to festung.
    """

    def __init__(self, session):
        self.session = session

    def request(self, request):
        resp = self.session.send(request.prepare())
        resp.raise_for_status()
        return resp

    def close(self):
        pass


class NewSessionPool(SessionPool):
    """Same as :class:`SessionPool` but instanciate a new `requests.Session`.

    Args:
        session (NoneType): Only accept None as a session (for polymorphism)
    """
    def __init__(self, session):
        if session is not None:
            raise TypeError("session should be None")
        super(NewSessionPool, self).__init__(requests.Session())

    def close(self):
        super(NewSessionPool, self).close()
        self.session.close()


def get_pool_class(session):
    if session is None:
        return NewSessionPool
    else:
        return SessionPool


def get_pool(session):
    pool_class = get_pool_class(session)
    return pool_class(session)
