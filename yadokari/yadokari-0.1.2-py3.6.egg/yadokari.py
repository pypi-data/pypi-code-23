import json
import pprint

import click
import requests

BASE_URL = 'https://yado-kari.herokuapp.com/'

RESERVATION_INFO = '''
*** YOUR INFORMATION ***
{}
************************
'''

VALUE_TO_PROMPT = [
    ('name', 'your name', None, None),
    ('email', 'email address', None, None),
    ('tel', 'tel number', None, None),
    ('check_in_on', 'check in date', None, None),
    ('check_out_on', 'check out date', None, None),
    ('check_in_time', 'check in time', None, None),
    ('men_number', 'number of men', None, None),
    ('women_number', 'number of women', None, None),
    ('purpose_of_use', 'purpose of use', '開発合宿', True),
    ('payment_method', 'method of payment', '現金支払い', True),
    ('coupon', 'coupon code', '無し', True),
    ('note', 'note', '無し', True),
]


@click.group()
def cmd():
    pass


@cmd.command(name='list')
def show_list():
    """宿の一覧を表示 """
    res = requests.get(BASE_URL + '/api/v1/yados')
    yados = json.loads(res.content)
    click.echo('\n'.join(('{}. {}'.format(yado["id"], yado["name"]) for yado in yados)))


@cmd.command()
@click.argument('context', nargs=-1)
def show(context):
    """宿の詳細URLを表示 """
    if context:
        click.echo('https://omishima-space.com/')


@cmd.command()
@click.argument('context', nargs=1)
def cal(context):
    """宿の予約状況を表示 """
    if not context:
        context = 1
    res = requests.get(BASE_URL + '/api/v1/yados/{}/schedules'.format(context))
    reservations = json.loads(res.content)
    click.echo(
        '\n'.join('{}: {} - {}'.format(r["schedule"], r["started_on"], r["finished_on"]) for r in
                  reservations))


@cmd.command()
@click.argument('context', nargs=1)
def reserve(context):
    """宿の予約を行う """
    if not context:
        context = 1
    info = get_reservation_info()
    res = requests.post(BASE_URL + 'api/v1/yados/{}/reservations'.format(context),
                        data={'reservation[{}]'.format(k): v for k, v in info.items()})
    click.echo(res.content)
    click.echo('done!!')


def get_reservation_info():
    """ユーザーから宿の予約情報を受け取る """
    info = {}
    for i, text, default, show_default in VALUE_TO_PROMPT:
        info[i] = click.prompt(text, default=default, show_default=show_default)

    click.echo(RESERVATION_INFO.format(
        '\n'.join(
            ('{}. {}: {}'.format(i, t[1], info[t[0]]) for i, t in enumerate(VALUE_TO_PROMPT)))))
    confirm = click.prompt('confirm(Y/y) or edit(0-{})'.format(len(VALUE_TO_PROMPT) - 1))
    while confirm not in ('Y', 'y', 'YES', 'Yes', 'yes'):
        try:
            confirm = int(confirm)
            i, text, default, show_default = VALUE_TO_PROMPT[confirm]
            info[i] = click.prompt(text, default=default, show_default=show_default)
        except:
            pass
        click.echo(RESERVATION_INFO.format(
            '\n'.join(
                ('{}. {}: {}'.format(i, t[1], info[t[0]]) for i, t in enumerate(VALUE_TO_PROMPT)))))
        confirm = click.prompt('confirm(Y/y) or edit(0-{}): '.format(len(VALUE_TO_PROMPT) - 1))
    return info


@cmd.command()
@click.argument('token', nargs=1)
def me(token):
    """トークンから予約情報を受け取る """
    if not token:
        return
    res = requests.get(BASE_URL + 'api/v1/me/{}'.format(token))
    if res.status_code == 404:
        click.echo('not found')
        return
    info = json.loads(res.content)
    pprint.pprint(info)


def main():
    cmd()


if __name__ == '__main__':
    main()
