import json
from pathlib import Path

import context
from instance import Instance
from tile import Tile
from symbol import Symbol


def test_init_with_json_path():
    instance = Instance(Path("tests/input/H3-nbT5-001.json"))
    assert instance.height == 3
    assert instance.symbol_size_bound == 9
    assert instance.opt_tiles_m1 == []
    assert instance.opt_tiles_m2 == []
    assert instance.opt_value == None
    assert instance.symbols_on_m1 == []
    assert instance.symbols_on_m2 == []
    assert instance.name == "tests/input/H3-nbT5-001.json"
    assert instance.symbols == frozenset(
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
    )
    assert instance.tiles == frozenset(
        {
            Tile([Symbol(1, 0), Symbol(2, 5), Symbol(5, 2), Symbol(10, 1)]),
            Tile([Symbol(1, 0), Symbol(2, 5), Symbol(5, 2), Symbol(11, 4)]),
            Tile([Symbol(1, 0), Symbol(3, 3), Symbol(7, 6), Symbol(14, 3)]),
            Tile([Symbol(1, 0), Symbol(2, 5), Symbol(4, 1), Symbol(9, 2)]),
            Tile([Symbol(1, 0), Symbol(3, 3), Symbol(7, 6), Symbol(15, 5)]),
        }
    )


def test_round_trip():
    path = Path("tests/input/H3-nbT5-001.json")
    text = path.read_text()
    data = json.loads(text)
    instance_1 = Instance(data)
    instance_2 = Instance(path)
    json_1 = instance_1.get_json()
    print(json_1)
    json_2 = instance_2.get_json()
    print(json_2)
    assert json_1 == json_2
    assert json_1 == text

