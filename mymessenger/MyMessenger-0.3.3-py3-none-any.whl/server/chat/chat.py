class Chat(object):
    """
    Класс Чат - класс, обеспечивающий взаимодействие двух клиентов.
    """
    def __init__(self):
        self.__clients = {}

    def join(self, client):
        self.__clients.update({client: []})

    def leave(self, client):
        del self.__clients[client]

    def put(self, client, message):
        for c in self.__clients:
            if c is not client:
                self.__clients[c].append(message)

    def get(self, client):
        if not self.is_empty(client):
            return self.__clients[client].pop(0)

    def get_members_count(self):
        return len(self.__clients)

    def is_member(self, client):
        return client in self.__clients

    def is_empty(self, client):
        if self.is_member(client):
            return len(self.__clients[client]) == 0
        return True


class ChatController(object):
    """
    Класс ЧатКонтроллер - класс, обеспечивающий передачу данных из Чата в ГрафическийЧат и обратно;
    обрабатывает события от пользователя (ввод данных, отправка сообщения).
    """
    pass
