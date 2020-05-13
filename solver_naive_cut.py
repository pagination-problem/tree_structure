"""
Partition the tile list into the best two lists of CONSECUTIVE tiles.

Due to the hierarchy constraint, the optimal solution tends to partition the tiles in such
a way that most tiles of bin1 have an index lesser than that of all tiles of bin2. This
simple linear search finds the “cut” i minimizing |weight(tiles[:i]) - weight(tiles[i:])|.
"""

from abstract_solver import AbstractSolver
from tile import merge_tiles

class Solver(AbstractSolver):

    def run(self):
        weight = lambda t: sum(symbol.weight for symbol in merge_tiles(t))
        tiles = self.instance.tiles
        differences = [abs(weight(tiles[:i]) - weight(tiles[i:])) for i in range(len(tiles))]
        minimal_difference = min(differences)
        i = differences.index(minimal_difference)
        self.solution = i
        self.c_max = max(weight(tiles[:i]), weight(tiles[i:]))
        self.step_count = "N/A"
        return self.c_max

    def retrieve_solution(self):
        i = self.solution
        return (list(range(i)), list(range(i, len(self.instance.tiles))))
