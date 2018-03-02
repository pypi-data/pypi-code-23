import datetime
import itertools

import click
import requests


@click.command()
@click.option('--statistics', help='show the hottest and the coolest temperature of the last 7 days', is_flag="True")
def aare(statistics):
    """A simple command which displays the current aare temperature"""
    if statistics:
        display_stats()
    else:
        display_current_temp()


def display_current_temp():
    api_url = 'http://aare.schwumm.ch/aare.json'
    response = requests.get(api_url)
    aare_json = response.json()
    click.echo("Current temperature of the aare: {}° C".format(aare_json["temperature"]))


def display_stats():
    api_url = 'http://aare.schwumm.ch/api/archive'
    params = {"from": "now", "to": "-7 days"}
    # The website denies unknown user agents. So we have to impersonate a general webbrowser to gain access
    headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_5) AppleWebKit/537.36 (KHTML, like Gecko) '
                      'Chrome/50.0.2661.102 Safari/537.36'}
    response = requests.get(api_url, params, headers=headers)
    response_json = response.json()
    temperatures = response_json['data']['temperature']
    dates = [datetime.datetime.strptime(item, '%Y-%m-%d %H:%M:%S') for item in response_json['data']['datetime']]
    data = list(zip(dates, temperatures))

    # Remove data points not having a temperature
    data = list(filter(lambda item: item[1], data))
    for key, group in itertools.groupby(data, lambda item: datetime.date(item[0].year, item[0].month, item[0].day)):
        temperatures = [item[1] for item in tuple(group)]
        min_temp = min(temperatures)
        max_temp = max(temperatures)
        day_string = key.strftime('%Y-%m-%d')
        output = "{}: min {}° C, max {}° C".format(day_string, min_temp, max_temp)
        print(output)


if __name__ == '__main__':
    aare()
