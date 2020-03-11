import json
from pathlib import Path
from typing import Dict, Union

from regex import sub

from tile import Tile
from symbol import Symbol
from goodies import data_to_json


def unwrap_int_list(m):
    return f"[{', '.join(m.captures('n'))}]"


class Instance:
    def __init__(self, path_or_data: Union[Path, Dict]):

        # Create a new dictionary from the data
        if isinstance(path_or_data, Path):
            data = json.loads(path_or_data.read_text())
            data["name"] = str(path_or_data)
        else:
            data = path_or_data.copy()  # avoid mutating the input data

        # Convert raw symbols and tiles (simple lists of integers) into appropriate objects
        d = {s[0]: Symbol(*s) for s in zip(data.pop("symbol_indexes"), data.pop("symbol_sizes"))}
        data["symbols"] = frozenset(d.values())
        data["tiles"] = frozenset(Tile([d[i] for i in t]) for t in data.pop("tiles"))

        # Populate the other fields without touching the raw values
        self.height = data["height"]
        self.symbol_size_bound = data["symbol_size_bound"]
        self.opt_tiles_m1 = data["opt_tiles_m1"]
        self.opt_tiles_m2 = data["opt_tiles_m2"]
        self.opt_value = data["opt_value"]
        self.symbols_on_m1 = data["symbols_on_m1"]
        self.symbols_on_m2 = data["symbols_on_m2"]
        self.name = data.get("name")
        self.symbols = data["symbols"]
        self.tiles = data["tiles"]

        # Add some calculated attributes
        self.symbol_size_sum = sum(symbol.size for symbol in self.symbols)
        self.tile_count = len(self.tiles)

    def get_data(self):
        return {
            "height": self.height,
            "symbol_size_bound": self.symbol_size_bound,
            "opt_value": self.opt_value,
            "opt_tiles_m1": self.opt_tiles_m1,
            "symbols_on_m1": self.symbols_on_m1,
            "opt_tiles_m2": self.opt_tiles_m2,
            "symbols_on_m2": self.symbols_on_m2,
            "symbol_indexes": [s.index for s in sorted(self.symbols)],
            "symbol_sizes": [s.size for s in sorted(self.symbols)],
            "tiles": sorted(sorted(s.index for s in t.symbols) for t in self.tiles),
        }

    def get_json(self) -> str:
        return data_to_json(self.get_data())

    def dump_json(self, json_path: Path) -> None:
        json_path.write_text(self.get_json())
