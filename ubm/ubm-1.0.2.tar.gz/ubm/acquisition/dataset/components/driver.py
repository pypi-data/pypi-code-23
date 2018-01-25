import numpy as np
from ubm.acquisition.dataset.names import Names
from ubm.acquisition.filter import Filter


class SteeringAngle:
    """
    Gyroscope and Speed needed for calibration
    """

    STEERING_ANGLE = Names.Driver["SteeringAngle"]
    ZEROING_CALI = 0.1
    CL_MOVING_SPEED = 5
    OUT_TRIGGER = 50
    OUT_LEN = 32

    def __init__(self, dataset):
        self.dataset = dataset
        self.filter = Filter()
        self.ANGLE_OFFSET = 0

    def get(self):
        return self.filter.set_data(self.get_raw()).remove_outliers(self.OUT_TRIGGER, self.OUT_LEN) - self.ANGLE_OFFSET

    def get_raw(self):
        return self.dataset.get_data()[self.STEERING_ANGLE]

    def calibrate(self):
        lateral_force = self.dataset.get_accelerometer().get_roll()
        is_moving = (self.dataset.get_speed() > self.CL_MOVING_SPEED)
        is_not_turning = (lateral_force < self.ZEROING_CALI) & (lateral_force > -self.ZEROING_CALI)
        self.ANGLE_OFFSET = np.median(self.get()[is_moving & is_not_turning])


class Throttle:

    THROTTLE = Names.Driver["Throttle"]

    def __init__(self, dataset):
        self.dataset = dataset

    def get(self):
        return self.dataset.get_data()[self.THROTTLE]


class Brakes:

    FRONT_PRESSURE, REAR_PRESSURE = Names.Driver["Brakes"]

    def __init__(self, dataset):
        self.dataset = dataset

    def get_front_pressure(self):
        return self.dataset.get_data()[self.FRONT_PRESSURE]

    def get_rear_pressure(self):
        return self.dataset.get_data()[self.REAR_PRESSURE]

    def get_balance(self):
        total_mean = np.mean(np.concatenate((self.get_front_pressure(), self.get_rear_pressure())))
        return np.round((np.mean(self.get_front_pressure()) / total_mean) * 50, 1)
