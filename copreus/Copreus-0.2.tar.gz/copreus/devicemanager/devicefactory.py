import copreus.drivers
import importlib

class DriverFactory:
    @staticmethod
    def create(config, verbose, spi_lock=None):
        """Static driver factory - takes a driver entry from json/yaml config and instantiates the corresponding
        Class. Classes that are specializations of ASPI are provided with the spi_lock (if one is provided to this
        factory).

        New implemented driver must be added manually."""
        type_name = config["type"].upper()

        # it is on purpose that not class names are used to be compared with type_name (as will be done within the
        # constructor of the base class ADriver). This approach allows for late binding - thus, a class is imported
        # if and only if it is needed which results in less dependencies that must be fullfilled although they might
        # not be needed.

        drivers = copreus.drivers.get_drivers()

        try:
            driver = drivers[type_name]
            mod = importlib.import_module(driver["module"])
            klass = getattr(mod, driver["name"])
            if "ASPI" in driver["bases"]:
                result = klass(config, verbose, spi_lock)
            else:
                result = klass(config, verbose)
        except:
            raise ValueError("unknown type name '{}'.".format(type_name))

        return result

    @staticmethod
    def old_create(config, verbose, spi_lock=None):
        type_name = config["type"].upper()
        if type_name == "ADC":
            from copreus.drivers.adc import ADC
            result = ADC(config, verbose, spi_lock)
        elif type_name == "DAC":
            from copreus.drivers.dac import DAC
            result = DAC(config, verbose, spi_lock)
        elif type_name == "BME_280":
            from copreus.drivers.bme_280 import BME_280
            result = BME_280(config, verbose)
        elif type_name == "DHT":
            from copreus.drivers.dht import DHT
            result = DHT(config, verbose)
        elif type_name == "EPAPER":
            from copreus.drivers.epaper import EPaper
            result = EPaper(config, verbose, spi_lock)
        elif type_name == "INPUT":
            from copreus.drivers.input import Input
            result = Input(config, verbose)
        elif type_name == "OUTPUT":
            from copreus.drivers.output import Output
            result = Output(config, verbose)
        elif type_name == "ROTARYENCODER":
            from copreus.drivers.rotaryencoder import RotaryEncoder
            result = RotaryEncoder(config, verbose)
        else:
            raise ValueError("unknown type name '{}'.".format(type_name))

        return result


