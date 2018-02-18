class VehicleDevice:
    def __init__(self, data, controller):
        self._id = data['id']
        self._vin = data['vin']
        self._raw_name = data['name']
        self._controller = controller
        self.should_poll = True

    def _name(self):
        return "{} {}".format(self._raw_name, self.type)

    def _uniq_name(self):
        return '{} {} {}'.format(self._raw_name, self._vin, self.type)
