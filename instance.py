import json
from pathlib import Path
from typing import Dict, Union
from math import ceil

from regex import sub

from tile import Tile
from symbol import Symbol
from goodies import data_to_json


class Instance:
    def __init__(self, path_or_data: Union[Path, Dict]):

        # Create a new dictionary from the data
        if isinstance(path_or_data, Path):
            data = json.loads(path_or_data.read_text())
            data["name"] = path_or_data.name
        else:
            data = path_or_data.copy()  # avoid mutating the input data

        # Convert raw symbols and tiles (simple lists of integers) into appropriate objects
        d = {s[0]: Symbol(*s) for s in enumerate(data.pop("symbol_weights"))}
        data["symbols"] = frozenset(d.values())
        data["tiles"] = [Tile([d[i] for i in t]) for t in data.pop("tiles")]

        # Populate the other fields without touching the raw values
        self.name = data.get("name")
        self.height = data["height"]
        self.symbol_weight_bound = data["symbol_weight_bound"]
        self.symbol_count = data["symbol_count"]
        self.symbols = data["symbols"]
        self.tiles = data["tiles"]
        self.costs = data["costs"]
        self.cost_standard_deviation = data["cost_standard_deviation"]
        self.cost_mean = data["cost_mean"]

        # Add some calculated attributes
        self.symbol_weight_sum = sum(symbol.weight for symbol in self.symbols)
        self.tile_count = len(self.tiles)

    def get_data(self):
        return {
            "name": self.name,
            "height": self.height,
            "symbol_weight_bound": self.symbol_weight_bound,
            "symbol_count": self.symbol_count,
            "symbol_weights": [s.weight for s in sorted(self.symbols)],
            "cost_mean": self.cost_mean,
            "cost_standard_deviation": self.cost_standard_deviation,
            "tiles": sorted(sorted(s.index for s in t.symbols) for t in self.tiles),
            "costs": self.costs,
        }

    def get_json(self) -> str:
        return data_to_json(self.get_data())

    def dump_json(self, json_path: Path) -> None:
        json_path.write_text(self.get_json())
    
    def copy_with_hashed_symbols(self, epsilon):
        data = self.get_data()
        delta = (epsilon * self.symbol_weight_sum) / (2 * self.symbol_count)
        data["symbol_weight_bound"] = ceil(self.symbol_weight_bound / delta)
        data["symbol_weights"] = [ceil(s.weight / delta) for s in sorted(self.symbols)]
        return Instance(data)
