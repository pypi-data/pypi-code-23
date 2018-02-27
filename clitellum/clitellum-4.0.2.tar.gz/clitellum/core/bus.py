# author = sbermudel
# package description
from datetime import date
import datetime
import pytz

## Clase que contiene la informacion de identificacion de un proceso
class Identification:
    '''
    Contiene la información de identificacion del servicio
    '''

    def __init__(self, id_service, type_service):
        self._id = id_service
        self._type = type_service
        self._reply_key = type_service

    @property
    def id(self):
        '''
        Devuelve el identificador del servicio
        '''
        return self._id

    @property
    def type(self):
        '''
        Devuelve el tipo del servicio
        '''
        return self._type

    def set_reply_key(self, routing_key):
        '''
        Estable la clave de enrutamiento para los mensajes de reply
        '''
        self._reply_key = routing_key

    def get_reply_key(self):
        '''
        Devuelve la clave de enrutamiento para los mensajes de reply
        '''
        return self._reply_key

class MessageBuilder:
    '''
    Constructor de mensajes
    '''
    def __init__(self):
        self._identifcation = None
        self._body = None
        self._body_type = None
        self._call_context = dict()
        self._stack_trace = list()
        self._call_stack = list()
        self._is_reply = False
        self._priority = 0

    @classmethod
    def create(cls):
        '''
        Devuelve un builder de Message
        '''
        return MessageBuilder()

    def set_service(self, identification):
        '''
        Establece el servicio que crea el mensaje
        '''
        self._identifcation = identification
        return self

    def set_body(self, body):
        '''
        Establece el body
        '''
        self._body = body
        return self

    def set_type(self, body_type):
        '''
        Establece el tipo de mensaje
        '''
        self._body_type = body_type
        return self
    
    def set_context(self, header):
        '''
        Establece el contexto de ejecucion del mensaje
        '''
        if header is None:
            return self

        if 'CallContext' in header:
            self._call_context = header['CallContext']

        if 'CallStack' in header:
            self._call_stack = header['CallStack']

        if 'StackTrace' in header:
            self._stack_trace = header['StackTrace']

        return self

    def set_reply(self):
        '''
        Establece que el mensaje es un reply
        '''
        self._is_reply = True
        return self

    def set_priority(self, priority):
        '''
        Estable que la prioridad del mensaje por defecto es cero
        '''
        self._priority = priority
        return self

    def build(self):
        '''
        Contruye el mensaje
        '''
        message = dict()
        message['Body'] = self._body
        message['Header'] = self._generate_header()
        return message

    def _generate_header(self):
        header = dict()
        header['BodyType'] = self._body_type
        header['Priority'] = self._priority
        header['CreatedAt'] = datetime.datetime.utcnow().replace(tzinfo=pytz.timezone("UTC")).isoformat()
        header['CallContext'] = self._call_context
        header['CallStack'] = self._call_stack
        header['StackTrace'] = self._stack_trace
        header['IdentificationService'] = self._generate_identificaction()
        header['IsReply'] = self._is_reply

        header['StackTrace'].append(header['IdentificationService'])

        if not self._is_reply:
            header['CallStack'].append(header['IdentificationService'])
        else:
            if header['CallStack'][len(header['CallStack']) - 1]['Type'] == self._identifcation.type:
                header['CallStack'].pop()
        return header

    def _generate_identificaction(self):
        identification = dict()
        identification['Id'] = self._identifcation.id
        identification['Type'] = self._identifcation.type
        identification['ReplyKey'] = self._identifcation.get_reply_key()
        return identification
