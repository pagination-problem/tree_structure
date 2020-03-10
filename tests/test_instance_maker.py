import random

import pytest

import context
from instance_maker import MakeInstance


def test_call_sequence():

    maker = MakeInstance(height=4)
    assert maker.leaves == [8, 9, 10, 11, 12, 13, 14, 15]

    random.seed(42)

    with pytest.raises(AssertionError):
        maker.create_sample_paths(sample_size=100)

    maker.create_sample_paths(sample_size=5)
    assert maker.paths == [
        [0, 1, 2, 4, 9],
        [0, 1, 2, 4, 8],
        [0, 1, 3, 6, 13],
        [0, 1, 2, 5, 10],
        [0, 1, 3, 7, 15],
    ]

    maker.renumber_symbols()
    assert maker.paths == [
        [0, 1, 2, 4, 9],
        [0, 1, 2, 4, 8],
        [0, 1, 3, 6, 11],
        [0, 1, 2, 5, 10],
        [0, 1, 3, 7, 12],
    ]
    assert maker.node_count == 13
    assert maker.node_count == maker.paths[-1][-1] + 1

    maker.create_random_weights(max_weight=4)
    assert maker.weights == [2, 2, 1, 1, 4, 1, 1, 1, 2, 2, 1, 2, 4]
