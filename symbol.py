from typing import Iterable, NamedTuple


class Symbol(NamedTuple):
    index: int
    size: int = 1  # default size = 1


Symbols = Iterable[Symbol]
