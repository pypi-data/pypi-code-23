from . import Coordinate


class Pod:
    def __init__(self, coordinates: Coordinate, respawn, size):
        self.size = size
        self.respawn = respawn
        self.coordinates = coordinates