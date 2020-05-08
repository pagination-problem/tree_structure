from solver import AbstractSolver

NO_LAST_TILE = -1  # index of the last column of the cost matrix


class Fptas(AbstractSolver):
    def set_engine_strategy(self, engine_name):
        if engine_name == "basic":
            self.launch_engine = self.basic_engine
            self.retrieve_solution = self.retrieve_basic_solution
        elif engine_name == "improved":
            self.launch_engine = self.improved_engine
            self.retrieve_solution = self.retrieve_improved_solution

    def set_instance(self, instance):
        self.may_reset_log()
        self.instance = instance
        self.costs = [[tile.weight] * instance.tile_count for tile in instance.tiles]
        for (new, new_tile) in enumerate(instance.tiles):
            for (last, last_tile) in enumerate(instance.tiles[:new]):
                self.costs[new][last] = sum(symbol.weight for symbol in new_tile - last_tile)

    def set_parameters(self, epsilon):
        self.epsilon = epsilon

    def run(self):
        self.grid = Grid(self.epsilon, self.instance.symbol_weight_sum, self.instance.tile_count)
        states = self.launch_engine()
        self.c_max = max(min(states, key=lambda state: max(state[0], state[1]))[:2])

    def basic_engine(self):
        states = [(0, 0, NO_LAST_TILE, NO_LAST_TILE)]
        self.may_log(states)
        for new in range(self.instance.tile_count):
            self.grid.reset()
            for (w1, w2, top1, top2) in states:
                self.grid.may_add_state((w1 + self.costs[new][top1], w2, new, top2))
                self.grid.may_add_state((w1, w2 + self.costs[new][top2], top1, new))
            states = self.grid.get_states()
            self.may_log(states)
        return states

    def retrieve_basic_solution(self):
        """Backtrack the logged states to tell which tiles are assigned to which bins."""
        log_result = self.log_result[:]
        assert log_result
        self.best_states = [min(log_result.pop(), key=lambda state: max(state[0], state[1]))]
        while log_result:
            bin1 = self.best_states[-1][0::2]
            bin2 = self.best_states[-1][1::2]
            states = log_result.pop()
            for state in states:
                if state[0::2] == bin1 or state[1::2] == bin2:
                    self.best_states.append(state)
                    break
            else:
                raise ValueError(f"Cannot match {self.best_states[-1]} in {states}.")
        bin1 = set(t for (_, _, t, _) in self.best_states if t != NO_LAST_TILE)
        bin2 = set(t for (_, _, _, t) in self.best_states if t != NO_LAST_TILE)
        assert not bin1.intersection(bin2)
        assert len(bin1.union(bin2)) == self.instance.tile_count
        return (sorted(bin1), sorted(bin2))

    def improved_engine(self):
        states = [(0, 0, NO_LAST_TILE, 2)]
        self.may_log(states)
        last1 = NO_LAST_TILE
        for new in range(self.instance.tile_count):
            self.grid.reset()
            for (w1, w2, last2, alpha) in states:
                if alpha == 1:
                    self.grid.may_add_state((w1 + self.costs[new][last1], w2, last2, 1))
                    self.grid.may_add_state((w1, w2 + self.costs[new][last2], last1, 2))
                else:
                    self.grid.may_add_state((w1 + self.costs[new][last2], w2, last1, 1))
                    self.grid.may_add_state((w1, w2 + self.costs[new][last1], last2, 2))
            last1 = new
            states = self.grid.get_states()
            self.may_log(states)
        return states

    def retrieve_improved_solution(self):
        raise NotImplementedError


class Grid:
    """Grid keeping only the “representative” states."""

    def __init__(self, epsilon, symbol_weight_sum, tile_count):
        self.delta = epsilon * symbol_weight_sum / 2 / tile_count

    def reset(self):
        self.grid = {}

    def may_add_state(self, state):
        coords = (state[0] // self.delta, state[1] // self.delta)
        key = coords + state[2:4]
        if key not in self.grid or state[:2] < self.grid[key][:2]:
            self.grid[key] = state

    def get_states(self):
        return list(self.grid.values())
