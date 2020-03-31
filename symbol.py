from typing import Iterable, NamedTuple


class Symbol(NamedTuple):
    index: int
    weight: int = 1  # default weight = 1


Symbols = Iterable[Symbol]
