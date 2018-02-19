import RPi.GPIO as GPIO
GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)
import dht11
import time




# read data using pin 2

def read(pin):
    instance = dht11.DHT11(pin)
    for i in range(6):
        result = instance.read()
        if result.is_valid():
            return result.temperature,result.humidity
            break
        time.sleep(0.5)
    return 0,0





