import sys
from client import User
from handlers import ConsoleReceiver
import threading

try:
    addr = sys.argv[1]
except IndexError:
    addr = 'localhost'

try:
    port = int(sys.argv[2])
except IndexError:
    port = 7777
except ValueError:
    print('Порт должен быть целым числом')
    sys.exit()

try:
    name = sys.argv[3]
except IndexError:
    name = 'ConsoleGuest'

client = User(name, addr, port)
client.connect()

listener = ConsoleReceiver(client.sock, client.request_queue)
th_listen = threading.Thread(target=listener.poll)
th_listen.daemon = True
th_listen.start()

while True:
    message_str = input('<<')
    if message_str.startswith('add'):
        try:
            username = message_str.split()[1]
        except IndexError:
            print('Не указано имя пользователя')
        else:
            client.add_contact(username)
    elif message_str.startswith('del'):
        try:
            username = message_str.split()[1]
        except IndexError:
            print('Не указано имя пользователя')
        else:
            client.del_contact(username)
    elif message_str == 'list':
        contacts = client.get_contacts()
        print(contacts)
    elif message_str.startswith('message'):
        params = message_str.split()
        try:
            to = params[1]
            text = ' '.join(params[2:])
        except IndexError:
            print('Не задан получатель или текст сообщения')
        else:
            client.send_message(to, text)
    elif message_str == 'help':
        print('add <имя пользователя> - добавить контакт')
        print('del <имя пользователя> - удалить контакт')
        print('list - список контактов')
        print('message <получатель> <текст> - отправка сообщения')
        print('exit - выход')
    elif message_str == 'exit':
        break
    else:
        print('Неизвестная команда. Для справки введите help')

client.disconnect()

# python client_console.py localhost 7777 Igor
