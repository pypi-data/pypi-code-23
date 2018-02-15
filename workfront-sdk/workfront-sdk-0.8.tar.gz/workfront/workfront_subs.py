import requests
import urlparse


class WorkfrontSubscriptionAPI:

    def __init__(self, apikey):
        self.api_key = apikey
        self.sess = requests.sessions.session()
        self.url_base = 'https://thebridgecorp.my.workfront.com/'

    def get_subscriptions(self):
        u = urlparse.urljoin(self.url_base, 'attask/eventsubscription/api/v1/subscriptions/list')
        hs = {'Authorization': self.api_key}
        return self.sess.get(u, headers=hs)

    def subscribe(self, obj):
        u = urlparse.urljoin(self.url_base, 'attask/eventsubscription/api/v1/subscriptions')
        hs = {'Authorization': self.api_key}
        return self.sess.post(u, json=obj, headers=hs)
