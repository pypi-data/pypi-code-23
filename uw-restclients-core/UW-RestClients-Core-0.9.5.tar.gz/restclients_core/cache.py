class NoCache(object):
    """
    A cache implementation that never caches.
    """
    def getCache(self, service, url, headers):
        return None

    def processResponse(self, service, url, response):
        pass
