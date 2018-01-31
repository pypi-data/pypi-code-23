import select
import socket
from .helpers import console, jim
from .db.server_repo import ServerRepo
from .log.server import server_logger

WORKERS = 5


class Dispatcher:
    def __init__(self, sock, handler):
        self.__sock = sock
        self.client_name = None
        self.__logger = server_logger
        self.__handler = handler
        self.__in = []
        self.__out = []

        self.status = False

        # presence
        self.receive()
        self.process()
        self.release()

    def receive(self):
        parcels = jim.receive(self.__sock, self.__logger)
        if not parcels:
            raise Exception
        self.__in.extend(parcels)

    def process(self):
        while len(self.__in):
            request = self.__in.pop()
            request.client_name = self.client_name
            response = self.__handler.run_action(request)
            if request.action == 'presence' and response.response == 200:
                self.client_name = request.user_account_name
                self.status = True
            if isinstance(response, jim.Message):
                self.__out.append(response)
            else:
                self.__out.extend(response)

    def send(self, request):
        self.__logger.info('Send {}.'.format(str(request)))
        self.__sock.send(bytes(request))

    def release(self, names=None):
        while len(self.__out):
            response = self.__out.pop()
            if response.destination:
                if response.destination in names:
                    client_socket = names[response.destination]
                    client_socket.send(bytes(response))
            else:
                self.__sock.send(bytes(response))
            self.__logger.info('Send {}.'.format(str(response)))


class Handler:
    def __init__(self):
        self._repo = ServerRepo()

    def run_action(self, request):
        if request.action == 'presence':
            self._repo.add_client(request.user_account_name)
            return jim.success()
        elif request.action == 'quit':
            return jim.success()
        elif request.action == 'msg':
            client = self._repo.get_user_by_name(request.client_name)
            contacts = client.contacts
            responses = [jim.success()]
            for contact in contacts:
                responses.append(
                    jim.Message(action='msg', text=request.text, to=contact.name, _from=request.client_name))
            return responses
        elif request.action == 'get_contacts':
            contacts = self._repo.get_contact_list(request.client_name)
            count = len(contacts)
            responses = [jim.success(response=202, quantity=count)]
            for contact in contacts:
                account_name = contact.name
                responses.append(jim.Message(action='contact_list', account_name=account_name))
            return responses
        elif request.action == 'add_contact':
            if request.client_name == request.user_name:
                return jim.error('It is not possible to add yourself')
            try:
                self._repo.add_contact(request.client_name, request.user_name)
                return jim.success()
            except:
                return jim.error('Contact does not exist')
        elif request.action == 'del_contact':
            try:
                self._repo.remove_contact(request.client_name, request.user_name)
                return jim.success()
            except:
                return jim.error('Contact does not exist')
        elif request.action == 'error':
            return jim.error('Error action')
        else:
            return jim.error('Action is not available')


class Server:
    def __init__(self, address):
        self.__server = socket.socket()
        self.__server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.__server.bind(address)
        self.__server.listen(WORKERS)
        self.__server.settimeout(0.2)
        self.__handler = Handler()
        self.__clients = []
        self.__dispatchers = {}
        self.__names = {}
        self.__in = []
        self.__out = []
        print('Listen on {}'.format(address))

    def listen(self):
        while True:
            try:
                client, address = self.__server.accept()
                dispatcher = Dispatcher(client, self.__handler)
            except OSError as e:
                pass
            else:
                if dispatcher.status:
                    self.__clients.append(client)
                    self.__dispatchers[client] = dispatcher
                    self.__names[dispatcher.client_name] = client
                    print('User "{}" from {} connected. Current {}.'.format(self.__user_name(client), address, len(self.__clients)))
            finally:
                r = []
                w = []
                try:
                    r, w, e = select.select(self.__clients, self.__clients, [], 0)
                except Exception as e:
                     pass #print('Exception until I/O select - {}'.format(e.args))
                self.__input(r)
                self.__process()
                self.__output(w)

    def __input(self, clients):
        for c in clients:
            try:
                dispatcher = self.__dispatchers[c]
                dispatcher.receive()
                self.__in.append(dispatcher)
            except:
                self.__remove_client(c)

    def __process(self):
        while len(self.__in):
            dispatcher = self.__in.pop()
            dispatcher.process()
            self.__out.append(dispatcher)

    def __output(self, clients):
        while len(self.__out):
            dispatcher = self.__out.pop()
            try:
                dispatcher.release(self.__names)
            except:
                self.__remove_client(dispatcher.__sock)

    def __remove_client(self, c):
        self.__clients.remove(c)
        print('User {} closed. Current {} '.format(self.__user_name(c), len(self.__clients)))
        c.close()

    def __user_name(self, c):
        return list(self.__names.keys())[list(self.__names.values()).index(c)]


def run():
    params = console.args()
    s = Server((params.address, params.port))
    s.listen()


if __name__ == '__main__':
    run()
