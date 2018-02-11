import requests
import xmltodict
import urllib3


class GopHub:

    def __init__(self, host, apiVersion=3):
        self.host = host
        self.scheme = 'https'
        self.token = None
        self.gopApiVersion = apiVersion
        self.fixture_ids = []
        self.bulb_ids = []
        self.devices = {}
        if apiVersion < 3:
            self.token = '1234567890'
            self.scheme = 'http'

    def set_token(self, token):
        self.token = token

    def clear_fixtures(self):
        for id in self.fixture_ids:
            del self.devices[id]
        self.fixture_ids = []

    def clear_bulbs(self):
        for id in self.bulb_ids:
            del self.devices[id]
        self.bulb_ids = []

    def update_fixtures(self):
        path = ('/gwr/gop.php?cmd=GWRBatch&data=<gwrcmds><gwrcmd>'
                '<gcmd>RoomGetCarousel</gcmd><gdata><gip><version>1</version>'
                '<token>{0}</token><fields>name,status</fields></gip></gdata>'
                '</gwrcmd></gwrcmds>&fmt=xml').format(self.token)
        response = self.send_command(path)
        parsed_response = xmltodict.parse(response.content,
                                          force_list={'room', 'device'})
        rooms = parsed_response['gwrcmds']['gwrcmd']['gdata']['gip']['room']

        self.clear_fixtures()
        for room in rooms:
            for device in room['device']:
                did = int(device['did'])
                self.fixture_ids.append(did)
                self.devices[did] = device

    def update_bulbs(self):
        path = ('/gwr/gop.php?cmd=GWRBatch&data=<gwrcmds><gwrcmd><gcmd>'
                'DeviceVirtualGetList</gcmd><gdata><gip><version>1</version>'
                '<token>{0}</token><fields>name,status</fields></gip></gdata>'
                '</gwrcmd></gwrcmds>&fmt=xml').format(self.token)
        response = self.send_command(path)
        parsed_response = xmltodict.parse(response.content,
                                          force_list={'virtual', 'device'})
        virtual_devices = (parsed_response['gwrcmds']['gwrcmd']
                           ['gdata']['gip']['virtual'])
        self.clear_bulbs()
        for virtual_device in virtual_devices:
            for device in virtual_device['device']:
                did = int(device['did'])
                self.bulb_ids.append(did)
                self.devices[did] = device

    def update_devices(self, allow_fixtures=True, allow_bulbs=True):
        if allow_fixtures:
            self.update_fixtures()
        elif self.fixture_ids.count > 0:
            self.clear_fixtures()

        if allow_bulbs:
            self.update_bulbs()
        elif self.bulb_ids.count > 0:
            self.clear_bulbs()

    def set_brightness(did, value):
        value = str(value)
        path = ('/gwr/gop.php?cmd=DeviceSendCommand&data=<gip>'
                '<version>1</version><token>{0}</token><did>{1}</did>'
                '<value>{2}</value><type>level</type>'
                '</gip>&fmt=xml').format(self.token, did, value)

        response = self.send_command(path)
        if response.status_code == '200':
            return True
        else:
            return False

    def hass_brightness(device):
        """Home Assistant logic for determining brightness"""
        if 'level' in device:
            level = int((int(device['level']) / 100) * 255)
            return level
        else:
            return 0

    def turn_on(did):
        path = ('/gwr/gop.php?cmd=DeviceSendCommand&data=<gip>'
                '<version>1</version><token>{0}</token><did>{1}</did>'
                '<value>1</value></gip>&fmt=xml')
        response = requests.get(url, verify=False)
        return response.status_code == '200'

    def turn_off(did):
        path = ('/gwr/gop.php?cmd=DeviceSendCommand&data=<gip>'
                '<version>1</version><token>{0}</token><did>{1}</did>'
                '<value>0</value></gip>&fmt=xml')
        response = requests.get(url, verify=False)
        return response.status_code == '200'

    def check_online(device):
        """ Logic for Determining Device Availability """
        return 'offline' not in device

    def grab_token():
        """ Grab token from gateway. Press sync button before running. """
        path = ('/gwr/gop.php?cmd=GWRLogin&data=<gip><version>1</version>'
                '<email>email</email><password>password</password></gip>'
                '&fmt=xml')
        response = self.send_command(path)
        if '<rc>404</rc>' in response.text:
            raise PermissionError('Not In Pairing Mode')
        parsed = xmltodict.parse(response.content)
        token = parsed['gip']['token']
        return token

    def send_command(self, path):
        urllib3.disable_warnings()
        url = '{0}://{1}{2}'.format(self.scheme, self.host, path)
        return requests.get(url, verify=False)
