import json
import sys
from functools import reduce
from hashlib import sha256
from pathlib import Path
from random import randint, randrange, sample, seed

from statistics import mean, pstdev
from instance import Instance
from tile import Tile
from symbol import Symbol

from numpy import base_repr

from goodies import data_to_json


class InstanceMaker:
    def __init__(
        self,
        height,
        arity=2,
        tile_min_size=2,
        common_symbol_min_count=0,
        common_symbol_max_count=sys.maxsize,
    ):
        self.leaves = list(range(arity ** (height - 1), arity ** height))
        self.height = height
        self.arity = arity
        self.tile_min_size = tile_min_size
        self.common_symbol_min_count = common_symbol_min_count
        self.common_symbol_max_count = common_symbol_max_count

    def ancestors(self, node):
        """Return all the ancestors of a node in a complete n-ary tree, including itself."""
        result = [node]
        while node:
            node //= self.arity
            result.append(node)
        return result[::-1]

    def create_path_sample(self, leaf_rate):
        """Create all paths from the root to a random sample of leaves in a complete n-ary tree."""
        assert 0 <= leaf_rate <= 1
        self.paths = sorted(
            self.ancestors(leaf)
            for leaf in sample(self.leaves, round(len(self.leaves) * leaf_rate))
        )

    def remove_random_nodes(self, kill_rate):
        """
        Suppress a certain percentage (expressed as a floating-point value in [0, 1]) of the distinct
        nodes occurring in self.paths.
        """
        if 0 < kill_rate <= 1:
            candidates = set.union(*map(set, self.paths))
            to_kill = set(sample(candidates, round(len(candidates) * kill_rate)))
            for path in self.paths:
                path[:] = [node for node in path if node not in to_kill]
                if len(path) < self.tile_min_size:
                    raise TileTooSmall
            if len(set(map(tuple, self.paths))) != len(self.paths):
                raise DuplicateTiles

    def renumber_symbols(self):
        """Update self.paths with all their nodes renumbered consecutively."""
        remaining_nodes = set.union(*map(set, self.paths))
        self.node_count = len(remaining_nodes)
        renumber_node = dict((old, new) for (new, old) in enumerate(remaining_nodes)).get
        self.paths = [list(map(renumber_node, path)) for path in self.paths]
        self.common_symbols = reduce(lambda s1, s2: set(s1).intersection(s2), self.paths)
        if len(self.common_symbols) < self.common_symbol_min_count:
            raise TooFewCommonSymbols
        if len(self.common_symbols) > self.common_symbol_max_count:
            raise TooManyCommonSymbols

    def create_random_weights(self, max_weight):
        """Return a list of n random weights, where n is the number of distinct nodes in self.paths."""
        self.weights = [1 + randrange(max_weight) for _ in range(self.node_count)]

    def __call__(self, leaf_rate, kill_rate, symbol_weight_bound):
        self.create_path_sample(leaf_rate)
        self.remove_random_nodes(kill_rate)
        self.renumber_symbols()
        self.create_random_weights(symbol_weight_bound)
        identifier = f"{self.paths},{self.weights}".encode("utf8")

        returned_dict = {
            "name": "h={height:02}_t={tiles:03}_s={symbols:03}_m={max_weight:02}__{hash_value}.json".format(
                height=self.height,
                tiles=len(self.paths),
                symbols=self.node_count,
                max_weight=max(self.weights),
                hash_value=base_repr(int(sha256(identifier).hexdigest(), 16), base=36)[:4],
            ),
            "height": self.height,  # seems useless
            "symbol_weight_bound": max(self.weights),  # may be less than symbol_weight_bound
            "symbol_count": self.node_count,
            "common_symbols": sorted(self.common_symbols),
            "symbol_weights": self.weights,
            "cost_mean": "N/A",
            "cost_standard_deviation": "N/A",
            "tiles": sorted(self.paths),
            "costs": "N/A"
        }

        temporary_instance = Instance(returned_dict)

        costs = [[tile.weight] * (temporary_instance.tile_count + 1) for tile in temporary_instance.tiles]
        for (new, new_tile) in enumerate(temporary_instance.tiles):
            for (last, last_tile) in enumerate(temporary_instance.tiles[:new]):
                costs[new][last] = sum(symbol.weight for symbol in new_tile - last_tile)
        
        lower_triangle_costs = [row[: i + 1] for (i, row) in enumerate(costs)]
        flattened_costs = reduce(lambda x, y: x + y, lower_triangle_costs)
        cost_mean = mean(flattened_costs)
        cost_standard_deviation = pstdev(flattened_costs)

        returned_dict["cost_mean"] = cost_mean
        returned_dict["cost_standard_deviation"] = cost_standard_deviation
        returned_dict["costs"] = costs

        return returned_dict


class TileTooSmall(Exception):
    ...


class DuplicateTiles(Exception):
    ...


class TooManyCommonSymbols(Exception):
    ...


class TooFewCommonSymbols(Exception):
    ...


def dump_instances(config_path):
    cfg = json.loads(Path(config_path).read_text())
    directory = Path(cfg["output_directory"])
    directory.mkdir(parents=True, exist_ok=True)
    seed(cfg["seed"])
    i = 1
    column = 1
    while i <= cfg["instance_count"]:
        height = randint(cfg["min_height"], cfg["max_height"])
        maker = InstanceMaker(
            height,
            cfg["arity"],
            cfg["tile_min_size"],
            cfg["common_symbol_min_count"],
            cfg["common_symbol_max_count"],
        )
        leaf_rate = randint(cfg["min_tile_percentage"], cfg["max_tile_percentage"]) / 100.0
        kill_rate = randint(cfg["min_kill_percentage"], cfg["max_kill_percentage"]) / 100.0
        symbol_weight_bound = randint(
            cfg["min_symbol_weight_bound"], cfg["max_symbol_weight_bound"]
        )
        try:
            instance = maker(leaf_rate, kill_rate, symbol_weight_bound)
        except DuplicateTiles:
            outcome = "D"
        except TileTooSmall:
            outcome = "S"
        except TooFewCommonSymbols:
            outcome = "F"
        except TooManyCommonSymbols:
            outcome = "M"
        else:
            (directory / instance["name"]).write_text(data_to_json(instance))
            outcome = "."
            i += 1
        print(outcome, end="" if column % 80 else "\n", flush=True)
        column += 1


if __name__ == "__main__":
    filename = "instances/sarah/test_config.json" if len(sys.argv) <= 1 else sys.argv[1]
    # alternatively:  "instances/snapshots.json"
    dump_instances(filename)
