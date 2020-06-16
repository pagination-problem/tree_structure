import json
import sys
from functools import reduce
from hashlib import sha256
from pathlib import Path
from random import randint, randrange, sample, seed

from statistics import mean, pstdev
from instance import Instance
from tile import Tile
from symbol import Symbol

from numpy import base_repr

from goodies import data_to_json

import numpy as np
from scipy import optimize


class InstanceMaker:
    def __init__(
        self,
        height,
        arity=2,
        tile_min_size=2,
        common_symbol_min_count=0,
        common_symbol_max_count=sys.maxsize,
        cost_mean=20,
        min_cost_standard_deviation=3,
        max_cost_standard_deviation=8,
        method="classic",
        min_symbol_weight_bound=0,
        max_symbol_weight_bound=np.inf,
    ):
        self.leaves = list(range(arity ** (height - 1), arity ** height))
        self.height = height
        self.arity = arity
        self.tile_min_size = tile_min_size
        self.common_symbol_min_count = common_symbol_min_count
        self.common_symbol_max_count = common_symbol_max_count
        self.cost_mean = cost_mean
        self.min_cost_standard_deviation = min_cost_standard_deviation
        self.max_cost_standard_deviation = max_cost_standard_deviation
        self.method = method #if method==classic, we generate instances without controlling the mean and the standard deviation. 
                             #if method==stats (or anything else in fact), it means we want to control the stats
        self.min_symbol_weight_bound = min_symbol_weight_bound
        self.max_symbol_weight_bound = max_symbol_weight_bound

    def ancestors(self, node):
        """Return all the ancestors of a node in a complete n-ary tree, including itself."""
        result = [node]
        while node:
            node //= self.arity
            result.append(node)
        return result[::-1]

    def create_path_sample(self, leaf_rate):
        """Create all paths from the root to a random sample of leaves in a complete n-ary tree."""
        assert 0 <= leaf_rate <= 1
        self.paths = sorted(
            self.ancestors(leaf)
            for leaf in sample(self.leaves, round(len(self.leaves) * leaf_rate))
        )

    def remove_random_nodes(self, kill_rate):
        """
        Suppress a certain percentage (expressed as a floating-point value in [0, 1]) of the distinct
        nodes occurring in self.paths.
        """
        if 0 < kill_rate <= 1:
            candidates = set.union(*map(set, self.paths))
            to_kill = set(sample(candidates, round(len(candidates) * kill_rate)))
            for path in self.paths:
                path[:] = [node for node in path if node not in to_kill]
                if len(path) < self.tile_min_size:
                    raise TileTooSmall
            if len(set(map(tuple, self.paths))) != len(self.paths):
                raise DuplicateTiles

            for (i, path1) in enumerate(self.paths):
                for (j, path2) in enumerate(self.paths[:i]):
                    path1[:] = [node for node in path1]
                    path2[:] = [node for node in path2]
                    ps1 = set(path1)
                    ps2 = set(path2)
                    if ps1.issubset(ps2) or ps2.issubset(ps1):
                        raise TileContainedInAnother

    def renumber_symbols(self):
        """Update self.paths with all their nodes renumbered consecutively."""
        remaining_nodes = set.union(*map(set, self.paths))
        self.node_count = len(remaining_nodes)
        renumber_node = dict((old, new) for (new, old) in enumerate(remaining_nodes)).get
        self.paths = [list(map(renumber_node, path)) for path in self.paths]
        self.common_symbols = reduce(lambda s1, s2: set(s1).intersection(s2), self.paths)
        if len(self.common_symbols) < self.common_symbol_min_count:
            raise TooFewCommonSymbols
        if len(self.common_symbols) > self.common_symbol_max_count:
            raise TooManyCommonSymbols

    def create_random_weights(self, max_weight):
        """Return a list of n random weights, where n is the number of distinct nodes in self.paths."""
        self.weights = [1 + randrange(max_weight) for _ in range(self.node_count)]

    def compute_occurrences_of_p_i(self, the_instance):
        l = list()
        p_i_occurrences = [0 for i in range(the_instance.symbol_count)]

        for (new, new_tile) in enumerate(the_instance.tiles):
            for last_tile in the_instance.tiles[:new]:
                [l.append(symbol.index) for symbol in new_tile - last_tile]
                
            for s in l:
                p_i_occurrences[s] = p_i_occurrences[s] + 1
                
            l = list()
            
        for new_tile in the_instance.tiles:
            for symbol in new_tile:
                p_i_occurrences[symbol.index] = p_i_occurrences[symbol.index] + 1
                
        return p_i_occurrences

    def compute_coefficient_for_quadratic_var(self, the_instance):
        try:
            coeff_for_quadratic =  [[0 for y in range(the_instance.symbol_count)] for x in range(the_instance.symbol_count)]
        except MemoryError:
            print("System out of memory, now quitting")
        else:
            #traitement basé sur la première colonne de la matrice costs
            for tile in the_instance.tiles:
                for s1 in tile:
                    for s2 in tile:
                        if s1.index == s2.index:
                            coeff_for_quadratic[s1.index][s2.index] = coeff_for_quadratic[s1.index][s2.index] + 1
                        elif s1.index < s2.index:
                            coeff_for_quadratic[s1.index][s2.index] = coeff_for_quadratic[s1.index][s2.index] + 2

                            
            # Traitement du reste de la matrice :
            for (new, new_tile) in enumerate(the_instance.tiles):
                for last_tile in the_instance.tiles[:new]:
                    for s1 in new_tile - last_tile:
                        for s2 in new_tile - last_tile:
                            if s1.index == s2.index:
                                coeff_for_quadratic[s1.index][s2.index] = coeff_for_quadratic[s1.index][s2.index] + 1
                            elif s1.index < s2.index:
                                coeff_for_quadratic[s1.index][s2.index] = coeff_for_quadratic[s1.index][s2.index] + 2
    
        return coeff_for_quadratic

    def create_weights_according_to_mean_and_deviation(
        self,
        the_instance,
        p_i_occurrences,
        coeff_for_quadratic
    ):
        cell_count_in_costs_matrix = (the_instance.tile_count * (the_instance.tile_count + 1)) / 2
        p_i_count = self.node_count

        def f(x):
            # The objective function is not important
            return 1

        def mean_constraint(x):
            return np.dot(p_i_occurrences, x) - cell_count_in_costs_matrix * self.cost_mean

        def define_standard_deviation(x, coeff_for_quadratic):
            res = self.cost_mean * self.cost_mean  * cell_count_in_costs_matrix
            for l in range(p_i_count):
                for c in range(l, p_i_count):
                    res = res + coeff_for_quadratic[l][c] * x[l] * x[c]

            for l in range(p_i_count):
                res = res - 2 * self.cost_mean * coeff_for_quadratic[l][l] * x[l]
            
            return res * (1/cell_count_in_costs_matrix)

        def sd_constraint_1(x, coeff_for_quadratic=coeff_for_quadratic): #LB for the standard deviation
            return define_standard_deviation(x, coeff_for_quadratic) - (self.min_cost_standard_deviation * self.min_cost_standard_deviation)

        def sd_constraint_2(x, coeff_for_quadratic=coeff_for_quadratic): #UB for the standard deviation
            return  (self.max_cost_standard_deviation * self.max_cost_standard_deviation) - define_standard_deviation(x, coeff_for_quadratic)
        
        cons = [{'type': 'eq', 'fun': mean_constraint},
        {'type': 'ineq', 'fun': sd_constraint_1},
        {'type': 'ineq', 'fun': sd_constraint_2}]

        bnds = list()
        for i in range(p_i_count):
            bnds.append([self.min_symbol_weight_bound, self.max_symbol_weight_bound])

        variables =  np.array([0 for y in range(p_i_count)])
        value_distrib = optimize.minimize(f, variables, method="SLSQP", bounds=bnds, constraints=cons)
        # if we want more control over the possible values for the p_i, we will need to store the values read
        # in this document line 294 : cfg["min_symbol_weight_bound"], cfg["max_symbol_weight_bound"]
    
        return value_distrib.x

    def __call__(self, leaf_rate, kill_rate, symbol_weight_bound):
        self.create_path_sample(leaf_rate)
        self.remove_random_nodes(kill_rate)
        self.renumber_symbols()

        if self.method == "classic":
            self.create_random_weights(symbol_weight_bound)
        else:
            self.weights = [0 for i in range(self.node_count)]
            #self.create_random_weights(symbol_weight_bound)
            temporary_dict = {
                "name": "temp",
                "height": self.height,  # seems useless
                "symbol_weight_bound": max(self.weights),  # may be less than symbol_weight_bound
                "symbol_count": self.node_count,
                "common_symbols": sorted(self.common_symbols),
                "symbol_weights": self.weights,
                "cost_mean": self.cost_mean,
                "cost_standard_deviation": "N/A",
                "tiles": sorted(self.paths),
                "costs": "N/A"
            }
            temporary_instance = Instance(temporary_dict)

            p_i_occurrences = self.compute_occurrences_of_p_i(temporary_instance)
            coefficients_for_quadratic_var = self.compute_coefficient_for_quadratic_var(temporary_instance)
            temp_weights = self.create_weights_according_to_mean_and_deviation(temporary_instance, p_i_occurrences, coefficients_for_quadratic_var)
            self.weights =  [round(temp_weights[i], 1) for i in range(self.node_count)] #tranformation necessary because json doesnt know NDarray of numpy
            
        identifier = f"{self.paths},{self.weights}".encode("utf8")
        returned_dict = {
            "name": "h={height:02}_t={tiles:03}_s={symbols:03}_m={max_weight:02}__{hash_value}.json".format(
                height=self.height,
                tiles=len(self.paths),
                symbols=self.node_count,
                max_weight=max(self.weights),
                hash_value=base_repr(int(sha256(identifier).hexdigest(), 16), base=36)[:4],
            ),
            "height": self.height,  # seems useless
            "symbol_weight_bound": max(self.weights),  # may be less than symbol_weight_bound
            "symbol_count": self.node_count,
            "common_symbols": sorted(self.common_symbols),
            "symbol_weights": self.weights,
            "cost_mean": "N/A",
            "cost_standard_deviation": "N/A",
            "tiles": sorted(self.paths),
            "costs": "N/A"
        }
        
        temporary_instance = Instance(returned_dict)

        costs = [[tile.weight] * (temporary_instance.tile_count + 1) for tile in temporary_instance.tiles]
        for (new, new_tile) in enumerate(temporary_instance.tiles):
            for (last, last_tile) in enumerate(temporary_instance.tiles[:new]):
                costs[new][last] = sum(symbol.weight for symbol in new_tile - last_tile)
        
        lower_triangle_costs = [row[: i + 1] for (i, row) in enumerate(costs)]
        flattened_costs = reduce(lambda x, y: x + y, lower_triangle_costs)
        cost_mean = mean(flattened_costs)
        cost_standard_deviation = pstdev(flattened_costs)

        returned_dict["cost_mean"] = round(cost_mean, 1)
        returned_dict["cost_standard_deviation"] = round(cost_standard_deviation, 1)
        returned_dict["costs"] = costs

        return returned_dict


class TileTooSmall(Exception):
    ...


class DuplicateTiles(Exception):
    ...


class TooManyCommonSymbols(Exception):
    ...


class TooFewCommonSymbols(Exception):
    ...


class TileContainedInAnother(Exception):
    ...


def dump_instances(config_path):
    cfg = json.loads(Path(config_path).read_text())
    directory = Path(cfg["output_directory"])
    directory.mkdir(parents=True, exist_ok=True)
    seed(cfg["seed"])
    i = 1
    column = 1
    while i <= cfg["instance_count"]:
        height = randint(cfg["min_height"], cfg["max_height"])
        maker = InstanceMaker(
            height,
            cfg["arity"],
            cfg["tile_min_size"],
            cfg["common_symbol_min_count"],
            cfg["common_symbol_max_count"],
            cfg["cost_mean"],
            cfg["min_cost_standard_deviation"],
            cfg["max_cost_standard_deviation"],
            cfg["method"],
            cfg["min_symbol_weight_bound"],
            cfg["max_symbol_weight_bound"]
        )
        leaf_rate = randint(cfg["min_tile_percentage"], cfg["max_tile_percentage"]) / 100.0
        kill_rate = randint(cfg["min_kill_percentage"], cfg["max_kill_percentage"]) / 100.0
        symbol_weight_bound = randint(
            cfg["min_symbol_weight_bound"], cfg["max_symbol_weight_bound"]
        )
        try:
            instance = maker(leaf_rate, kill_rate, symbol_weight_bound)
        except DuplicateTiles:
            outcome = "D"
        except TileTooSmall:
            outcome = "S"
        except TooFewCommonSymbols:
            outcome = "F"
        except TooManyCommonSymbols:
            outcome = "M"
        except TileContainedInAnother:
            outcome = "C"
        else:
            (directory / instance["name"]).write_text(data_to_json(instance))
            outcome = "."
            i += 1
        print(outcome, end="" if column % 80 else "\n", flush=True)
        column += 1


if __name__ == "__main__":
    filename =  "instances/sarah/test_config.json"  if len(sys.argv) <= 1 else sys.argv[1]
    # alternatively: filename =  "instances/snapshots.json"  if len(sys.argv) <= 1 else sys.argv[1]
    dump_instances(filename)

