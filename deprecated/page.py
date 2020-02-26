from symbol import Symbol
from typing import Union

from tile import Tile


class Page:
    def __init__(self):
        self.symbols = set()
        self.tiles = set()

    def add_tile(self, tile: Tile):
        self.tiles.add(tile)
        for s in tile:
            self.symbols.add(s)

    def __contains__(self, x: Union[Tile, Symbol]):
        if isinstance(x, Tile):
            return x in self.tiles
        else:
            return x in self.symbols

    def __str__(self):
        return f"{{{', '.join(map(str, self.tiles))}}}"

    def __iter__(self):
        return iter(self.tiles)

    def tile_count(self):
        return len(self.tiles)

    def symbol_count(self):
        return len(self.symbols)
