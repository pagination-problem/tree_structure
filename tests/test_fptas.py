from pathlib import Path
from pprint import pprint

import context
from fptas import Fptas
from instance import Instance

fptas = Fptas()


def test_select_representatives_on_grid():
    fptas.delta = 2
    states = [(0.5, 0.5), (1.5, 1.5), (2.5, 2.5), (2.75, 2.75)]
    actual = fptas.select_representatives_on_grid(states)
    print(actual)
    assert actual == [(0.5, 0.5), (2.5, 2.5)]


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
    fptas.set_instance(instance)
    # fmt: off
    expected_costs = [
        [ 8,  8,  8,  8,  8], # tile (0, 1, 3,  6) / weights (0 + 5 + 1 + 2) =  8
        [ 3,  8,  8,  8,  8], # tile (0, 1, 4,  7) / weights (0 + 5 + 2 + 1) =  8
        [ 6,  4, 11, 11, 11], # tile (0, 1, 4,  8) / weights (0 + 5 + 2 + 4) = 11
        [12, 12, 12, 12, 12], # tile (0, 2, 5,  9) / weights (0 + 3 + 6 + 3) = 12
        [14, 14, 14,  5, 14], # tile (0, 2, 5, 10) / weights (0 + 3 + 6 + 5) = 14
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


def test_run_basic_fptas():
    fptas.set_instance(instance)
    fptas.set_log_strategy(True)
    fptas.set_engine_strategy("basic")
    fptas.run(epsilon=0.1)
    assert fptas.c_max == 17
    pprint(fptas.log_result)
    # fmt: off
    expected_log_result = [
        [(0, 0, -1, -1)],
        [(8, 0, 0, -1), (0, 8, -1, 0)],
        [(11, 0, 1, -1), (8, 8, 0, 1), (0, 11, -1, 1)],
        [(15, 0, 2, -1), (11, 11, 1, 2), (14, 8, 2, 1), (8, 12, 0, 2), (0, 15, -1, 2)],
        [(27, 0, 3, -1), (15, 12, 2, 3), (23, 11, 3, 2), (11, 23, 1, 3), (26, 8, 3, 1), (14, 20, 2, 3), (20, 12, 3, 2), (8, 24, 0, 3), (12, 15, 3, 2), (0, 27, -1, 3)],
        [(32, 0, 4, -1), (27, 14, 3, 4), (29, 12, 4, 3), (15, 17, 2, 4), (28, 11, 4, 2), (23, 25, 3, 4), (25, 23, 4, 3), (11, 28, 1, 4), (31, 8, 4, 1), (26, 22, 3, 4), (28, 20, 4, 3), (14, 25, 2, 4), (25, 12, 4, 2), (20, 26, 3, 4), (22, 24, 4, 3), (8, 29, 0, 4), (17, 15, 4, 2), (12, 29, 3, 4), (14, 27, 4, 3), (0, 32, -1, 4)],
    ]
    # fmt: on
    for (i, (expected, actual)) in enumerate(zip(expected_log_result, fptas.log_result)):
        print(f"Step {i}: {actual}")
        assert expected == actual
    (bin1, bin2) = fptas.reconstruct_solution()
    assert (bin1, bin2) == ([0, 1, 2], [3, 4])
    assert fptas.best_states == [
        (15, 17, 2, 4),
        (15, 12, 2, 3),
        (15, 0, 2, -1),
        (11, 0, 1, -1),
        (8, 0, 0, -1),
        (0, 0, -1, -1),
    ]


def test_run_improved_fptas():
    fptas.set_instance(instance)
    fptas.set_log_strategy(True)
    fptas.set_engine_strategy("improved")
    fptas.run(epsilon=0.1)
    assert fptas.c_max == 17
    pprint(fptas.log_result)
    # fmt: off
    expected_log_result = [
        [(0, 0, -1, 2)],
        [(8, 0, -1, 1), (0, 8, -1, 2)],
        [(11, 0, -1, 1), (8, 8, 0, 1), (0, 11, -1, 2)],
        [(15, 0, -1, 1), (11, 11, 1, 1), (12, 8, 0, 1), (8, 14, 1, 2), (0, 15, -1, 2)],
        [(27, 0, -1, 1), (15, 12, 2, 2), (23, 11, 1, 1), (11, 23, 2, 2), (24, 8, 0, 1), (12, 20, 2, 2), (20, 14, 2, 1), (8, 26, 1, 2), (12, 15, 2, 1), (0, 27, -1, 2)],
        [(32, 0, -1, 1), (27, 14, 3, 2), (29, 12, 3, 1), (15, 17, 2, 2), (28, 11, 1, 1), (23, 25, 3, 2), (25, 23, 3, 1), (11, 28, 2, 2), (29, 8, 0, 1), (24, 22, 3, 2), (26, 20, 3, 1), (12, 25, 2, 2), (25, 14, 2, 1), (20, 28, 3, 2), (22, 26, 3, 1), (8, 31, 1, 2), (17, 15, 2, 1), (12, 29, 3, 2), (14, 27, 3, 1), (0, 32, -1, 2)],
    ]
    # fmt: on
    for (i, (expected, actual)) in enumerate(zip(expected_log_result, fptas.log_result)):
        print(f"Step {i}: {actual}")
        assert expected == actual
