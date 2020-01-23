import context

from instance import Instance
from symbol import Symbol
from tile import Tile
from pathlib import Path

def test_deserialize():
    expected = {
        "height": 3,
        "symbol_size_bound": 9,
        "opt_tiles_m1": [],
        "opt_tiles_m2": [],
        "opt_value": None,
        "symbols_on_m1": [],
        "symbols_on_m2": [],
        "name": "tests/input/H3-nbT5-001.json",
        "symbols": frozenset(
            {
                Symbol(1, 0),
                Symbol(2, 5),
                Symbol(3, 3),
                Symbol(4, 1),
                Symbol(5, 2),
                Symbol(7, 6),
                Symbol(9, 2),
                Symbol(10, 1),
                Symbol(11, 4),
                Symbol(14, 3),
                Symbol(15, 5),
            }
        ),
        "tiles": frozenset(
            {
                Tile([Symbol(1, 0), Symbol(2, 5), Symbol(5, 2), Symbol(10, 1)]),
                Tile([Symbol(1, 0), Symbol(2, 5), Symbol(5, 2), Symbol(11, 4)]),
                Tile([Symbol(1, 0), Symbol(3, 3), Symbol(7, 6), Symbol(14, 3)]),
                Tile([Symbol(1, 0), Symbol(2, 5), Symbol(4, 1), Symbol( 9, 2)]),
                Tile([Symbol(1, 0), Symbol(3, 3), Symbol(7, 6), Symbol(15, 5)]),
            }
        ),
    }
    actual = Instance.deserialize(Path("tests/input/H3-nbT5-001.json"))
    print(actual)
    assert expected == actual
