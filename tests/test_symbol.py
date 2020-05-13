import context
from symbol import Symbol

def test_attributes():
    """A symbol has two attributes: its index and its weight."""
    s1 = Symbol(4, 2)
    assert s1.index == 4
    assert s1.weight == 2
    s2 = Symbol(4)
    assert s2.index == 4
    assert s2.weight == 1 # default value
    s3 = Symbol(weight=2, index=4)
    assert s3.index == 4
    assert s3.weight == 2


def test_equality():
    """Two symbols with the same attributes are identical."""
    s1 = Symbol(1, 4)
    s2 = Symbol(2, 2)
    s3 = Symbol(2, 2)
    assert s1 != s2
    assert s2 == s3

def test_inequality():
    """The symbols are ordered by index."""
    s1 = Symbol(1, 100)
    s2 = Symbol(100, 1)
    assert s1 < s2
