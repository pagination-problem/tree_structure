from functools import partial
import struct

from abstract_solver import AbstractSolver
from tile import merge_tiles


class Solver(AbstractSolver):
    """Dynamic programming solver, with optional FPATS and pruning."""

    def __init__(self, params):
        self.store = StateStore(params)

    def set_instance(self, instance):
        self.may_reset_log()
        self.tile_count = instance.tile_count
        self.tiles = instance.tiles
        self.costs = instance.costs
        self.no_top_tile = self.tile_count
        self.store.set_instance(instance)

    def run(self):
        """Compute and return the c_max of the setted instance."""
        l = list()
        l.append(0)
        states = [(self.tiles[0].weight, 0, 0, self.no_top_tile, l)] #
        self.step_count = 1
        self.may_log(states)
        add_state = self.store.add_state  # micro-optimize attribute access
        for new in range(1, self.tile_count):
            self.store.cleanup_states()
            costs = self.costs[new]  # micro-optimize element access
            for (w1, w2, top1, top2, tiles_on_P1) in states:  # bottleneck of the solver #
                new_list_on_P1 = tiles_on_P1.copy()
                new_list_on_P1.append(new)
                add_state(w1 + costs[top1], w2, new, top2, new_list_on_P1)#
                add_state(w1, w2 + costs[top2], top1, new, tiles_on_P1)#
            states = self.store.get_states()
            self.step_count += len(states)
            self.may_log(states)
        min_state = min(states, key=lambda state: max(state[:2]))
        self.c_max = max(min_state[:2])
        # return self.c_max
        # Need to return c_max AND the state to reconstruction if needed
        return (self.c_max, min_state)

    def _run (self):
        print("Ctypes")

    def retrieve_solution(self):
        """Backtrack the logged states to tell which tiles are assigned to which bins."""
        assert self.log_result, "could not retrieve the solution when logging is disabled."
        self.best_states = [min(self.log_result[-1], key=lambda state: max(state[0], state[1]))]
        new = len(self.log_result) - 1
        for states in reversed(self.log_result[:-1]):
            best_state = self.best_states[-1]
            for state in states:
                if (
                    best_state[0] > state[0]
                    and best_state[1] == state[1]
                    and best_state[3] == state[3]
                ) or (
                    best_state[1] > state[1]
                    and best_state[0] == state[0]
                    and best_state[2] == state[2]
                ):
                    self.best_states.append(state)
                    break
            else:
                raise ValueError(f"cannot match {self.best_states[-1]} in {states}.")
            new -= 1
        tiles1 = set(state[2] for state in self.best_states if state[2] != self.no_top_tile)
        tiles2 = set(state[3] for state in self.best_states if state[3] != self.no_top_tile)
        w1 = sum(symbol.weight for symbol in merge_tiles(self.tiles[i] for i in tiles1))
        w2 = sum(symbol.weight for symbol in merge_tiles(self.tiles[i] for i in tiles2))
        c_max = max(w1, w2)
        assert not tiles1.intersection(tiles2), "the two bins have some tiles in common."
        assert len(tiles1.union(tiles2)) == self.tile_count, "some tiles were not assigned."
        # assert self.c_max == c_max, f"c_max: {self.c_max} (calculated) ≠ {c_max} (retrieved)."
        return (sorted(tiles1), sorted(tiles2))


class StateStore:
    """Facade layer for a collection of states generated during one step of the FPTAS."""

    def __init__(self, params):
        if params.get("hash_epsilon"):
            if params.get("redis"):
                adder = HashAdderRedis(params)
            elif params.get("mini"):
                adder = HashAdderMini(params)
            else:
                adder = HashAdder(params)
        else:
            adder = RawAdder()
        self.cleanup_states = adder.cleanup_states
        self.get_states = adder.get_states
        pruner = BoundPruner(adder, params) if params.get("c_max_pruner") else NoPruner(adder)
        self.set_instance = pruner.set_instance
        self.add_state = pruner.add_state


class RawAdder:
    """Structure storing a list of states, with no comparison needed before addition."""

    def set_instance(self, instance):
        pass

    def cleanup_states(self):
        self.store = []

    def add_state(self, w1, w2, i1, i2, tiles_on_P1): #
        self.store.append((w1, w2, i1, i2, tiles_on_P1)) 

    def get_states(self):
        return self.store


class HashAdder:
    """Structure storing a dict of states, with hash comparison before each addition."""

    __slots__ = ["delta", "store", "epsilon"] # micro-optimization

    def __init__(self, params):
        self.epsilon = params["hash_epsilon"]

    def set_instance(self, instance):
        self.delta = self.epsilon * instance.symbol_weight_sum / 2 / instance.tile_count

    def cleanup_states(self):
        self.store = {}

    def add_state(self, w1, w2, i1, i2, tiles_on_P1): #
        # the next expression micro-optimized the integer division
        key = ((w1 / self.delta).__trunc__(), (w2 / self.delta).__trunc__(), i1, i2)
        if key not in self.store or (w1, w2) < self.store[key]:
            self.store[key] = (w1, w2, i1, i2, tiles_on_P1) #

    def get_states(self):
        return self.store.values()


class HashAdderMini(HashAdder):
    """Structure storing a dict of states, with hash comparison before each addition."""

    __slots__ = ["store"] # micro-optimization

    def set_instance(self, instance):
        pass

    def add_state(self, w1, w2, i1, i2, tiles_on_P1):#
        key = (w1, i1, i2)
        if key not in self.store or w2 < self.store[key][1]:
            self.store[key] = (w1, w2, i1, i2, tiles_on_P1)#


class HashAdderRedis(HashAdder):
    """Experimental variation of HashAdder with Redis for backend."""

    pack = partial(struct.pack, "HHHH") # H denotes an unsigned short (generally 2 bytes)
    unpack = partial(struct.unpack, "HHHH") # H denotes an unsigned short (generally 2 bytes)

    def __init__(self, params):
        redis = __import__("redis").StrictRedis
        self.store = redis(host="localhost", port=6379, db=3)
        self.store.config_set("save", "") # disable RDB persistence
        self.store.config_set("appendonly", "no") # disable AOF persistence
        HashAdder.__init__(self, params)

    def cleanup_states(self):
        self.store.flushdb()

    def add_state(self, w1, w2, i1, i2):
        key = self.pack(int(w1 // self.delta), int(w2 // self.delta), i1, i2)
        if not self.store.exists(key) or (w1, w2) < self.unpack(self.store.get(key)):
            self.store.set(key, self.pack(w1, w2, i1, i2))

    def get_states(self):
        return list(map(self.unpack, self.store.mget(self.store.scan_iter())))


class NoPruner:
    def __init__(self, adder):
        self.add_state = adder.add_state
        self.set_instance = adder.set_instance


class BoundPruner:
    """Filter layer for rejecting states which already exceed a precalculated c_max bound."""

    def __init__(self, adder, params):
        self.c_max_pruner = __import__(params["c_max_pruner"]).Solver()
        self.c_max_pruner.set_log_strategy(False)  # no need to track the heuristics
        self.adder_add_state = adder.add_state
        self.adder_set_instance = adder.set_instance

    def set_instance(self, instance):
        self.adder_set_instance(instance)
        self.c_max_pruner.set_instance(instance)
        self.c_max_bound = self.c_max_pruner.run()

    def add_state(self, w1, w2, i1, i2):
        if w1 <= self.c_max_bound and w2 <= self.c_max_bound:
            self.adder_add_state(w1, w2, i1, i2)
