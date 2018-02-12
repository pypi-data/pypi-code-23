import requests


class Connection(object):
    """
    The connection to the API. All interaction ultimately goes via this
    object.
    """

    def __init__(self, api_key):
        self.api_key = api_key
        self.api_base = 'https://api2.autopilothq.com/v1'

    def contact(self, email):
        return Contact(self, email)

    def send_get_request(self, path):
        full_path = self.api_base + '/' + path
        response = requests.get(full_path,
                                headers={'autopilotapikey': self.api_key})
        response.raise_for_status()
        return response

    def send_delete_request(self, path):
        full_path = self.api_base + '/' + path
        response = requests.delete(full_path,
                                   headers={'autopilotapikey': self.api_key})
        response.raise_for_status()
        return response


class Contact(object):
    """
    A single contact in the Autopilot database.
    """

    def __init__(self, connection, email):
        self.connection = connection
        self.email = email

        # Check the contact exists
        self.connection.send_get_request(self._url())

    def _url(self):
        """Get the URL that identifies this object."""
        return 'contact/{email}'.format(email=self.email)

    def delete(self):
        self.connection.send_delete_request(self._url())
