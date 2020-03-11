from pathlib import Path
from pprint import pprint

import context
from fptas import Fptas, NA
from instance import Instance

fptas = Fptas()


def test_select_representatives_on_grid():
    fptas.delta = 2
    states = [(0.5, 0.5), (1.5, 1.5), (2.5, 2.5), (2.75, 2.75)]
    actual = fptas.select_representatives_on_grid(states)
    print(actual)
    assert actual == [(0.5, 0.5), (2.5, 2.5)]


def test_set_instance():
    instance = Instance(Path("tests/input/H3-nbT5-001.json"))
    fptas.set_instance(instance)
    actual_matrix = fptas.matrix
    # fmt: off
    expected_matrix = [
        [NA, NA, NA, NA, NA, NA, NA, NA, NA], # (offset?)
        [NA, NA, NA, NA, NA, NA, NA, NA, NA], # leaf 1 (node 8)
        [ 8, NA,  0, NA, NA, NA, NA, NA, NA], # tile (1, 2, 4,  9) / weights (0, 5, 1, 2) / weight sum = 8
        [ 8, NA,  3,  0, NA, NA, NA, NA, NA], # tile (1, 2, 5, 10) / weights (0, 5, 2, 1) / weight sum = 8
        [11, NA,  6,  4,  0, NA, NA, NA, NA], # tile (1, 2, 5, 11) / weights (0, 5, 2, 4) / weight sum = 11
        [NA, NA, NA, NA, NA, NA, NA, NA, NA], # leaf 5 (node 12)
        [NA, NA, NA, NA, NA, NA, NA, NA, NA], # leaf 6 (node 13)
        [12, NA, 12, 12, 12, NA, NA,  0, NA], # tile (1, 3, 7, 14) / weights (0, 3, 6, 3) / weight sum = 12
        [14, NA, 14, 14, 14, NA, NA,  5,  0], # tile (1, 3, 7, 15) / weights (0, 3, 6, 5) / weight sum = 14
    ]
    # fmt: on
    pprint(actual_matrix)
    assert expected_matrix == actual_matrix


def test_run():
    instance = Instance(Path("tests/input/H3-nbT5-001.json"))
    fptas.set_instance(instance)
    fptas.set_log_strategy(False)
    for engine in ("basic", "improved"):
        fptas.set_engine_strategy(engine)
        fptas.run(epsilon=0.1)
        assert fptas.state_count == 42
        assert fptas.c_max == 17
