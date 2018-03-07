class WifiNetwork:
    def __init__(self,
                 mac_address=None,
                 age=None,
                 channel=None,
                 frequency=None,
                 signalStrength=None,
                 snr=None,
                 ssid=None):
        self.mac_address = mac_address
        self.age = age
        self.channel = channel
        self.frequency = frequency
        self.signalStrength = signalStrength
        self.snr = snr
        self.ssid = ssid

    def to_query(self):
        query = {}
        if self.mac_address:
            query["macAddress"] = self.mac_address
        if self.age:
            query["age"] = self.age
        if self.channel:
            query["channel"] = self.channel
        if self.frequency:
            query["frequency"] = self.frequency
        if self.signalStrength:
            query["signalStrength"] = self.signalStrength
        if self.snr:
            query["signalToNoiseRatio"] = self.snr
        if self.ssid:
            query["ssid"] = self.ssid
        return query


class RadioType:
    GSM = "gsm"
    WCDMA = "wcdma"
    LTE = "lte"


class CellTower:
    def __init__(self,
                 radio_type: str = None,
                 mobile_country_code: int = None,
                 mobile_network_code: int = None,
                 location_area_code: int = None,
                 cell_id: int = None,
                 age: int = None,
                 psc: int = None,
                 signal_strength: int = None,
                 timing_advance: int = None):
        self.radio_type = radio_type
        self.mobile_country_code = mobile_country_code
        self.mobile_network_code = mobile_network_code
        self.location_area_code = location_area_code
        self.cell_id = cell_id
        self.age = age
        self.psc = psc
        self.signal_strength = signal_strength
        self.timing_advance = timing_advance

    def to_query(self):
        query = {}
        if self.radio_type:
            query["radioType"] = self.radio_type
        if self.mobile_country_code:
            query["mobileCountryCode"] = self.mobile_country_code
        if self.mobile_network_code:
            query["mobileNetworkCode"] = self.mobile_network_code
        if self.location_area_code:
            query["locationAreaCode"] = self.location_area_code
        if self.cell_id:
            query["cellId"] = self.cell_id
        if self.age:
            query["age"] = self.age
        if self.psc:
            query["psc"] = self.psc
        if self.signal_strength:
            query["signalStrength"] = self.signal_strength
        if self.timing_advance:
            query["timingAdvance"] = self.timing_advance
        return query


class BluetoothBeacon:
    def __init__(self,
                 mac_address: str = None,
                 name: str = None,
                 age: int = None,
                 signal_strength: int = None):
        self.mac_address = mac_address
        self.name = name
        self.age = age
        self.signal_strength = signal_strength

    def to_query(self):
        query = {}
        if self.mac_address:
            query["macAddress"] = self.mac_address
        if self.name:
            query["name"] = self.name
        if self.age:
            query["age"] = self.age
        if self.signal_strength:
            query["signalStrength"] = self.signal_strength
        return query
