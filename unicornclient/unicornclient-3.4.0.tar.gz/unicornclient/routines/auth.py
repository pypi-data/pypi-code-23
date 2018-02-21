from unicornclient import spy
from unicornclient import routine
from unicornclient import message
from unicornclient import version

class Routine(routine.Routine):
    def __init__(self):
        routine.Routine.__init__(self)

    def process(self, data):
        action = data['action'] if 'action' in data else None

        if action == 'authenticate':
            self.authenticate()
        elif action == 'install':
            secret = data['secret'] if 'secret' in data else None
            spy.save_secret(secret)

    def authenticate(self):
        payload = {
            'type':'auth',
            'secret': spy.load_secret(),
            'version': version.VERSION,
        }
        self.manager.send(message.Message(payload))
