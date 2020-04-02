import json
from random import sample, randint, randrange, seed
from hashlib import sha256
from pathlib import Path

from goodies import data_to_json


class MakeInstance:
    def __init__(self, height, arity=2):
        self.leaves = list(range(arity ** (height - 1), arity ** height))
        self.arity = arity
        self.max_sample_weight = arity ** height
        self.height = height

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
        self.paths = [
            self.ancestors(leaf)
            for leaf in sample(self.leaves, round(len(self.leaves) * leaf_rate))
        ]

    def remove_random_nodes(self, kill_rate):
        """
        Suppress a certain percentage (expressed as a floating-point value in [0, 1]) of the distinct
        nodes occurring in self.paths, excluding the root and the leaves.
        """
        if 0 < kill_rate <= 1:
            candidates = set.union(*map(set, self.paths))
            to_kill = set(sample(candidates, round(len(candidates) * kill_rate)))
            for path in self.paths:
                path[:] = [node for node in path if node not in to_kill]
            self.paths.sort()

    def renumber_symbols(self):
        """Update self.paths with all their nodes renumbered consecutively."""
        remaining_nodes = set.union(*map(set, self.paths))
        self.node_count = len(remaining_nodes)
        renumber_node = dict((old, new) for (new, old) in enumerate(remaining_nodes)).get
        self.paths = [list(map(renumber_node, path)) for path in self.paths]

    def create_random_weights(self, max_weight):
        """Return a list of n random weights, where n is the number of distinct nodes in self.paths."""
        self.weights = [1 + randrange(max_weight) for _ in range(self.node_count)]

    def __call__(self, leaf_rate, kill_rate, symbol_weight_bound):
        self.create_path_sample(leaf_rate)
        self.remove_random_nodes(kill_rate)
        self.renumber_symbols()
        self.create_random_weights(symbol_weight_bound)
        return {
            "name": "h={height:02}_t={tiles:03}_s={symbols:03}_m={max_weight:02}__{hash_value}.json".format(
                height=self.height,
                tiles=len(self.paths),
                symbols=self.node_count,
                max_weight=max(self.weights),
                hash_value=sha256(f"{self.paths},{self.weights}".encode("utf8")).hexdigest()[:16],
            ),
            "height": self.height,  # seems useless
            "symbol_weight_bound": max(self.weights),  # may be less than symbol_weight_bound
            "symbol_count": self.node_count,
            "symbol_weights": self.weights,
            "tiles": self.paths,
        }


def dump_instances(config_path):
    cfg = json.loads(Path(config_path).read_text())
    directory = Path(cfg["output_directory"])
    directory.mkdir(parents=True, exist_ok=True)
    seed(cfg["seed"])
    for i in range(1, cfg["instance_count"] + 1):
        height = randint(cfg["min_height"], cfg["max_height"])
        maker = MakeInstance(height, cfg["arity"])
        leaf_rate = randint(cfg["min_tile_percentage"], cfg["max_tile_percentage"]) / 100.0
        kill_rate = randint(cfg["min_kill_percentage"], cfg["max_kill_percentage"]) / 100.0
        symbol_weight_bound = randint(cfg["min_symbol_weight_bound"], cfg["max_symbol_weight_bound"])
        instance = maker(leaf_rate, kill_rate, symbol_weight_bound)
        (directory / instance["name"]).write_text(data_to_json(instance))
        print(".", end="" if i % 80 else "\n", flush=True)


if __name__ == "__main__":
    dump_instances("instances/1_config.json")
