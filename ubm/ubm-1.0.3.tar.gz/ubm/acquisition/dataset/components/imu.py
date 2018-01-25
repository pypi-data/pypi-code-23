import numpy as np
from ubm.acquisition.dataset.names import Names
from ubm.acquisition.filter import Filter


class InertialAxis:

    def __init__(self, device):
        self.device = device
        self.filter = device.filter
        self.dataset = device.dataset
        self.X_OFFSET = []
        self.Y_OFFSET = []
        self.Z_OFFSET = []
        self.get_pitch = self.get_x
        self.get_roll = self.get_y
        self.get_yaw = self.get_z
        self.get_raw_pitch = self.get_raw_x
        self.get_raw_roll = self.get_raw_y
        self.get_raw_yaw = self.get_raw_z

    def get_x(self):
        return self.filter.set_data(self.get_raw_x()).get() + self.get_x_offset()

    def get_y(self):
        return self.filter.set_data(self.get_raw_y()).get() + self.get_y_offset()

    def get_z(self):
        return self.filter.set_data(self.get_raw_z()).get() + self.get_z_offset()

    def get_raw_x(self):
        # As strange as it might seem, it is right.
        # Thanks Team-Luke for the erroneous Axis
        return -self.dataset.get_data()[self.device.AXIS_X]

    def get_raw_y(self):
        # Same
        return self.dataset.get_data()[self.device.AXIS_Z]

    def get_raw_z(self):
        # Same
        return self.dataset.get_data()[self.device.AXIS_Y]

    def get_x_offset(self):
        return self.get_offset(self.X_OFFSET)

    def get_y_offset(self):
        return self.get_offset(self.Y_OFFSET)

    def get_z_offset(self):
        return self.get_offset(self.Z_OFFSET)

    def get_offset(self, defined_offset):
        offset_size = np.size([defined_offset])
        if offset_size == self.dataset.get_size():
            return defined_offset[self.dataset.get_interval().to_index()]
        if offset_size > 0:
            return np.r_(defined_offset)[0]
        return 0


class Accelerometer(InertialAxis):

    AXIS_X, AXIS_Y, AXIS_Z = Names.IMU["Accelerometer"]
    ZERO_BOUNDARY = 0.05

    def __init__(self, dataset):
        self.dataset = dataset
        self.filter = Filter()
        self.filter.set_type(Filter.TYPE_MEDIAN)
        self._zero_ = None
        InertialAxis.__init__(self, self)

    def get_filter(self):
        return self.filter

    def when_zero(self):
        return self.when_between(-self.ZERO_BOUNDARY, self.ZERO_BOUNDARY)

    def when_between(self, lower_bound, upper_bound):
        if self._zero_ is None:
            x_sel = self.filter.set_data(self.get_x()).in_range(lower_bound, upper_bound)
            y_sel = self.filter.set_data(self.get_y()).in_range(lower_bound, upper_bound)
            z_sel = self.filter.set_data(self.get_z() + 1).in_range(lower_bound, upper_bound)
            self._zero_ = x_sel & y_sel & z_sel
        return self._zero_[self.dataset.get_interval().to_index()]


class Gyroscope(InertialAxis):
    """
    Accelerometer needed for calibration
    """

    AXIS_X, AXIS_Y, AXIS_Z = Names.IMU["Gyroscope"]
    CL_ZEROING = 0.66

    def __init__(self, dataset):
        self.dataset = dataset
        self.filter = Filter()
        self.filter.set_type(Filter.TYPE_MEDIAN)
        InertialAxis.__init__(self, self)

    def get_filter(self):
        return self.filter

    def calibrate(self):
        line = self.dataset.get_interval().to_sample()

        mean_diff, mean_val = self._get_calibration_values(self.get_x())
        self.X_OFFSET = -mean_val - (line * mean_diff)

        mean_diff, mean_val = self._get_calibration_values(self.get_y())
        self.Y_OFFSET = -mean_val - (line * mean_diff)

        mean_diff, mean_val = self._get_calibration_values(self.get_z())
        self.Z_OFFSET = -mean_val - (line * mean_diff)

    def _get_calibration_values(self, data):
        when_pretty_small = self.dataset.get_accelerometer().when_between(-self.CL_ZEROING, self.CL_ZEROING)
        mean_diff = np.mean(self.filter.set_data(data[when_pretty_small]).get_derivative())
        mean_val = np.mean(data[when_pretty_small][0:10])
        return mean_diff, mean_val
