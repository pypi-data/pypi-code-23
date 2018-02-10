from models import Coordinate, Direction


class Bullet:
    def __init__(self, coordinates: Coordinate, direction: Direction, size):
        self.size = size
        self.direction = direction
        self.coordinates = coordinates