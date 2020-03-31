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
        elif engine_name == "improved":
            self.launch_engine = self.improved_engine

    def set_instance(self, instance):
        self.instance = instance
        self.costs = [[tile.weight] * instance.tile_count for tile in instance.tiles]
        for (new, new_tile) in enumerate(instance.tiles):
            for (last, lasttile) in enumerate(instance.tiles[:new]):
                self.costs[new][last] = sum(symbol.weight for symbol in new_tile - lasttile)

    def run(self, epsilon):
        self.may_reset_log()
        self.delta = (epsilon * self.instance.symbol_weight_sum) / (2 * self.instance.tile_count)
        self.tiles = sorted(self.instance.tiles, key=lambda tile: tile.leaf_index)
        selected_states = [(0, 0, NO_LAST_TILE, NO_LAST_TILE)]
        self.may_log(selected_states)
        selected_states = self.launch_engine(selected_states)
        self.c_max = max(min(selected_states, key=lambda state: max(state[0], state[1]))[:2])

    def basic_engine(self, selected_states):
        for new in range(self.instance.tile_count):
            states = []
            for (w1, w2, last1, last2) in selected_states:
                states.append((w1 + self.costs[new][last1], w2, new, last2))
                states.append((w1, w2 + self.costs[new][last2], last1, new))
            selected_states = self.select_representatives_on_grid(states)
            self.may_log(selected_states)
        return selected_states

    def improved_engine(self, selected_states):
        last1 = 0
        for new in range(self.instance.tile_count):
            states = []
            for (w1, w2, last2, alpha) in selected_states:
                if alpha == 1:
                    states.append((w1 + self.costs[new][last1 if w1 else 0], w2, last2, 1))
                    states.append((w1, w2 + self.costs[new][last2 if w2 else 0], last1, 0))
                else:
                    states.append((w1 + self.costs[new][last2 if w1 else 0], w2, last1, 1))
                    states.append((w1, w2 + self.costs[new][last1 if w2 else 0], last2, 0))
            last1 = new
            selected_states = self.select_representatives_on_grid(states)
            self.may_log(selected_states)
        return selected_states

    def select_representatives_on_grid(self, states):
        result = {}
        for state in states:
            coords = (state[0] // self.delta, state[1] // self.delta)
            if coords not in result or state < result[coords]:
                result[coords] = state
        return list(result.values())
