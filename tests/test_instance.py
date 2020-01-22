import context

from instance import deserialize
from symbol import Symbol
from tile import Tile


def test_deserialize():
    text = """
        {
            "height": 3,
            "max_symbol_size": 9,
            "opt_value": null,
            "opt_tiles_m1": [],
            "symbols_on_m1": [],
            "opt_tiles_m2": [],
            "symbols_on_m2": [],
            "tiles": [
                [1, 2, 5, 10],
                [1, 2, 5, 11],
                [1, 3, 7, 14],
                [1, 2, 4, 9],
                [1, 3, 7, 15]
            ],
            "symbol_indexes": [1, 2, 3, 4, 5, 7, 9, 10, 11, 14, 15],
            "symbol_sizes": [0, 5, 3, 1, 2, 6, 2, 1, 4, 3, 5]
        }
    """
    expected = {
        "height": 3,
        "max_symbol_size": 9,
        "opt_tiles_m1": [],
        "opt_tiles_m2": [],
        "opt_value": None,
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
        "symbols_on_m1": [],
        "symbols_on_m2": [],
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
    actual = deserialize(text)
    print(actual)
    assert expected == actual
