import json
from pathlib import Path

import context
from instance import Instance
from tile import Tile
from symbol import Symbol


def test_init_with_json_path():
    name = "tests/input/h=03_t=005_s=011_m=06.json"
    instance = Instance(Path(name))
    assert instance.height == 3
    assert instance.symbol_weight_bound == 6
    assert instance.name == Path(name).name
    assert instance.symbols == frozenset(
        {
            Symbol(0, 0),
            Symbol(1, 5),
            Symbol(2, 3),
            Symbol(3, 1),
            Symbol(4, 2),
            Symbol(5, 6),
            Symbol(6, 2),
            Symbol(7, 1),
            Symbol(8, 4),
            Symbol(9, 3),
            Symbol(10, 5),
        }
    )
    assert instance.tiles == [
        Tile([Symbol(0, 0), Symbol(1, 5), Symbol(3, 1), Symbol(6, 2)]),
        Tile([Symbol(0, 0), Symbol(1, 5), Symbol(4, 2), Symbol(7, 1)]),
        Tile([Symbol(0, 0), Symbol(1, 5), Symbol(4, 2), Symbol(8, 4)]),
        Tile([Symbol(0, 0), Symbol(2, 3), Symbol(5, 6), Symbol(9, 3)]),
        Tile([Symbol(0, 0), Symbol(2, 3), Symbol(5, 6), Symbol(10, 5)]),
    ]


def test_round_trip():
    path = Path("tests/input/h=03_t=005_s=011_m=06.json")
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
