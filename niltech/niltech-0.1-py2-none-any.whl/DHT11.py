
import dht11
import time




# read data using pin 2

def read(pin):
    instance = dht11.DHT11(pin)
    while True:
        result = instance.read()
        if result.is_valid():
            
            return result.temperature,result.humidity
            break

        time.sleep(0.5)
