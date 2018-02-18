from pyconnectedcars.vehicle import VehicleDevice
import datetime


class Fuel(VehicleDevice):
    def __init__(self, data, controller):
        super().__init__(data, controller)
        self.__fuel_level = 0
        self.fuel_level_pct = 0

        self.last_updated = 0

        self.type = 'fuel level'
        self.measurement = 'VOLUME_LITERS'
        self.hass_type = 'sensor'
        self.name = self._name()
        self.uniq_name = self._uniq_name()
        self.bin_type = 0x5
        self.update()

    def update(self):
        self._controller.update()
        data = self._controller.get_car_params(self._id)
        if data:
            self.__fuel_level = data['fuelLevelLiter']
            self.fuel_level_pct = data['fuelLevel']
            self.last_updated = datetime.datetime.strptime(data['fuelLevelUpdatedAt'], "%Y-%m-%dT%H:%M:%S.%fZ")

    @staticmethod
    def has_battery():
        return False

    def get_value(self):
        return self.__fuel_level
