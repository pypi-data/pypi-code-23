import os
import json
import leankit


def convert(item, table):
    def f(data):
        if isinstance(data, dict):
            r = {}
            for key, value in data.items():
                r[key] = f(value)
        elif isinstance(data, list):
            r = []
            for value in data:
                r.append(f(value))
        elif isinstance(data, (str, int)) and data in table:
            r = table.get(data, data)
        else:
            r = data
        return r

    return f(item)


def routes(board):
    main = [f'/Boards/{board.id}', f'/Board/{board.id}/Archive']
    cards = [f'/Board/{board.id}/GetCard/{card}' for card in board.cards]
    events = [f'/Card/History/{board.id}/{card}' for card in board.cards]
    return main + cards + events


def download(board, table):
    for route in routes(board):
        print(route)
        response = leankit.connector.api.get(route)
        data = convert(response, table)
        if 'OrganizationActivities' in data:
            data['OrganizationActivities'] = []
        path = [table.get(folder, folder) for folder in route.split('/')]
        path[0] = 'data'
        folder = '/'.join(path[:-1])
        if not os.path.exists(folder):
            os.makedirs(folder)
        print('/'.join(path))
        with open('/'.join(path) + '.json', 'w') as output:
            json.dump(data, output, indent=2)


def table(board, new_id):
    lanes = [lane['Id'] for lane in board.sorted_lanes]
    tbl = {board.id: 0}
    tbl.update({i: 1 + v for v, i in enumerate(board.users)})
    tbl.update({i: 11 + v for v, i in enumerate(board.card_types)})
    tbl.update({i: 101 + v for v, i in enumerate(board.classes_of_service)})
    tbl.update({i: 1001 + v for v, i in enumerate(lanes)})
    tbl.update({i: 10001 + v for v, i in enumerate(board.cards)})
    for user in board.users.values():
        tbl[user.user_name] = f'User{tbl[user.id]}@example.org'
        tbl[user.full_name] = f'User {tbl[user.id]}'
    tbl[board.title] = f'Board {new_id}'
    tbl.update({i: v + new_id for i, v in tbl.items() if isinstance(i, int)})
    tbl.update({str(i): str(v) for i, v in tbl.items() if isinstance(i, int)})
    return tbl


def run(board_id, new_id):
    board = leankit.Board(board_id)
    board.get_archive()
    tbl = table(board, new_id)
    download(board, tbl)
