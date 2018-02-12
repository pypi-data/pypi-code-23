from . import Tile


class Map:
    def __init__(self, tileSize, xlen, ylen, tiles: [Tile]):
        self.tiles = tiles
        self.ylen = ylen
        self.xlen = xlen
        self.tileSize = tileSize
