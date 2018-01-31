from twisted.internet.defer import inlineCallbacks
from autobahn.twisted.wamp import ApplicationSession, ApplicationRunner
import json
class Connection(ApplicationSession):
    def __init__(self, name, port=8080, host='localhost',path='/ws', realm="default", channels=[], procedures=[], handler=None):
        ApplicationSession.__init__(self,None)
        self.name = name
        self.host = host
        self.port = port
        self.path = path
        self.realm = realm
        self.channels = [u'gg']
        self.procedures = procedures
        self.handler = handler
        pass
    def connect(self):
        run = ApplicationRunner(
            u"ws://"+self.host+":"+str(self.port)+self.path,
            u""+self.realm
        )
        run.run(self)
    def onJoin(self, details):
        print('Connecting')
        print('s {}'.format(details))
        for chan in self.channels:
            self.subscribe(lambda d : self.onEvent(d,chan),chan)
        self.sendEvent(u'gg',{'type':'wow'})
        pass
    def onEvent(self, msg=None, evt=None):
        print("Got event: {}".format(msg))
        print("Got details: {}".format(evt))
        # msg.chan = chan
        # msg.connection = self.name
        if(self.handler):
            self.handler(evt, self.name, msg)
        pass
    def sendEvent(self, evt, message):
        self.publish(evt, message)
        pass
