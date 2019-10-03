# -*- coding: utf-8 -*

from type_symbol import Symbol

class Tile:
    
    def __init__(self, symbols):
        self.symbols = set(symbols)
        self.hash = hash(tuple(self.symbols))
        self.leaf_symbol = max(self.symbols, key=lambda symbol: symbol.index)
        self.leaf_index = self.leaf_symbol.index # in the order of a Breadth-first search
    
    def __str__(self):
        return "[%s]" % ", ".join(map(str, sorted(self.symbols)))
    
    def __iter__(self):
        return iter(self.symbols)
    
    def __len__(self):
        return sum(symbol.size for symbol in self.symbols)

    def __repr__(self):
        return str(self)
    
    def __hash__(self):
        return self.hash
    
    def __eq__(self, other): #eq(a, b) is equivalent to a == b
        return self.symbols == other.symbols

    def count_on_page(self, page):
        return len(symbol in page for symbol in self.symbols)

    # def is_included_in(self, other):
    #     #other must be a tile
    #     return self.symbols.issubset(other.symbols)
    
    # def is_included_in_at_least_one_tile_of_the_set(self, tile_set):
    #     for t in tile_set:
    #         if self.is_included_in(t):
    #             return True

    #     return False
    
    # def includes_at_least_a_tile_of_the_set(self, tile_set):
    #     for t in tile_set:
    #         if t.is_included_in(self):
    #             return True

    #     return False
