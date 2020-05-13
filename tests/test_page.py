import os
import context
from symbol import Symbol
from tile import Tile
from page import Page


s1 = Symbol(1, 4)
s2 = Symbol(2, 2)
s3 = Symbol(3, 7)
s4 = Symbol(4, 1)
s5 = Symbol(5, 4)

t1 = Tile({s1, s2})
t2 = Tile({s2, s4})
t3 = Tile({s3, s2, s1})
t4 = Tile({s1, s5})  # a tile absent from p
t5 = Tile({s1, s2})  # a tile with the same elements as t1...

p = Page()

p.add_tile(t1)
p.add_tile(t2)
p.add_tile(t3)


def test_tile_belonging():
    assert t1 in p
    assert t2 in p
    assert t3 in p
    assert t4 not in p
    assert t5 in p  # ... would nevertheless be contained in p too


def test_symbol_belonging():
    assert s1 in p
    assert s2 in p
    assert s3 in p
    assert s4 in p
    assert s5 not in p


def test_string_conversion():
    assert str(p) == r"{{2, 4}, {1, 2}, {1, 2, 3}}"


def test_iter():
    assert set(tile for tile in p) == set([t1, t2, t3])


def test_counts():
    assert p.tile_count() == 3
    assert p.symbol_count() == 4
