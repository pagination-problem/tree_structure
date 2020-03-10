import random

import pytest

import context
from instance_maker import MakeInstance


def test_call_sequence():
    maker = MakeInstance(height=4)
    assert maker.leaves == [8, 9, 10, 11, 12, 13, 14, 15]

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


def test_beyond_binary_trees():
    maker = MakeInstance(height=3, arity=3)
    assert maker.leaves == [9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26]

    random.seed(42)
    maker.create_path_sample(leaf_rate=0.8)
    assert maker.paths == [
        [0, 1, 4, 12],
        [0, 1, 3, 9],
        [0, 1, 5, 17],
        [0, 2, 8, 26],
        [0, 2, 7, 23],
        [0, 1, 3, 11],
        [0, 2, 6, 20],
        [0, 1, 3, 10],
        [0, 2, 8, 24],
        [0, 2, 6, 19],
        [0, 1, 5, 15],
        [0, 2, 8, 25],
        [0, 1, 5, 16],
        [0, 1, 4, 14],
    ]

    maker.remove_random_nodes(kill_rate=0.2)
    assert maker.paths == [
        [0, 1, 3, 9],
        [0, 1, 3, 10],
        [0, 1, 3, 11],
        [0, 1, 5, 15],
        [0, 1, 5, 16],
        [0, 1, 5, 17],
        [0, 1, 12],
        [0, 1, 14],
        [0, 6, 19],
        [0, 6, 20],
        [0, 7, 23],
        [0, 8, 24],
        [0, 8, 25],
        [0, 8, 26],
    ]

    maker.renumber_symbols()
    assert maker.paths == [
        [0, 1, 2, 7],
        [0, 1, 2, 8],
        [0, 1, 2, 9],
        [0, 1, 3, 12],
        [0, 1, 3, 13],
        [0, 1, 3, 14],
        [0, 1, 10],
        [0, 1, 11],
        [0, 4, 15],
        [0, 4, 16],
        [0, 5, 17],
        [0, 6, 18],
        [0, 6, 19],
        [0, 6, 20],
    ]
    assert maker.node_count == 21

    maker.create_random_weights(max_weight=4)
    print(maker.weights)
    assert maker.weights == [1, 2, 4, 2, 4, 3, 1, 2, 4, 3, 3, 2, 2, 3, 1, 1, 4, 1, 3, 3, 3]
