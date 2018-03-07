
import requests

from mozls.query import WifiNetwork, CellTower, BluetoothBeacon

DEFAULT_API_KEY = "test"


class Fallback:
    LAC = "lacf"
    IP = "ipf"


class MLSException(Exception):
    def __init__(self, error_obj: dict):
        self.code = error_obj["code"]
        self.message = error_obj["message"]

    def __str__(self):
        return "Error code {}: {}".format(self.code, self.message)


class MLSNoLocationException(MLSException):
    pass


class MLSInvalidApiKeyException(MLSException):
    pass


class MLSParseException(MLSException):
    pass


class MLSApiKeyLimitException(MLSException):
    pass


class MLSUnreachableException(MLSException):
    pass


class Location:
    def __init__(self,
                 lat: float = 0.0,
                 lon: float = 0.0,
                 accuracy: float = 0.0,
                 fallback: str = None):
        self.lat = lat
        self.lon = lon
        self.accuracy = accuracy
        self.fallback = fallback

    @staticmethod
    def from_response(response: dict) -> "Location":
        o = Location()
        o.lat = response["location"]["lat"]
        o.lon = response["location"]["lng"]
        o.accuracy = response["accuracy"]

        fallbacks = {
            "ipf": Fallback.IP,
            "lacf": Fallback.LAC
        }
        o.fallback = fallbacks.get(response.get("fallback", ""), None)

        return o


def query_mls(wifi_networks = None,
              cell_towers = None,
              bluetooth_beacons = None,
              fallbacks = (),
              apikey=DEFAULT_API_KEY) -> Location:
    if wifi_networks is None:
        wifi_networks = []
    if cell_towers is None:
        cell_towers = []
    if bluetooth_beacons is None:
        bluetooth_beacons = []
    query_url = "https://location.services.mozilla.com/v1/geolocate?key={key}".format(key=apikey)

    avail_fallbacks = {
        Fallback.IP: "ipf",
        Fallback.LAC: "lacf"
    }

    query_body = {
        "wifiAccessPoints": [n.to_query() for n in wifi_networks],
        "cellTowers": [ct.to_query() for ct in cell_towers],
        "bluetoothBeacons": [bb.to_query() for bb in bluetooth_beacons],
        "fallbacks": {f: f in fallbacks for f in avail_fallbacks}
    }

    http_response = requests.post(query_url, json=query_body)

    if 500 <= http_response.status_code <= 599:
        raise MLSUnreachableException({"code": http_response.status_code, "message": "HTTP error"})

    response = http_response.json()
    if "error" in response:
        errorcode = response["error"]["code"]
        reason = response["error"]["errors"][0]["reason"]
        if errorcode is 400:
            if reason == "keyInvalid":
                raise MLSInvalidApiKeyException(response["error"])
            elif reason == "parseError":
                raise MLSParseException(response["error"])
        elif errorcode is 403:
            raise MLSApiKeyLimitException(response["error"])
        elif errorcode is 404:
            raise MLSNoLocationException(response["error"])
        elif 500 <= errorcode <= 599:
            raise MLSUnreachableException(response["error"])
        else:
            raise MLSException(response["error"])

    return Location.from_response(response)
