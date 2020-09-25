from pathlib import Path
from pprint import pprint
from collections import namedtuple

import context
from solver_fptas import Solver, StateStore
from instance import Instance

InstanceStub = namedtuple('InstanceStub', ["symbol_weight_sum", "tile_count"])

def test_state_store():
    store = StateStore({"hash_epsilon": 0.1})
    instance = InstanceStub(symbol_weight_sum=200, tile_count=5)
    store.set_instance(instance)
    store.cleanup_states()
    states = [(0, 1, 42, 42, {}), (1, 5, 42, 42, {}), (2, 0, 42, 42, {}), (3, 1, 42, 42, {}), (3, 3, 42, 42, {}), (4, 1, 42, 42, {}), (5, 0, 42, 42, {}), (5, 1, 42, 42, {}), (5, 3, 42, 42, {}), (5, 4, 42, 42, {})]
    for state in states:
        store.add_state(*state)
    filtered_states = list(store.get_states())
    print(filtered_states)
    assert filtered_states == [(0, 1, 42, 42, {}), (1, 5, 42, 42, {}), (2, 0, 42, 42, {}), (3, 3, 42, 42, {}), (4, 1, 42, 42, {}), (5, 3, 42, 42, {}), (5, 4, 42, 42, {})]


instance = Instance(Path("tests/input/h=03_t=005_s=011_m=06.json"))
#
#     Symbol indexes         Symbol weights
#
#            0                      0
#          /   \                  /   \
#         1     2                5     3
#        / \     \              / \     \
#       3   4     5            1   2     6
#      /   / \   / \          /   / \   / \
#     6   7   8 9  10        2   1   4 3   5
#
#            Tile weights    8   8  11 12  14


def test_set_instance():
    fptas = Solver({})
    fptas.set_log_strategy(True)
    fptas.set_instance(instance)
    # fmt: off                +----- The last column is duplicated to differentiate "last tile" and "no top tile"
    expected_costs = [ #      |
        [ 8,  8,  8,  8,  8,  8], # tile (0, 1, 3,  6) / weights (0 + 5 + 1 + 2) =  8
        [ 3,  8,  8,  8,  8,  8], # tile (0, 1, 4,  7) / weights (0 + 5 + 2 + 1) =  8
        [ 6,  4, 11, 11, 11, 11], # tile (0, 1, 4,  8) / weights (0 + 5 + 2 + 4) = 11
        [12, 12, 12, 12, 12, 12], # tile (0, 2, 5,  9) / weights (0 + 3 + 6 + 3) = 12
        [14, 14, 14,  5, 14, 14], # tile (0, 2, 5, 10) / weights (0 + 3 + 6 + 5) = 14
    ] #       |           |
    #         |           +------ adding tile (0, 1, 3,  6) on an empty bin costs 0 + 5 + 1 + 2 = 8, etc.
    #         |
    #         +------ If tile (0, 1, 4,  7) is already present in a given bin...
    #                 ... adding tile (0, 1, 4,  8) costs weight(8) = 4
    #                                 (0, 2, 5,  9) costs weight(2, 5, 9) = 3 + 6 + 3 = 12
    #                                 (0, 2, 5, 10) costs weight(2, 5, 10) = 3 + 6 + 5 = 14
    # fmt: on
    pprint(fptas.costs)
    assert expected_costs == fptas.costs


def test_run_fptas_hash_store():
    fptas = Solver({"hash_epsilon": 1})
    fptas.set_log_strategy(True)
    fptas.set_instance(instance)
    (computed_c_max, best_state) = fptas.run()
    assert computed_c_max == 17
    pprint(fptas.log_result)
    expected_log_result = [
        [(8, 0, 0, 5)],
        [(11, 0, 1, 5), (8, 8, 0, 1)],
        [(15, 0, 2, 5), (11, 11, 1, 2), (14, 8, 2, 1), (8, 12, 0, 2)],
        [
            (27, 0, 3, 5),
            (15, 12, 2, 3),
            (23, 11, 3, 2),
            (11, 23, 1, 3),
            (26, 8, 3, 1),
            (14, 20, 2, 3),
            (20, 12, 3, 2),
            (8, 24, 0, 3),
        ],
        [
            (32, 0, 4, 5),
            (27, 14, 3, 4),
            (29, 12, 4, 3),
            (15, 17, 2, 4),
            (28, 11, 4, 2),
            (23, 25, 3, 4),
            (25, 23, 4, 3),
            (11, 28, 1, 4),
            (31, 8, 4, 1),
            (26, 22, 3, 4),
            (28, 20, 4, 3),
            (14, 25, 2, 4),
            (25, 12, 4, 2),
            (20, 26, 3, 4),
            (22, 24, 4, 3),
            (8, 29, 0, 4),
        ],
    ]
    for (i, (expected, actual)) in enumerate(zip(expected_log_result, fptas.log_result)):
        print(f"Step {i}: {actual}")
        assert expected == actual
    (bin1, bin2) = fptas.retrieve_solution()
    assert fptas.c_max == 17
    assert (bin1, bin2) == ([0, 1, 2], [3, 4])
    print(fptas.best_states)
    assert fptas.best_states == [
        (15, 17, 2, 4),
        (15, 12, 2, 3),
        (15, 0, 2, 5),
        (11, 0, 1, 5),
        (8, 0, 0, 5),
    ]
