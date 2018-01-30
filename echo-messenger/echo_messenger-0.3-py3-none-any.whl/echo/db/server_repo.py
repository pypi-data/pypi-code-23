from sqlalchemy import exists
from .server import session, Client


class ServerRepo:
    def __init__(self):
        self.__session = session

    def add_client(self, account_name):
        if not self.__session.query(exists().where(Client.name == account_name)).scalar():
            client = Client(account_name)
            self.__session.add(client)
        return self.__session.commit()

    def get_contact_list(self, client_name):
        client = self.get_user_by_name(client_name)
        return client.contacts

    def add_contact(self, client_name, contact_name):
        client = self.get_user_by_name(client_name)
        contact = self.get_user_by_name(contact_name)
        if contact:
            client.contacts.append(contact)
            self.__session.add(client)
            self.__session.commit()
        else:
            raise Exception

    def remove_contact(self, client_name, contact_name):
        client = self.get_user_by_name(client_name)
        contact = self.get_user_by_name(contact_name)
        if contact:
            client.contacts.remove(contact)
            self.__session.add(client)
            self.__session.commit()
        else:
            raise Exception

    def get_user_by_name(self, name):
        return self.__session.query(Client).filter(Client.name == name).first()
