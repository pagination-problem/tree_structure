# -*- coding: utf-8 -*

from type_symbol import Symbol
from type_tile import Tile
from type_page import Page
from type_problem_input import ProblemInput

FLOAT_CORRECTION = 1e-6

class Fptas:

    def set_log_strategy(self, log):
        self.log_result = []
        if log:
            self.may_log = lambda i, chi: self.log_result.append(f"{i}: {chi}")
        else:
            self.may_log = lambda *args : None

    def initialize(self, the_input):
        self.the_input = the_input
        leaf_count = 2 ** the_input.height
        self.internal_node_offset = leaf_count - 1
        self.matrix = [['x' for x in range(leaf_count+1)] for y in range(leaf_count+1)]
        tile_set = sorted(the_input.tileSet, key=lambda tile: tile.leaf_index)
        for t in tile_set:
            leaf_index_t = t.leaf_index
            i = leaf_index_t - self.internal_node_offset
            self.matrix[i][0]= len(t)
        for t1 in tile_set:
            for t2 in tile_set:
                set_of_symbols_not_assigned_yet = t1.symbols.difference(t2.symbols)
                i = t1.leaf_index - self.internal_node_offset
                j = t2.leaf_index - self.internal_node_offset
                if i >= j:
                    self.matrix[i][j] = sum(symbol.size for symbol in set_of_symbols_not_assigned_yet)

    def run(self, epsilon):
        generated_state_count = 0
        chi_seed = {(0, 0, 0, 0)}
        self.upper_bound = self.the_input.get_sum_symbol_sizes()
        self.delta = (epsilon * self.upper_bound) /  (2 * len(self.the_input))
        tile_set = sorted(self.the_input.tileSet, key=lambda tile: tile.leaf_index)
        for t in tile_set:
            chi = set()
            i = t.leaf_index - self.internal_node_offset #index (in the leaf-only index) of the tile we are about to schedule
            for (a, b, j, k) in chi_seed:
                chi.add((a + self.matrix[i][j], b, i, k))
                chi.add((a, b + self.matrix[i][k], j, i))
            generated_state_count += len(chi)
            self.may_log(i, chi)
            chi_seed = self.select_representatives_on_grid(chi)
        c_max = min(chi_seed, key=lambda state: max(state[0], state[1]))
        return (c_max, generated_state_count)
    
    def run_improved(self, epsilon):
        generated_state_count = 0
        chi_seed = {(0, 0, 0, 0)}
        self.upper_bound = self.the_input.get_sum_symbol_sizes()
        self.delta = (epsilon * self.upper_bound) /  (2 * len(self.the_input))
        tile_set = sorted(self.the_input.tileSet, key=lambda tile: tile.leaf_index)
        j = 0
        for t in tile_set:
            chi = set()
            i = t.leaf_index - self.internal_node_offset #index (in the leaf-only index) of the tile we are about to schedule
            for (a, b, k, alpha) in chi_seed:
                if alpha == 1:
                    chi.add((a + self.matrix[i][j if a else 0], b, k, 1))
                    chi.add((a, b + self.matrix[i][k if b else 0], j, 0))
                else:
                    chi.add((a + self.matrix[i][k if a else 0], b, j, 1))
                    chi.add((a, b + self.matrix[i][j if b else 0], k, 0))
            j = i
            generated_state_count += len(chi)
            self.may_log(i, chi)
            chi_seed = self.select_representatives_on_grid(chi)
        c_max = min(chi_seed, key=lambda state: max(state[0], state[1]))
        return (c_max, generated_state_count)

    def select_representatives_on_grid(self, states):
        result = {}
        for state in states:
            coords = (int(state[0] / self.delta), int(state[1] / self.delta))
            if coords not in result or state[0] < result[coords][0]:
                result[coords] = state
        return set(result.values())
