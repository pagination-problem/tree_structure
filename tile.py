from symbol import Symbols


def merge_tiles(tiles):
    return set().union(*(tile.symbols for tile in tiles))


class Tile:
    def __init__(self, symbols: Symbols):
        self.symbols = frozenset(symbols)
        self.hash = hash(tuple(self.symbols))
        self.leaf_symbol = max(self.symbols)
        self.leaf_index = self.leaf_symbol.index  # in the order of a Breadth-first search
        self.weight = sum(symbol.weight for symbol in self.symbols)
        self.string = f"{{{', '.join([str(symbol.index) for symbol in sorted(self.symbols)])}}}"

    def __str__(self):
        return self.string

    def __iter__(self):
        return iter(self.symbols)

    def __repr__(self):
        return self.string

    def __hash__(self):
        return self.hash

    def __eq__(self, other):  # a.__eq__(b) is equivalent to a == b
        return self.symbols == other.symbols

    def __sub__(self, other):
        """Return the set difference between this tile and another tile."""
        return self.symbols - other.symbols
