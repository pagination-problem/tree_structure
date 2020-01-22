import context

from symbol import Symbol
from tile import Tile


def test_init():
    s1 = Symbol(1, 4)
    s2 = Symbol(2, 2)
    s3 = Symbol(3, 7)
    t = Tile({s1, s2, s3})
    assert t.symbols == {s1, s2, s3}
    assert hasattr(t, "hash")
    assert t.leaf_symbol == s3
    assert t.leaf_index == 3
    assert t.length == 13
    assert t.string == "{1, 2, 3}"
