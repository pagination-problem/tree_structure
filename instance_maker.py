import random


class TrivialPathError(Exception):
    ...


class MakeInstance:
    def __init__(self, height, arity=2):
        self.leaves = list(range(arity ** (height - 1), arity ** height))
        self.arity = arity
        self.max_sample_size = arity ** height

    def ancestors(self, node):
        """Return all the ancestors of a node in a complete binary tree, including itself."""
        result = [node]
        while node:
            node //= self.arity
            result.append(node)
        return result[::-1]

    def create_path_sample(self, sample_size):
        """Create all paths from the root to a random sample of leaves in a binary tree."""
        assert sample_size <= self.max_sample_size
        self.paths = [self.ancestors(leaf) for leaf in random.sample(self.leaves, sample_size)]

    def remove_random_nodes(self, kill_rate):
        """Suppress a certain percentage of the distinct nodes occurring in self.paths."""
        if not kill_rate:
            return
        remaining_nodes = set.union(*map(set, self.paths))
        to_kill = set(random.sample(remaining_nodes, round(len(remaining_nodes) * kill_rate)))
        for path in self.paths:
            path[:] = [node for node in path if node not in to_kill]
            if len(path) <= 1:
                raise TrivialPathError

    def renumber_symbols(self):
        """Update self.paths with all their nodes renumbered consecutively."""
        remaining_nodes = set.union(*map(set, self.paths))
        self.node_count = len(remaining_nodes)
        renumber_node = dict((old, new) for (new, old) in enumerate(remaining_nodes)).get
        self.paths = [list(map(renumber_node, path)) for path in self.paths]

    def create_random_weights(self, max_weight):
        """Return a list of n random weights, where n is the number of distinct nodes in self.paths."""
        self.weights = [1 + random.randrange(max_weight) for _ in range(self.node_count)]

    def __call__(self):
        raise NotImplementedError
