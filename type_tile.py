# -*- coding: utf-8 -*

from type_symbol import Symbol

class Tile:
    
    def __init__(self, symbols):
        self.symbols = set(symbols)
        self.hash = hash(tuple(self.symbols))
        temp_set_of_symbols = sorted(self.symbols)
        self.index_of_leaf = (temp_set_of_symbols.pop()).index
    
    def __str__(self):
        return "[%s]" % ", ".join(map(str, sorted(self.symbols)))
    
    def __iter__(self):
        return iter(self.symbols)
    
    def __len__(self):
        tile_size = 0
        for symbol in self.symbols :
            tile_size = tile_size + symbol.size()
        return tile_size

    def __repr__(self):
        return str(self)
    
    def __hash__(self):
        return self.hash
    
    def __eq__(self, other): #eq(a, b) is equivalent to a == b
        return self.symbols == other.symbols

    def count_on_page(self, page):
        return sum(symbol in page for symbol in self.symbols)
    
    def get_leaf_symbol(self):
        temp_set_of_symbols = sorted(self.symbols)
        return temp_set_of_symbols.pop()

    def is_included_in(self, other):
        #other must be a tile
        return self.symbols.issubset(other.symbols)
    
    def is_included_in_at_least_one_tile_of_the_set(self, tile_set) :
        for t in tile_set:
            if self.is_included_in(t):
                return True

        return False
    
    def includes_at_least_a_tile_of_the_set(self, tile_set) :
        for t in tile_set:
            if t.is_included_in(self):
                return True

        return False

    def size(self):
        tile_size = 0
        for symbol in self.symbols :
            tile_size = tile_size + symbol.size
        return tile_size