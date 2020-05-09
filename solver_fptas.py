from solver import AbstractSolver

NO_LAST_TILE = -1  # index of the last column of the cost matrix


class Fptas(AbstractSolver):
    def set_engine_strategy(self, engine_name):
        if engine_name == "basic":
            self.launch_engine = self.basic_engine
        elif engine_name == "improved":
            self.launch_engine = self.improved_engine
        elif engine_name == "basic_with_c_max_bound":
            self.launch_engine = self.basic_engine_with_c_max_bound

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
        self.step_count = 0
        states = self.launch_engine()
        self.c_max = max(min(states, key=lambda state: max(state[0], state[1]))[:2])
    
    def basic_engine_with_c_max_bound(self):
        bound_calculator = __import__("solver_naive_cut").NaiveCut()
        bound_calculator.set_log_strategy(False)
        bound_calculator.set_instance(self.instance)
        bound_calculator.run()
        c_max_bound = bound_calculator.c_max
        self.grid.set_c_max_bound(c_max_bound)
        return self.basic_engine()

    def basic_engine(self):
        states = [(self.instance.tiles[0].weight, 0, 0, NO_LAST_TILE)]
        self.may_log(states)
        for new in range(1, self.instance.tile_count):
            self.grid.reset()
            for (w1, w2, top1, top2) in states:
                self.grid.may_add_state((w1 + self.costs[new][top1], w2, new, top2))
                self.grid.may_add_state((w1, w2 + self.costs[new][top2], top1, new))
            states = self.grid.get_states()
            self.step_count += len(states)
            self.may_log(states)
        return states

    def improved_engine(self):
        states = [(self.instance.tiles[0].weight, 0, NO_LAST_TILE, 1, 0, NO_LAST_TILE)]
        self.may_log(states)
        last1 = 0
        for new in range(1, self.instance.tile_count):
            self.grid.reset()
            for (w1, w2, last2, alpha, top1, top2) in states:
                if alpha == 1:
                    self.grid.may_add_state((w1 + self.costs[new][last1], w2, last2, 1, new, top2))
                    self.grid.may_add_state((w1, w2 + self.costs[new][last2], last1, 2, top1, new))
                else:
                    self.grid.may_add_state((w1 + self.costs[new][last2], w2, last1, 1, new, top2))
                    self.grid.may_add_state((w1, w2 + self.costs[new][last1], last2, 2, top1, new))
            last1 = new
            states = self.grid.get_states()
            self.step_count += len(states)
            self.may_log(states)
        return states

    def retrieve_solution(self):
        """Backtrack the logged states to tell which tiles are assigned to which bins."""
        log_result = self.log_result[:]
        assert log_result
        self.best_states = [min(log_result.pop(), key=lambda state: max(state[0], state[1]))]
        while log_result:
            best_state = self.best_states[-1]
            bin1 = [best_state[0], best_state[-2]]
            bin2 = [best_state[1], best_state[-1]]
            states = log_result.pop()
            for state in states:
                if bin1 == [state[0], state[-2]] or bin2 == [state[1], state[-1]]:
                    self.best_states.append(state)
                    break
            else:
                raise ValueError(f"Cannot match {self.best_states[-1]} in {states}.")
        bin1 = set(state[-2] for state in self.best_states if state[-2] != NO_LAST_TILE)
        bin2 = set(state[-1] for state in self.best_states if state[-1] != NO_LAST_TILE)
        assert not bin1.intersection(bin2)
        assert len(bin1.union(bin2)) == self.instance.tile_count
        return (sorted(bin1), sorted(bin2))


class Grid:
    """Grid keeping only the “representative” states."""

    def __init__(self, epsilon, symbol_weight_sum, tile_count):
        self.delta = epsilon * symbol_weight_sum / 2 / tile_count
        self.may_add_state = self.may_add_state_without_bound_check

    def set_c_max_bound(self, c_max_bound):
        """If a c_max is already known, use its value to cut states."""
        self.c_max_bound = c_max_bound
        self.may_add_state = self.may_add_state_with_bound_check

    def reset(self):
        self.grid = {}

    def may_add_state_with_bound_check(self, state):
        if state[0] <= self.c_max_bound and state[1] <= self.c_max_bound:
            self.may_add_state_without_bound_check(state)

    def may_add_state_without_bound_check(self, state):
        coords = (state[0] // self.delta, state[1] // self.delta)
        key = coords + state[2:4]
        if key not in self.grid or state[:2] < self.grid[key][:2]:
            self.grid[key] = state

    def get_states(self):
        return list(self.grid.values())
