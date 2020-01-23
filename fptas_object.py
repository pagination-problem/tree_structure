from type_symbol import Symbol
from type_tile import Tile
from type_page import Page
from type_problem_input import ProblemInput

class Fptas:
    
    def set_log_strategy(self, log):
        self.log_result = []
        if log:
            self.may_reset_log = lambda: self.log_result.clear()
            self.may_log = lambda i, chi: self.log_result.append(f"{i}: {sorted(chi)}")
        else:
            self.may_reset_log = lambda: None
            self.may_log = lambda *args: None
    
    def set_engine_strategy(self, engine_name):
        if engine_name == "basic":
            self.launch_engine = self.basic_engine
        elif engine_name == "improved":
            self.launch_engine = self.improved_engine

    def set_instance(self, instance):
        self.instance = instance
        leaf_count = 2 ** instance.height
        self.internal_node_offset = leaf_count - 1
        self.matrix = [['x' for x in range(leaf_count+1)] for y in range(leaf_count+1)]
        tiles = sorted(instance.tileSet, key=lambda tile: tile.leaf_index)
        for t in tiles:
            i = t.leaf_index - self.internal_node_offset
            self.matrix[i][0]= len(t)
        for t1 in tiles:
            for t2 in tiles:
                set_of_symbols_not_assigned_yet = t1.symbols.difference(t2.symbols)
                i = t1.leaf_index - self.internal_node_offset
                j = t2.leaf_index - self.internal_node_offset
                if i >= j:
                    self.matrix[i][j] = sum(symbol.size for symbol in set_of_symbols_not_assigned_yet)

    def run(self, epsilon):
        self.may_reset_log()
        self.generated_state_count = 0
        self.upper_bound = self.instance.get_sum_symbol_sizes()
        self.delta = (epsilon * self.upper_bound) /  (2 * len(self.instance))
        self.tiles = sorted(self.instance.tileSet, key=lambda tile: tile.leaf_index)
        chi_seed = [(0, 0, 0, 0)]
        self.launch_engine(chi_seed)
        self.c_max = max(min(chi_seed, key=lambda state: max(state[0], state[1]))[:2])

    def basic_engine(self, chi_seed):
        for t in self.tiles:
            chi = []
            i = t.leaf_index - self.internal_node_offset
            for (a, b, j, k) in chi_seed:
                chi.append((a + self.matrix[i][j], b, i, k))
                chi.append((a, b + self.matrix[i][k], j, i))
            self.generated_state_count += len(chi)
            chi_seed = self.select_representatives_on_grid(chi)
            self.may_log(i, chi_seed)

    def improved_engine(self, chi_seed):
        j = 0
        for t in self.tiles:
            chi = []
            i = t.leaf_index - self.internal_node_offset
            for (a, b, k, alpha) in chi_seed:
                if alpha == 1:
                    chi.append((a + self.matrix[i][j if a else 0], b, k, 1))
                    chi.append((a, b + self.matrix[i][k if b else 0], j, 0))
                else:
                    chi.append((a + self.matrix[i][k if a else 0], b, j, 1))
                    chi.append((a, b + self.matrix[i][j if b else 0], k, 0))
            j = i
            self.generated_state_count += len(chi)
            chi_seed = self.select_representatives_on_grid(chi)
            self.may_log(i, chi_seed)

    def select_representatives_on_grid(self, states):
        result = {}
        for state in states:
            coords = (int(state[0] / self.delta), int(state[1] / self.delta))
            if coords not in result or state < result[coords]:
                result[coords] = state
        return list(result.values())
