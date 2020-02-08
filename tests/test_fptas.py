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


def test_set_instance():
    instance = Instance(Path("tests/input/H3-nbT5-001.json"))
    fptas.set_instance(instance)
    actual_matrix = fptas.matrix
    # fmt: off
    expected_matrix = [
        ['x', 'x', 'x', 'x', 'x', 'x', 'x', 'x', 'x'],
        ['x', 'x', 'x', 'x', 'x', 'x', 'x', 'x', 'x'], 
        [  8, 'x',   0, 'x', 'x', 'x', 'x', 'x', 'x'], 
        [  8, 'x',   3,   0, 'x', 'x', 'x', 'x', 'x'], 
        [ 11, 'x',   6,   4,   0, 'x', 'x', 'x', 'x'], 
        ['x', 'x', 'x', 'x', 'x', 'x', 'x', 'x', 'x'], 
        ['x', 'x', 'x', 'x', 'x', 'x', 'x', 'x', 'x'], 
        [ 12, 'x',  12,  12,  12, 'x', 'x',   0, 'x'], 
        [ 14, 'x',  14,  14,  14, 'x', 'x',   5,   0],
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
