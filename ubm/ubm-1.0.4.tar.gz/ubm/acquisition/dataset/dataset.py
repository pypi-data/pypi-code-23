import math
import numpy as np
from ubm.acquisition.dataset.names import Names
from ubm.acquisition.dataset.components import driver, imu
from ubm.acquisition.dataset.components import internal
from ubm.acquisition.dataset.components import vehicle


class Dataset:
    F_SAMPLING = 100.0

    def __init__(self, data):
        self.original_data = data
        Names().fix(self)
        self.start_instant = Instant(0)
        self.end_instant = Instant(self.get_size())
        """
        The order is IMU -> Vehicle -> Driver -> Internal
        Important as they have dependencies
        """
        self.accelerometer = imu.Accelerometer(self)
        self.gyroscope = imu.Gyroscope(self)
        self.speed = vehicle.Speed(self)
        self.dampers = vehicle.Dampers(self)
        self.ride_height = vehicle.RideHeight(self)
        self.steering_angle = driver.SteeringAngle(self)
        self.brakes = driver.Brakes(self)
        self.throttle = driver.Throttle(self)
        self.temperatures = internal.Temperatures(self)
        self.init()

    def init(self):
        self.accelerometer.calibrate()
        self.gyroscope.calibrate()
        self.steering_angle.calibrate()

    def get_original_data(self):
        return self.original_data

    def get_data(self):
        return self.original_data[:][self.get_interval().to_index()]

    def set_start_time(self, time):
        self.start_instant = Instant(time, Instant.TYPE_TIME)

    def set_end_time(self, time):
        self.end_instant = Instant(time, Instant.TYPE_TIME)

    def get_time_axis(self):
        return self.get_interval().to_time()

    def get_accelerometer(self):
        return self.accelerometer

    def get_gyroscope(self):
        return self.gyroscope

    def get_speed(self):
        return self.speed.get()

    def get_dampers(self):
        return self.dampers

    def get_ride_height(self):
        return self.ride_height

    def get_steering_angle(self):
        return self.steering_angle.get()

    def get_brakes(self):
        return self.brakes

    def get_throttle(self):
        return self.throttle.get()

    def get_temperatures(self):
        return self.temperatures

    def get_size(self):
        return len(self.original_data)

    def get_samples_count(self):
        return len(self.get_data())

    def get_duration(self):
        return self.get_samples_count() / self.F_SAMPLING

    def get_interval(self):
        return Interval(self.start_instant, self.end_instant)


class Interval:
    F_SAMPLING = Dataset.F_SAMPLING

    def __init__(self, start, end):
        """
        :type start: Instant
        :type end: Instant
        """
        self.start = start
        self.end = end

    def to_index(self):
        return np.s_[self.start.to_sample():self.end.to_sample()]

    def to_sample(self):
        return np.r_[self.start.to_sample():self.end.to_sample()]

    def to_time(self):
        return self.to_sample() / self.F_SAMPLING


class Instant:
    F_SAMPLING = Dataset.F_SAMPLING
    TYPE_SAMPLE = 0
    TYPE_TIME = 1

    def __init__(self, instant, instant_type=TYPE_SAMPLE):
        self.type = instant_type
        self.instant = instant
        if self.type == self.TYPE_TIME:
            self.instant = math.floor(instant * self.F_SAMPLING)

    def to_sample(self):
        return self.instant

    def to_time(self):
        return self.instant * self.F_SAMPLING
