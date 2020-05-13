import random

import pytest

import context
from generate_instances import (
    InstanceMaker,
    TileTooSmall,
    TooFewCommonSymbols,
    TooManyCommonSymbols,
)


def test_call_sequence():
    maker = InstanceMaker(height=4)
    assert maker.leaves == [8, 9, 10, 11, 12, 13, 14, 15]

    random.seed(42)
    maker.create_path_sample(leaf_rate=0.8)
    print(maker.paths)
    assert maker.paths == [
        [0, 1, 2, 4, 8],
        [0, 1, 2, 4, 9],
        [0, 1, 2, 5, 10],
        [0, 1, 3, 6, 13],
        [0, 1, 3, 7, 14],
        [0, 1, 3, 7, 15],
    ]

    maker.remove_random_nodes(kill_rate=0.1)
    print(maker.paths)
    assert maker.paths == [
        [0, 1, 4, 8],
        [0, 1, 4, 9],
        [0, 1, 5, 10],
        [0, 1, 3, 6, 13],
        [0, 1, 3, 7, 14],
        [0, 1, 3, 7, 15],
    ]

    maker.renumber_symbols()
    print(maker.paths)
    assert maker.paths == [
        [0, 1, 3, 7],
        [0, 1, 3, 8],
        [0, 1, 4, 9],
        [0, 1, 2, 5, 10],
        [0, 1, 2, 6, 11],
        [0, 1, 2, 6, 12],
    ]
    assert maker.node_count == 13

    maker.create_random_weights(max_weight=4)
    print(maker.weights)
    assert maker.weights == [1, 1, 4, 1, 1, 1, 2, 2, 1, 2, 4, 2, 4]


def test_beyond_binary_trees():
    maker = InstanceMaker(height=3, arity=3)
    assert maker.leaves == [9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26]


def test_tile_too_small():
    # Success for tile_min_size == 2
    maker = InstanceMaker(height=4, tile_min_size=2)
    random.seed(42)
    maker.create_path_sample(leaf_rate=0.8)
    maker.remove_random_nodes(kill_rate=0.3)
    print(maker.paths)
    assert maker.paths == [
        [0, 4, 8],
        [0, 4, 9],
        [0, 5],
        [0, 3, 6],
        [0, 3, 7, 14],
        [0, 3, 7, 15],
    ]

    # Failure for tile_min_size == 3
    maker = InstanceMaker(height=4, tile_min_size=3)
    random.seed(42)
    maker.create_path_sample(leaf_rate=0.8)
    with pytest.raises(TileTooSmall):
        maker.remove_random_nodes(kill_rate=0.3)


def test_too_few_common_symbols():
    maker = InstanceMaker(height=4, tile_min_size=2, common_symbol_min_count=2)
    random.seed(42)
    maker.create_path_sample(leaf_rate=0.8)
    maker.remove_random_nodes(kill_rate=0.3)  # see self.paths' value in test_tile_too_small()
    with pytest.raises(TooFewCommonSymbols):
        maker.renumber_symbols()


def test_too_many_common_symbols():
    maker = InstanceMaker(height=4, tile_min_size=2, common_symbol_max_count=0)
    random.seed(42)
    maker.create_path_sample(leaf_rate=0.8)
    maker.remove_random_nodes(kill_rate=0.3)  # see self.paths' value in test_tile_too_small()
    with pytest.raises(TooManyCommonSymbols):
        maker.renumber_symbols()
