from pyconnectedcars.vehicle import VehicleDevice
import dateutil.parser


class Fuel(VehicleDevice):
    def __init__(self, data, controller):
        super().__init__(data, controller)
        self.__fuel_level = 0
        self.__fuel_level_pct = 0

        self.last_updated = 0

        self.type = 'fuel sensor'
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
            self.__fuel_level_pct = data['fuelLevel']
            self.last_updated = dateutil.parser.parse(
                data['fuelLevelUpdatedAt'])

    @staticmethod
    def has_battery():
        return False

    def get_value(self):
        return self.__fuel_level
