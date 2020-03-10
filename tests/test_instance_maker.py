import random

import pytest

import context
from instance_maker import MakeInstance, TrivialPathError

maker = MakeInstance(height=4)
assert maker.leaves == [8, 9, 10, 11, 12, 13, 14, 15]
with pytest.raises(AssertionError):
    maker.create_path_sample(sample_size=100)


def test_normal_sequence():
    random.seed(42)
    maker.create_path_sample(sample_size=5)
    assert maker.paths == [
        [0, 1, 2, 4, 9],
        [0, 1, 2, 4, 8],
        [0, 1, 3, 6, 13],
        [0, 1, 2, 5, 10],
        [0, 1, 3, 7, 15],
    ]

    maker.remove_random_nodes(kill_rate=0.3)
    assert maker.paths == [
        [0, 4, 9],
        [0, 4],
        [0, 6, 13],
        [0, 5, 10],
        [0, 7, 15],
    ]

    maker.renumber_symbols()
    assert maker.paths == [
        [0, 1, 5],
        [0, 1],
        [0, 3, 7],
        [0, 2, 6],
        [0, 4, 8],
    ]
    assert maker.node_count == 9
    assert maker.node_count == maker.paths[-1][-1] + 1

    maker.create_random_weights(max_weight=4)
    assert maker.weights == [1, 4, 1, 1, 1, 2, 2, 1, 2]


def test_removing_too_much_nodes():
    random.seed(42)
    maker.create_path_sample(sample_size=5)
    with pytest.raises(TrivialPathError):
        maker.remove_random_nodes(kill_rate=0.6)
