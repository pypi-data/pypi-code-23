
def indico_request():
    import requests
    import json
    import urllib.parse as urlparse
    from pprint import pprint

    api_key = '829e3826-39ad-4be3-b50f-1d25397e67bd'
    url_base = 'https://indico.desy.de/indico/export/categ/384.json'
    url_query = {
        'apikey': api_key
    }

    url = '{}?{}'.format(url_base, urlparse.urlencode(url_query))

    response = requests.get(url)
    response_dict = json.loads(response.text)
    pprint(response_dict)


def simple_text_view():
    from IndicoWp.indico.indico import IndicoEventRequestController
    from IndicoWp.views.text import SimpleEventTextView, SimpleEventsTableView

    requester = IndicoEventRequestController()
    event_list = requester.get_category_events(384)
    view = SimpleEventsTableView(event_list)
    print(view.get_string())


def create_database():
    from IndicoWp.database import MySQLDatabaseAccess
    MySQLDatabaseAccess.create_database()


def observerd():
    from IndicoWp.controller import Controller
    controller = Controller()
    try:
        controller.post_observed_events()
    finally:
        controller.close()


if __name__ == '__main__':
    observerd()