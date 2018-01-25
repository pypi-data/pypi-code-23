from serial import Serial
from time import sleep

class WallDisplay(Serial):
  def __init__(self, device):
    Serial.__init__(self, device)
    self.baudrate = 2400

  def safeWrite(self, msg):
    for char in msg:
      self.write(char.encode())
      sleep(0.02)

  def allOn(self):
    self.safeWrite("allon\n")

  def allOff(self):
    self.safeWrite("alloff\n")

  def flash(self):
    self.safeWrite("allflash\n")

  def print(self, msg):
    msg = msg.split("\n")
    if len(msg) > 2:
      raise Exception("No more then 2 lines can be controlled using one serial connection.")
    elif len(msg) == 2:
      self.safeWrite("\"%s\n"%(msg[0] + (" "*(24-len(msg[0]))) + msg[1]))
    else:
      self.safeWrite("\"%s\n"%(msg[0]))
