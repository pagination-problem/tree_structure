import random

import pytest

import context
from generate_instances import (
    InstanceMaker,
    TileTooSmall,
    TooFewCommonSymbols,
    TooManyCommonSymbols,
)

from instance import Instance
import numpy as np

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

def test_compute_occurrences_of_p_i():
    the_dict = {
        "name": "h=03_t=005_s=011_m=06.json",
        "height": 3,
        "symbol_weight_bound": 6,
        "symbol_count": 11,
        "symbol_weights": [0, 5, 3, 1, 2, 6, 2, 1, 4, 3, 5],
        "cost_mean": 9.933333333333334,
        "cost_standard_deviation": 3.785351884420904,
        "tiles": [
            [0, 1, 3, 6],
            [0, 1, 4, 7],
            [0, 1, 4, 8],
            [0, 2, 5, 9],
            [0, 2, 5, 10]
        ],
        "costs": [
            [8, 8, 8, 8, 8, 8],
            [3, 8, 8, 8, 8, 8],
            [6, 4, 11, 11, 11, 11],
            [12, 12, 12, 12, 12, 12],
            [14, 14, 14, 5, 14, 14]
        ]
    }
    maker = InstanceMaker(
        height=the_dict["height"],
        tile_min_size=2,
        common_symbol_max_count=1,
        min_symbol_weight_bound=0,
        max_symbol_weight_bound=np.inf)
    the_instance = Instance(the_dict)
    computed_occurrences = maker.compute_occurrences_of_p_i(the_instance)

    assert computed_occurrences == [5, 3, 8, 1, 4, 8, 1, 2, 3, 4, 5]

def test_compute_coefficient_for_quadratic_var():
    the_dict = {
    "name": "h=03_t=005_s=011_m=06.json",
    "height": 3,
    "symbol_weight_bound": 6,
    "symbol_count": 11,
    "symbol_weights": [0, 5, 3, 1, 2, 6, 2, 1, 4, 3, 5],
    "cost_mean": 9.933333333333334,
    "cost_standard_deviation": 3.785351884420904,
    "tiles": [
        [0, 1, 3, 6],
        [0, 1, 4, 7],
        [0, 1, 4, 8],
        [0, 2, 5, 9],
        [0, 2, 5, 10]
    ],
    "costs": [
        [8, 8, 8, 8, 8, 8],
        [3, 8, 8, 8, 8, 8],
        [6, 4, 11, 11, 11, 11],
        [12, 12, 12, 12, 12, 12],
        [14, 14, 14, 5, 14, 14]
        ]
    }
    maker = InstanceMaker(
        height=the_dict["height"],
        tile_min_size=2,
        common_symbol_max_count=1,
        min_symbol_weight_bound=0,
        max_symbol_weight_bound=np.inf)
    the_instance = Instance(the_dict)
    computed_coefficients = maker.compute_coefficient_for_quadratic_var(the_instance)
    assert computed_coefficients == [
            [5, 6, 4, 2, 4, 4, 2, 2, 2, 2, 2],
            [0, 3, 0, 2, 4, 0, 2, 2, 2, 0, 0],
            [0, 0, 8, 0, 0, 16, 0, 0, 0, 8, 8],
            [0, 0, 0, 1, 0, 0, 2, 0, 0, 0, 0],
            [0, 0, 0, 0, 4, 0, 0, 4, 4, 0, 0],
            [0, 0, 0, 0, 0, 8, 0, 0, 0, 8, 8],
            [0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 2, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0, 3, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0, 0, 4, 0],
            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 5]
        ]

def test_create_weights_according_to_mean_and_deviation():
    the_dict = {
    "name": "h=03_t=005_s=011_m=06.json",
    "height": 3,
    "symbol_weight_bound": 6,
    "symbol_count": 11,
    "symbol_weights": [0, 5, 3, 1, 2, 6, 2, 1, 4, 3, 5],
    "cost_mean": 9.933333333333334,
    "cost_standard_deviation": 3.785351884420904,
    "tiles": [
        [0, 1, 3, 6],
        [0, 1, 4, 7],
        [0, 1, 4, 8],
        [0, 2, 5, 9],
        [0, 2, 5, 10]
    ],
    "costs": [
        [8, 8, 8, 8, 8, 8],
        [3, 8, 8, 8, 8, 8],
        [6, 4, 11, 11, 11, 11],
        [12, 12, 12, 12, 12, 12],
        [14, 14, 14, 5, 14, 14]
        ]
    }
    maker = InstanceMaker(
        height=the_dict["height"],
        tile_min_size=2,
        common_symbol_max_count=1,
        desired_cost_mean=9.933333333333334,
        LB_standard_deviation=3,
        UB_standard_deviation=4,
        min_symbol_weight_bound=0,
        max_symbol_weight_bound=np.inf)
    maker.node_count = the_dict["symbol_count"]

    the_instance = Instance(the_dict)

    p_i_occurrences = [5, 3, 8, 1, 4, 8, 1, 2, 3, 4, 5]
    coeff_for_quadratic = [
            [5, 6, 4, 2, 4, 4, 2, 2, 2, 2, 2],
            [0, 3, 0, 2, 4, 0, 2, 2, 2, 0, 0],
            [0, 0, 8, 0, 0, 16, 0, 0, 0, 8, 8],
            [0, 0, 0, 1, 0, 0, 2, 0, 0, 0, 0],
            [0, 0, 0, 0, 4, 0, 0, 4, 4, 0, 0],
            [0, 0, 0, 0, 0, 8, 0, 0, 0, 8, 8],
            [0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 2, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0, 3, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0, 0, 4, 0],
            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 5]
        ]
    computed_weights = maker.create_weights_according_to_mean_and_deviation(the_instance, p_i_occurrences, coeff_for_quadratic)
    weights =  [computed_weights[i] for i in range(maker.node_count)]

    assert weights == [1.3143362332957655,
                        3.3797392557243984,
                        6.145356839344423,
                        1.1308671600950275,
                        4.2333493169300365,
                        6.145439612266686,
                        1.130865974019982,
                        2.110105630479951,
                        3.1299100560926725,
                        1.6543612251060553e-24,
                        0.23153152447721043]
