from connection import *
class WAMP:
    def __init__(self):
        print('Wamp')
        self.connections = [];
        self.connection = Connection('local',handler=self.handleMessage)
        # self.connections[1] = Connection('server',handler=self.handleMessage, host='sccug-330-02.lancs.ac.uk')
        self.connection.connect();
    def run(self):
        pass
    def handleMessage(self, channel, conName, message):
        print('yply')
        print(message['type'])
        return message.data
        pass
