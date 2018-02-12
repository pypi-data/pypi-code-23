from . import Direction


class Controls:
    def __init__(self, direction: Direction, shooting, running):
        self.running = running
        self.shooting = shooting
        self.direction = direction
