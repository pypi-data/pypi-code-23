"""
Twisted interface

"""

import os
from twisted.application import internet
from twisted.web import server
from twisted.web.resource import Resource
from twisted.internet import defer
from twisted.web.server import Session
from twisted.web.server import NOT_DONE_YET
from twisted.python.log import ILogObserver, FileLogObserver
from twisted.python.logfile import DailyLogFile

# try to import resources for gzipping (not available in older twisted versions
try:
    from twisted.web.resource import EncodingResourceWrapper
    from twisted.web.server import GzipEncoderFactory
    has_gzip = True
except ImportError:
    print("no gzip encoding available")
    has_gzip = False

from evoke.serve import respond, Dispatcher

# Twisted interface

class EvokeResource(Resource):
    isLeaf = True

    def render_GET(self, request):
        res = respond(request, self.evokeDispatcher)
        # handle deferred results
        if isinstance(res, defer.Deferred):
            res.addCallback(self.render_deferred, request)
            return NOT_DONE_YET
        else:
            return res

    # TODO: distinguish POST and GET
    render_POST = render_GET

    def render_deferred(self, result, request):
        "handle the final result of a deferred chain"
        request.write(result)
        request.finish()


# override Session to give us a longer timeout
class LongSession(Session):
    sessionTimeout = 60 * 60  # in seconds

application = ""

def start(application, apps=[]):
    "start a twisted instance"
    dispatcher = Dispatcher(apps)  # we only want one instance
    # attach the service to its parent application
    resource = EvokeResource()
    resource.evokeDispatcher = dispatcher
    # serve gzipped content if we can..
    if has_gzip:
        resource = EncodingResourceWrapper(resource, [GzipEncoderFactory()])
    # set up our server
    fileServer = server.Site(resource)
    # use long session
    fileServer.sessionFactory = LongSession
    # start the service
    port = int(list(dispatcher.apps.values())[0]['Config'].port)
    evokeService = internet.TCPServer(port, fileServer)
    evokeService.setServiceParent(application)

    # logging
    # create log dir if necessary
    try:
        os.mkdir('logs')
    except OSError:
        pass
    logfile = DailyLogFile("twistd.log", "logs")
    application.setComponent(ILogObserver, FileLogObserver(logfile).emit)
