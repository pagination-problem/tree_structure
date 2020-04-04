NO_LAST_TILE = -1  # index of the last column of the cost matrix


class Fptas:
    def set_log_strategy(self, log):
        self.log_result = []
        if log:
            self.may_reset_log = lambda: self.log_result.clear()
            self.may_log = lambda states: self.log_result.append(states)
        else:
            self.may_reset_log = lambda: None
            self.may_log = lambda *args: None

    def set_engine_strategy(self, engine_name):
        if engine_name == "basic":
            self.launch_engine = self.basic_engine
            self.reconstruct_solution = self.reconstruct_basic_solution
        elif engine_name == "improved":
            self.launch_engine = self.improved_engine
            self.reconstruct_solution = self.reconstruct_improved_solution

    def set_instance(self, instance):
        self.instance = instance
        self.costs = [[tile.weight] * instance.tile_count for tile in instance.tiles]
        for (new, new_tile) in enumerate(instance.tiles):
            for (last, lasttile) in enumerate(instance.tiles[:new]):
                self.costs[new][last] = sum(symbol.weight for symbol in new_tile - lasttile)

    def run(self, epsilon):
        self.may_reset_log()
        self.delta = (epsilon * self.instance.symbol_weight_sum) / (2 * self.instance.tile_count)
        selected_states = self.launch_engine()
        self.c_max = max(min(selected_states, key=lambda state: max(state[0], state[1]))[:2])

    def basic_engine(self):
        selected_states = [(0, 0, NO_LAST_TILE, NO_LAST_TILE)]
        self.may_log(selected_states)
        for new in range(self.instance.tile_count):
            states = []
            for (w1, w2, last1, last2) in selected_states:
                states.append((w1 + self.costs[new][last1], w2, new, last2))
                states.append((w1, w2 + self.costs[new][last2], last1, new))
            selected_states = self.select_representatives_on_grid(states)
            self.may_log(selected_states)
        return selected_states

    def reconstruct_basic_solution(self):
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
        selected_states = [(0, 0, NO_LAST_TILE, 2)]
        self.may_log(selected_states)
        last1 = NO_LAST_TILE
        for new in range(self.instance.tile_count):
            states = []
            for (w1, w2, last2, alpha) in selected_states:
                if alpha == 1:
                    states.append((w1 + self.costs[new][last1], w2, last2, 1))
                    states.append((w1, w2 + self.costs[new][last2], last1, 2))
                else:
                    states.append((w1 + self.costs[new][last2], w2, last1, 1))
                    states.append((w1, w2 + self.costs[new][last1], last2, 2))
            last1 = new
            selected_states = self.select_representatives_on_grid(states)
            self.may_log(selected_states)
        return selected_states

    def reconstruct_improved_solution(self):
        raise NotImplementedError

    def select_representatives_on_grid(self, states):
        result = {}
        for state in states:
            coords = (state[0] // self.delta, state[1] // self.delta)
            if coords not in result or state < result[coords]:
                result[coords] = state
        return list(result.values())
