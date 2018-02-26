import math
import socket
from iglo.helpers import Helpers

MODE_OFF              = 0
MODE_RGB              = 1
MODE_WHITE            = 2
MODE_EFFECT           = 3

CODE_COLOUR           = 161
CODE_RGB_BRIGHTNESS   = 162
CODE_POWER            = 163
CODE_EFFECT           = 165
CODE_WHITE_BRIGHTNESS = 167

MIN_KELVIN            = 2700
MAX_KELVIN            = 6500

EFFECTS = {
  'candle': 1,
  'warm_white': 2,
  'natural_white': 3,
  'snow_white': 4,
  'sleep': 5,
  'relax': 6,
  'reading': 7,
  'work': 8,

  'whites': 12,
  'rainbow': 13,
  'rainbow_chase': 14,
  'romance': 15,
  'waves': 17,
  'forest': 18
}

class Lamp(object):
  """
  This represents a lamp to control
  """

  def __init__(self, id, ip, port=8080):
    """
    :type id int:
    :type ip string:
    :type port int:
    :return:
    """
    self._id = id
    self._ip = ip
    self._port = port
    self._on = True
    self._mode = MODE_WHITE
    self._effect = ''
    self._white = MAX_KELVIN
    self._rgb = (0, 0, 0)
    self._brightness = {
      MODE_WHITE: 200,
      MODE_RGB: 200,
      MODE_EFFECT: 200
    }

  def switch(self, on):
    on_data = 18
    if on:
      on_data = 17
    self._on = on
    data = [CODE_POWER, self._id, on_data]
    self._send(data)

  def white(self, kelvin):
    """Supports between 2700K and 6500K white
    :type kelvin int:
    """
    whiteness = int(((kelvin - MIN_KELVIN) * 255)/(MAX_KELVIN-MIN_KELVIN))
    whiteness = max(min(whiteness,255),0)
    data = [CODE_COLOUR, self._id, 255 - whiteness, whiteness]
    self._mode = MODE_WHITE
    self._white = kelvin
    self._effect = ''
    self._send(data)

  def brightness(self, brightness):
    data = [CODE_RGB_BRIGHTNESS, self._id, brightness]
    if self._mode is MODE_WHITE:
      data[0] = CODE_WHITE_BRIGHTNESS
    self._brightness[self._mode] = brightness
    self._send(data)

  def rgb(self, r, g, b):
    data = [CODE_COLOUR, self._id, r, g, b]
    self._mode = MODE_RGB
    self._rgb = (r, g, b)
    self._effect = ''
    self._send(data)

  def state(self):
    return {
      'on': self._on,
      'mode': self._mode,
      'brightness': self._brightness[self._mode],
      'rgb': self._rgb,
      'white': self._white,
      'effect': self._effect
    }

  def _send(self, data):
    data_bytes = bytearray(Helpers.int_array_to_byte_array([-2, -17, len(data) + 1]))
    data_bytes.extend(Helpers.int_array_to_byte_array(data))
    checksum = 0
    for i in data:
      checksum += i
    data_bytes.append((checksum % 256) ^ 255)
    sock = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
    sock.connect((self._ip, self._port))
    sock.send(data_bytes)
    sock.close()
    sock = None

  @property
  def min_kelvin(self):
    return MIN_KELVIN

  @property
  def max_kelvin(self):
    return MAX_KELVIN

  @property
  def effect_list(self):
    return list(EFFECTS.keys())

  def effect(self, effect):
    if effect in self.effect_list:
      data = [CODE_EFFECT, self._id, EFFECTS[effect]]
      self._mode = MODE_EFFECT
      self._effect = effect
      self._send(data)
