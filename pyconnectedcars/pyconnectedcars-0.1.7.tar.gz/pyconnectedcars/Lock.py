from pyconnectedcars.vehicle import VehicleDevice
import datetime


class Lock(VehicleDevice):
    def __init__(self, data, controller):
        super().__init__(data, controller)
        self.__lock_state = False

        self.last_updated = 0

        self.type = 'door lock'
        self.hass_type = 'lock'
        self.name = self._name()
        self.uniq_name = self._uniq_name()
        self.bin_type = 0x7
        self.update()

    def update(self):
        self._controller.update()
        data = self._controller.get_car_params(self._id)
        if data:
            if data['lockedState'] == 'UNLOCKED':
                self.__lock_state = False
            else:
                self.__lock_state = True
            self.last_updated = datetime.datetime.strptime(data['lockedStateUpdatedAt'], "%Y-%m-%dT%H:%M:%S.%fZ")

    def is_locked(self):
        return self.__lock_state

    @staticmethod
    def has_battery():
        return False
