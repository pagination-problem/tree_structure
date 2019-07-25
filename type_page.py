# -*- coding: utf-8 -*

from type_tile import Tile

class Page:
    
    def __init__(self):
        self.used_capacity = 0
        self.symbols = set()
        self.tiles = set()

    def __repr__(self):
        return str(self)

    def add_tile(self, tile):
        self.tiles.add(tile)
        for s in tile:
            self.symbols.add(s)
    
    def __contains__(self, symbol_or_tile):
        if isinstance(symbol_or_tile, Tile):
            return symbol_or_tile in self.tiles
        else:
            return symbol_or_tile in self.symbols
    
    def __str__(self):
        return "{ " + " ; ".join(str(tile) for tile in self) + " }"
    
    def __iter__(self):
        return iter(self.tiles)
    
    def tile_count(self):
        return len(self.tiles)
    
    def symbol_count(self):
        return len(self.symbols)