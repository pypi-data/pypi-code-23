from . import Colors, Coordinate, Powerup, Controls


class Bot:
    def __init__(self, id, name, colors: Colors, coordinate: Coordinate, controls: Controls, maxHp, hp,
                 powerup: Powerup, status, size, magazine, respawn):
        self.respawn = respawn
        self.magazine = magazine
        self.size = size
        self.status = status
        self.powerup = powerup
        self.hp = hp
        self.maxHp = maxHp
        self.controls = controls
        self.coordinate = coordinate
        self.colors = colors
        self.name = name
        self.id = id
