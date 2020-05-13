from abstract_solver import AbstractSolver

NO_LAST_TILE = -1  # index of the last column of the cost matrix


class Solver(AbstractSolver):
    def __init__(self, parameters):
        self.store = StateStore(parameters)

    def set_instance(self, instance):
        self.may_reset_log()
        self.tile_count = instance.tile_count
        self.tiles = instance.tiles
        self.costs = [[tile.weight] * self.tile_count for tile in self.tiles]
        for (new, new_tile) in enumerate(self.tiles):
            for (last, last_tile) in enumerate(self.tiles[:new]):
                self.costs[new][last] = sum(symbol.weight for symbol in new_tile - last_tile)
        self.store.set_instance(instance)

    def run(self):
        self.step_count = 0
        states = [(self.tiles[0].weight, 0, 0, NO_LAST_TILE)]
        self.may_log(states)
        may_add_state = self.store.may_add_state
        for new in range(1, self.tile_count):
            self.store.reset()
            cost = self.costs[new]
            for (w1, w2, top1, top2) in states:
                may_add_state(w1 + cost[top1], w2, new, top2)
                may_add_state(w1, w2 + cost[top2], top1, new)
            states = self.store.get_states()
            self.step_count += len(states)
            self.may_log(states)
        min_state = min(states, key=lambda state: max(state[:2]))
        return max(min_state[:2])

    def retrieve_solution(self):
        """Backtrack the logged states to tell which tiles are assigned to which bins."""
        log_result = self.log_result[:]
        assert log_result
        self.best_states = [min(log_result.pop(), key=lambda state: max(state[0], state[1]))]
        while log_result:
            best_state = self.best_states[-1]
            bin1 = [best_state[0], best_state[2]]
            bin2 = [best_state[1], best_state[3]]
            states = log_result.pop()
            for state in states:
                if bin1 == [state[0], state[2]] or bin2 == [state[1], state[3]]:
                    self.best_states.append(state)
                    break
            else:
                raise ValueError(f"Cannot match {self.best_states[-1]} in {states}.")
        bin1 = set(state[2] for state in self.best_states if state[2] != NO_LAST_TILE)
        bin2 = set(state[3] for state in self.best_states if state[3] != NO_LAST_TILE)
        assert not bin1.intersection(bin2)
        assert len(bin1.union(bin2)) == self.tile_count
        return (sorted(bin1), sorted(bin2))


class StateStore:
    """Collection of states generated during one step of the FPTAS."""

    def __init__(self, parameters):
        self.parameters = parameters

        if parameters.get("hash_epsilon"):
            self.empty_store = lambda: {}
            self.may_set_instance_hash_parameters = self._set_instance_hash_parameters
            self.may_add_state = self._may_add_hashed_state
            self.get_states = lambda: self.store.values()
        else:
            self.empty_store = lambda: []
            self.may_set_instance_hash_parameters = lambda _: None
            self.may_add_state = self._add_raw_state
            self.get_states = lambda: self.store

        if parameters.get("c_max_bound_calculator"):
            # Set up the computation of a c_max upper bound by a given (supposedly fast) heuristics
            self.c_max_bound_calculator = __import__(parameters["c_max_bound_calculator"]).Solver()
            self.c_max_bound_calculator.set_log_strategy(False)  # no need to track the heuristics
            self.may_compute_c_max_bound = self._compute_c_max_bound
            # insert a filter with c_max bound before the call of the current may_add_state method
            self.may_add_state_after_c_max_bound_check = self.may_add_state
            self.may_add_state = self._may_add_state_with_c_max_bound_check
        else:
            self.may_compute_c_max_bound = lambda _: None

    def set_instance(self, instance):
        self.may_set_instance_hash_parameters(instance)
        self.may_compute_c_max_bound(instance)

    def reset(self):
        self.store = self.empty_store()

    # With hash

    def _set_instance_hash_parameters(self, instance):
        epsilon = self.parameters["hash_epsilon"]
        self.delta = epsilon * instance.symbol_weight_sum / 2 / instance.tile_count

    def _may_add_hashed_state(self, w1, w2, i1, i2):
        key = (w1 // self.delta, w2 // self.delta, i1, i2)
        if key not in self.store or (w1, w2) < self.store[key]:
            self.store[key] = (w1, w2, i1, i2)

    # Without hash

    def _add_raw_state(self, w1, w2, i1, i2):
        self.store.append((w1, w2, i1, i2))

    # With c_max_bound filtering

    def _compute_c_max_bound(self, instance):
        self.c_max_bound_calculator.set_instance(instance)
        self.c_max_bound = self.c_max_bound_calculator.run()

    def _may_add_state_with_c_max_bound_check(self, w1, w2, i1, i2):
        if w1 <= self.c_max_bound and w2 <= self.c_max_bound:
            self.may_add_state_after_c_max_bound_check(w1, w2, i1, i2)
