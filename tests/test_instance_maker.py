import random

import pytest

import context
from instance_maker import MakeInstance

maker = MakeInstance(height=4)
assert maker.leaves == [8, 9, 10, 11, 12, 13, 14, 15]


def test_call_sequence():
    random.seed(42)
    maker.create_path_sample(leaf_rate=0.8)
    assert maker.paths == [
        [0, 1, 2, 4, 9],
        [0, 1, 2, 4, 8],
        [0, 1, 3, 6, 13],
        [0, 1, 2, 5, 10],
        [0, 1, 3, 7, 15],
        [0, 1, 3, 7, 14],
    ]

    maker.remove_random_nodes(kill_rate=0.4)
    assert maker.paths == [
        [0, 3, 7, 14],
        [0, 3, 7, 15],
        [0, 3, 13],
        [0, 4, 8],
        [0, 4, 9],
        [0, 5, 10],
    ]

    maker.renumber_symbols()
    assert maker.paths == [
        [0, 1, 4, 9],
        [0, 1, 4, 10],
        [0, 1, 8],
        [0, 2, 5],
        [0, 2, 6],
        [0, 3, 7],
    ]
    assert maker.node_count == 11

    maker.create_random_weights(max_weight=4)
    assert maker.weights == [1, 4, 1, 1, 1, 2, 2, 1, 2, 4, 2]
