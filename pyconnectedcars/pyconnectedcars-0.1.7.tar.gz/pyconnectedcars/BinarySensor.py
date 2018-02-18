from pyconnectedcars.vehicle import VehicleDevice
import datetime


class SystemsAreOkSensor(VehicleDevice):
    def __init__(self, data, controller):
        super().__init__(data, controller)
        self.__state = False
        self.lamps = []
        self.indicators = []

        self.last_updated = None

        self.type = 'system ok'
        self.hass_type = 'binary_sensor'
        self.name = self._name()
        self.uniq_name = self._uniq_name()
        self.bin_type = 0x1
        self.update()

    def update(self):
        self._controller.update()
        data = self._controller.get_car_params(self._id)
        if data:
            self.__state = not data['systemsAreOk']
            self.lamps = data['lamps']
            self.indicators = data['incidents']
            self.last_updated = datetime.datetime.strptime(data['updatedAt'], "%Y-%m-%dT%H:%M:%S.%fZ")

    def get_value(self):
        return self.__state

    @staticmethod
    def has_battery():
        return False


class OilLevelIsOkSensor(VehicleDevice):
    def __init__(self, data, controller):
        super().__init__(data, controller)
        self.__state = False

        self.last_updated = None

        self.type = 'oil level'
        self.hass_type = 'binary_sensor'
        self.name = self._name()
        self.uniq_name = self._uniq_name()
        self.bin_type = 0x1
        self.update()

    def update(self):
        self._controller.update()
        data = self._controller.get_car_params(self._id)
        if data:
            self.__state = not data['oilLevelIsOk']
            self.last_updated = datetime.datetime.strptime(data['updatedAt'], "%Y-%m-%dT%H:%M:%S.%fZ")

    def get_value(self):
        return self.__state

    @staticmethod
    def has_battery():
        return False


class TirePressureIsOkSensor(VehicleDevice):
    def __init__(self, data, controller):
        super().__init__(data, controller)
        self.__state = False

        self.last_updated = None

        self.type = 'tire pressure'
        self.hass_type = 'binary_sensor'
        self.name = self._name()
        self.uniq_name = self._uniq_name()
        self.bin_type = 0x1
        self.update()

    def update(self):
        self._controller.update()
        data = self._controller.get_car_params(self._id)
        if data:
            self.__state = not data['tirePressureIsOk']
            self.last_updated = datetime.datetime.strptime(data['updatedAt'], "%Y-%m-%dT%H:%M:%S.%fZ")

    def get_value(self):
        return self.__state

    @staticmethod
    def has_battery():
        return False


class BatteryChargeIsOkSensor(VehicleDevice):
    def __init__(self, data, controller):
        super().__init__(data, controller)
        self.__state = False

        self.last_updated = None

        self.type = 'battery charge'
        self.hass_type = 'binary_sensor'
        self.name = self._name()
        self.uniq_name = self._uniq_name()
        self.bin_type = 0x1
        self.update()

    def update(self):
        self._controller.update()
        data = self._controller.get_car_params(self._id)
        if data:
            self.__state = not data['batteryChargeIsOk']
            self.last_updated = datetime.datetime.strptime(data['updatedAt'], "%Y-%m-%dT%H:%M:%S.%fZ")

    def get_value(self):
        return self.__state

    @staticmethod
    def has_battery():
        return False
