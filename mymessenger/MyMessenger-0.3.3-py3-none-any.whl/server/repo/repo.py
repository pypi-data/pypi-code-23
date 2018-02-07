from .models import Client, ClientContact
from .errors import ContactDoesNotExist


class Repo:
    """Серверное хранилище"""

    def __init__(self, session):
        """
        Запоминаем сессию, чтобы было удобно с ней работать
        :param session:
        """
        self.session = session

    def add_client(self, username, password='', info=None):
        """Добавление клиента"""
        new_item = Client(username, password, info)
        self.session.add(new_item)
        self.session.commit()

    def client_exists(self, username):
        """Проверка, что клиент уже есть"""
        result = self.session.query(Client).filter(Client.Name == username).count() > 0
        return result

    def get_client_by_username(self, username):
        """Получение клиента по имени"""
        client = self.session.query(Client).filter(Client.Name == username).first()
        return client

    def add_contact(self, client_username, contact_username):
        """Добавление контакта"""
        contact = self.get_client_by_username(contact_username)
        if contact:
            client = self.get_client_by_username(client_username)
            if client:
                cc = ClientContact(client_id=client.ClientId, contact_id=contact.ClientId)
                self.session.add(cc)
                self.session.commit()
            else:
                # raise NoneClientError(client_username)
                pass
        else:
            raise ContactDoesNotExist(contact_username)

    def del_contact(self, client_username, contact_username):
        """Удаление контакта"""
        contact = self.get_client_by_username(contact_username)
        if contact:
            client = self.get_client_by_username(client_username)
            if client:
                cc = self.session.query(ClientContact).filter(
                    ClientContact.ClientId == client.ClientId).filter(
                    ClientContact.ContactId == contact.ClientId).first()
                self.session.delete(cc)
                self.session.commit()
            else:
                # raise NoneClientError(client_username)
                pass
        else:
            raise ContactDoesNotExist(contact_username)

    def get_contacts(self, client_username):
        """Получение контактов клиента"""
        client = self.get_client_by_username(client_username)
        result = []
        if client:
            # Тут нету relationship поэтому берем запросом
            contacts_clients = self.session.query(ClientContact).filter(ClientContact.ClientId == client.ClientId)
            for contact_client in contacts_clients:
                contact = self.session.query(Client).filter(Client.ClientId == contact_client.ContactId).first()
                result.append(contact)
        return result

    def get_all_clients(self):
        result = []
        for c in self.session.query(Client).all():
            result.append(c.Name)
        return result

    def show_all_clients(self):
        for c in self.session.query(Client).all():
            print(c.ClientId, c.Name)
