import time
from multiprocessing import RLock
from pyconnectedcars.connection import Connection
from pyconnectedcars.Fuel import Fuel
from pyconnectedcars.Lock import Lock
from pyconnectedcars.BinarySensor import SystemsAreOkSensor, OilLevelIsOkSensor, TirePressureIsOkSensor, BatteryChargeIsOkSensor
from pyconnectedcars.GPS import GPS, Odometer


class Controller:
    def __init__(self, email, password, update_interval):
        self.__connection = Connection(email, password)
        self.__vehicles = []
        self.update_interval = update_interval
        self.__car = {}
        self.__last_update_time = 0
        self.__lock = RLock()
        self.update()
        for car_id, car in self.__car.items():
            self.__vehicles.append(Fuel(car, self))
            self.__vehicles.append(Lock(car, self))
            self.__vehicles.append(GPS(car, self))
            self.__vehicles.append(Odometer(car, self))
            self.__vehicles.append(SystemsAreOkSensor(car, self))
            self.__vehicles.append(OilLevelIsOkSensor(car, self))
            self.__vehicles.append(TirePressureIsOkSensor(car, self))
            self.__vehicles.append(BatteryChargeIsOkSensor(car, self))

    def get(self):
        self.__last_update_time = time.time()
        return self.__connection.get_data()

    def list_vehicles(self):
        return self.__vehicles

    def update(self):
        cur_time = time.time()
        with self.__lock:
            if cur_time - self.__last_update_time > self.update_interval:
                data = self.get()
                if data and data['data']:
                    for car_data in data['data']['user']['cars']:
                        self.__car[car_data['id']] = car_data
                else:
                    self.__car = {}

    def get_car_params(self, car_id):
        return self.__car[car_id]
