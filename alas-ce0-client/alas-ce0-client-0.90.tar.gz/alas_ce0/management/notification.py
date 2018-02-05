from alas_ce0.common.client_base import ApiClientBase


class NotificationClient(ApiClientBase):
    entity_endpoint_base_url = '/management/notifications/'

    def notify_user(self, resource_name, params=None):
        if params is None:
            params = dict()

        return self.http_post_json(self.entity_endpoint_base_url + 'user/' + resource_name, params)