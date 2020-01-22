from typing import Dict
from symbol import Symbol
from tile import Tile
import json


def deserialize(json_instance: str) -> Dict:
    """
    A thin wrapper around the deserialization of an instance's JSON dump.
    
    The symbols and the tiles are converted into the appropriate objects.
    The other fields, if any, are returned untouched.
    """
    data = json.loads(json_instance)
    d = {s[0]: Symbol(*s) for s in zip(data.pop("symbol_indexes"), data.pop("symbol_sizes"))}
    data["symbols"] = frozenset(d.values())
    data["tiles"] = frozenset(Tile([d[i] for i in t]) for t in data.pop("tiles"))
    return data
