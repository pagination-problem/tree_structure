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
        [NA, NA, NA, NA, NA, NA, NA, NA, NA],
        [NA, NA, NA, NA, NA, NA, NA, NA, NA], 
        [ 8, NA,  0, NA, NA, NA, NA, NA, NA], 
        [ 8, NA,  3,  0, NA, NA, NA, NA, NA], 
        [11, NA,  6,  4,  0, NA, NA, NA, NA], 
        [NA, NA, NA, NA, NA, NA, NA, NA, NA], 
        [NA, NA, NA, NA, NA, NA, NA, NA, NA], 
        [12, NA, 12, 12, 12, NA, NA,  0, NA], 
        [14, NA, 14, 14, 14, NA, NA,  5,  0],
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
