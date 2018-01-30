import sys

import jim
from console import Params
from echo import client

ACTIONS = (
    {
        'action': 'msg',
        'name': 'Послать сообщение',
        'params': ('text',)
    },
    {
        'action': 'get_contacts',
        'name': 'Список контактов',
    },
    {
        'action': 'add_contact',
        'name': 'Добавить контакт',
        'params': ('user_name',)
    },
    {
        'action': 'del_contact',
        'name': 'Удалить контакт',
        'params': ('user_name',)
    },
    {
        'action': 'quit',
        'name': 'Выйти'
    }
)


def interact():
    print('\n'.join(['{}. {}'.format(key, action['name']) for key, action in enumerate(ACTIONS, 1)]))
    try:
        num = abs(int(input('Выберите действие или введите сообщение: ')))
    except ValueError:
        num = 0
    config = ACTIONS[num - 1] if num <= len(ACTIONS) else ACTIONS[0]
    params = {'action': config['action']}
    if 'params' in config:
        for param in config['params']:
            p = str(input('Выберите параметр "{}": '.format(param)))
            params[param] = p
    return jim.Message(**params)


def receive_callback(parcel):
    if parcel.action == 'contact_list':
        print('\n{}'.format(parcel.account_name))
    elif parcel.action == 'msg':
        print('\nMessage from {}: {}'.format(parcel.sender, parcel.text))


if __name__ == '__main__':
    console_params = Params(sys.argv)
    client = client.Client(console_params.console_host, console_params.account_name, receive_callback)
    if client.connect():
        while True:
            message = interact()
            client.send(message)
