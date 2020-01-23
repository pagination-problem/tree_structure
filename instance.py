import json
from pathlib import Path
from symbol import Symbol
from typing import Dict

from tile import Tile


class Instance:

    @staticmethod
    def deserialize(json_path: Path) -> Dict:
        """
        A thin wrapper around the deserialization of an instance's JSON dump.
        
        The symbols and the tiles are converted into the appropriate objects.
        The other fields, if any, are returned untouched.
        """
        data = json.loads(json_path.read_text())
        d = {s[0]: Symbol(*s) for s in zip(data.pop("symbol_indexes"), data.pop("symbol_sizes"))}
        data["name"] = str(json_path)
        data["symbols"] = frozenset(d.values())
        data["tiles"] = frozenset(Tile([d[i] for i in t]) for t in data.pop("tiles"))
        return data

    def __init__(self, json_path: Path):
        data = Instance.deserialize(json_path)
        self.height = data["height"]
        self.symbol_size_bound = data["symbol_size_bound"]
        self.opt_tiles_m1 = data["opt_tiles_m1"]
        self.opt_tiles_m2 = data["opt_tiles_m2"]
        self.opt_value = data["opt_value"]
        self.symbols_on_m1 = data["symbols_on_m1"]
        self.symbols_on_m2 = data["symbols_on_m2"]
        self.name = data["name"]
        self.symbols = data["symbols"]
        self.tiles = data["tiles"]

        self.symbol_size_sum = sum(symbol.size for symbol in self.symbols)
        self.tile_count = len(self.tiles)
