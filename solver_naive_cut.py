"""
Partition the tile list into the best two lists of CONSECUTIVE tiles.

Due to the hierarchy constraint, the optimal solution tends to partition the tiles in such
a way that most tiles of bin1 have an index lesser than that of all tiles of bin2. This
simple linear search finds the “cut” i minimizing |weight(tiles[:i]) - weight(tiles[i:]|.
"""

from solver import AbstractSolver


class NaiveCut(AbstractSolver):
    def run(self):
        def weight(tiles):
            symbols = set().union(*(tile.symbols for tile in tiles))
            return sum(symbol.weight for symbol in symbols)

        tiles = self.instance.tiles
        differences = [abs(weight(tiles[:i]) - weight(tiles[i:])) for i in range(len(tiles))]
        self.may_log(tuple(differences))
        minimal_difference = min(differences)
        i = differences.index(minimal_difference)
        self.may_log(i)
        self.c_max = max(weight(tiles[:i]), weight(tiles[i:]))

    def retrieve_solution(self):
        assert self.log_result
        i = self.log_result[-1]
        return (list(range(i)), list(range(i, len(self.instance.tiles))))
