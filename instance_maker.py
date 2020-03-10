import random


def ancestors(node):
    """Return all the ancestors of a node in a complete binary tree, including itself."""
    result = [node]
    while node:
        node //= 2
        result.append(node)
    return result[::-1]


class MakeInstance:
    def __init__(self, height):
        self.leaves = list(range(2 ** (height - 1), 2 ** height))

    def create_sample_paths(self, sample_size):
        """Create all paths from the root to a random sample of leaves in a binary tree."""
        assert sample_size <= len(self.leaves), "The sample size should be at most 2 ** height."
        self.paths = [ancestors(leaf) for leaf in random.sample(self.leaves, sample_size)]

    def renumber_symbols(self):
        """Update self.paths with all their nodes renumbered consecutively."""
        remaining_nodes = set.union(*map(set, self.paths))
        renumber_node = dict((old, new) for (new, old) in enumerate(remaining_nodes)).get
        self.paths = [list(map(renumber_node, path)) for path in self.paths]
        self.node_count = len(remaining_nodes)

    def create_random_weights(self, max_weight):
        """Return a list of n random weights, where n is the number of distinct nodes in self.paths."""
        self.weights = [1 + random.randrange(max_weight) for _ in range(self.node_count)]

    def __call__(self):
        raise NotImplementedError
