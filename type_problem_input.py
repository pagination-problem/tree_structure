# -*- coding: utf-8 -*

import json
import re

from functools import reduce #For the reduce function 
from collections import Counter #For the Counter function 
from fractions import Fraction as F
import itertools #for the zip function 
import math

from type_tile import Tile

class ProblemInput(list) :
    """

    This class defines what the input of my problem is.
    It consists of a list of tiles.

    It also contains a name (str) to link the input problem to the solution found by the heuristics.
    To find it easily, we will also store the name of the .json file it comes from.

    The attributes of this class are :
        - name : str
        - tileSet : a 'list' of tiles
        - json_file_name : str
        - an optimal value : opt_value
        - an optimal repartition of the tiles : opt_tiles_m1 and opt_tiles_m2

    The optimal values can be unknown.
    """

    def __init__(self, tiles, name, height = None, max_symbol_size = None, seed = None, opt_value = None, opt_tiles_m1 = set(), opt_tiles_m2 = set()):
        """
        The format of 'name' given in input will be : H3-nbT5-001
        which means that this input comes from a tree of height = 3. It has 5 tiles and its the first one
        with these characteristics.
        """
        list.__init__(self, [(tile if isinstance(tile,Tile) else Tile(tile)) for tile in tiles])
        self.name = name
        self.tileSet = frozenset(tiles)
        self.height = height
        self.max_symbol_size = max_symbol_size
        self.sum_symbol_sizes = -1

        self.opt_value = opt_value
        self.opt_tiles_m1 = set(opt_tiles_m1)
        self.opt_tiles_m2 = set(opt_tiles_m2)

        self.seed = seed
        

    # def copy(self): -> So it is NOT tested
    #     return ProblemInput(self.tileSet, self.name, self.opt_value, self.opt_tiles_m1, self.opt_tiles_m1)

    def __contains__(self, tile):
        return tile in self.tileSet
    
    def __repr__(self):
        #print an instance in that way :
        # { tile_1, tile_2, tile_3, ... }
        return "{%s}" % ",".join(repr(tile) for tile in self)

    def __str__(self):
        #print an instance in that way :
        # { tile_1, tile_2, tile_3, ... }
        return "{%s}" % ",".join(repr(tile) for tile in self)

    def __len__(self):
        return len(self.tileSet) 
    
    def toList(self):
        return [tile.symbols for tile in self]
     
    def add(self,tile):
        self.append(tile)

    def remove(self,tileOrIndex):
        """ Suppress a tile by index or value. """
        if type(tileOrIndex) is int:
            del(self[tileOrIndex])
        else:
            list.remove(self,tileOrIndex)
        self.tileSet = frozenset(self)
    
    def isEmpty(self):
        return len(self) == 0

    def get_tiles(self):
        return self.tileSet

    def get_tile_corresponding_to_this_leaf_index(self, index):
        """
        index is in the 'full' numbering (the one for all the nodes in the tree, not just for the leaves) 
        """
        for t in self.tileSet:
            s = t.get_leaf_symbol()
            if s.index == index:
                return t

    def get_sum_symbol_sizes(self):
        if self.sum_symbol_sizes == -1:
            sum = 0
            symbol_set = set()
            for t in self.tileSet:
                symbol_set = symbol_set.union(t.symbols)

            for s in symbol_set:
                sum += s.size
            self.sum_symbol_sizes = sum
        else:
            sum = self.sum_symbol_sizes
        return sum
    
    def full_instance_to_str(self):
        symbol_set = set()
        for t in self.tileSet:
            symbol_set = symbol_set.union(t.symbols)
        symbol_set = sorted(symbol_set) #So symbol_set will be in alphabetical order

        if len(self.opt_tiles_m1) == 0:
            symbol_set_on_m1 = "None"
            str_for_tiles_on_m1 = "None"
        else :
            symbol_set_on_m1 = set()
            for t in self.opt_tiles_m1:
                symbol_set_on_m1 = symbol_set_on_m1.union(t.symbols)
            symbol_set_on_m1 = sorted(symbol_set_on_m1)
            str_for_tiles_on_m1 = str(self.opt_tiles_m1)

        if len(self.opt_tiles_m2) == 0:
            symbol_set_on_m2 = "None"
            str_for_tiles_on_m2 = "None"
        else :
            symbol_set_on_m2 = set()
            for t in self.opt_tiles_m2:
                symbol_set_on_m2 = symbol_set_on_m2.union(t.symbols)
            symbol_set_on_m2 = sorted(symbol_set_on_m2)
            str_for_tiles_on_m2 = str(self.opt_tiles_m2)

        result = ["[\n {"]
        result.append(f'"tiles" : {self}')
        result.append(f'"symbols" : {symbol_set}')
        result.append(f'"height" : {self.height}')
        result.append(f'"max_symbol_size" : {self.max_symbol_size}')
        result.append(f'"opt_value" : {self.opt_value}')
        result.append(f'"opt_tiles_m1" : {str_for_tiles_on_m1}')
        result.append(f'"symbols_on_m1" : {symbol_set_on_m1}')
        result.append(f'"opt_tiles_m2" : {str_for_tiles_on_m2}')
        result.append(f'"symbols_on_m2" : {symbol_set_on_m2}')
        result.append(f'"seed" : {self.seed}')
        result.append("\n }\n]")
        return ",\n".join(result)

    def write_instance_in_json_file(self, directory_path):
        directory_path = directory_path + self.name + ".json"

        temp_L_1 = list()
        for t in self.tileSet:
            temp_L_1.append(str(t))

        temp_L_symbols = list()
        symbol_set = set()
        for t in self.tileSet:
            symbol_set = symbol_set.union(t.symbols)
        symbol_set = sorted(symbol_set)
        for s in symbol_set:
            temp_L_symbols.append("["+str(s)+" - "+ str(s.size)+"]")

        temp_L_2 = list()
        for t in self.opt_tiles_m1:
            temp_L_2.append(str(t))

        temp_L_3 = list()
        for t in self.opt_tiles_m2:
            temp_L_3.append(str(t))

        symbol_set_on_m1 = set()
        for t in self.opt_tiles_m1:
            symbol_set_on_m1 = symbol_set_on_m1.union(t.symbols)
        symbol_set_on_m1 = sorted(symbol_set_on_m1)
        temp_L_symbols_m1 = list()
        for s in symbol_set_on_m1:
            temp_L_symbols_m1.append(str(s))

        symbol_set_on_m2 = set()
        for t in self.opt_tiles_m2:
            symbol_set_on_m2 = symbol_set_on_m2.union(t.symbols)
        symbol_set_on_m2 = sorted(symbol_set_on_m2)
        temp_L_symbols_m2 = list()
        for s in symbol_set_on_m2:
            temp_L_symbols_m2.append(str(s))
        
        
        my_dict = dict()
        my_dict["tiles"] = temp_L_1
        my_dict["symbols"] = temp_L_symbols
        my_dict["height"] = self.height
        my_dict["max_symbol_size"] = self.max_symbol_size
        my_dict["opt_value"] = self.opt_value
        my_dict["opt_tiles_m1"] = temp_L_2
        my_dict["symbols_on_m1"] = temp_L_symbols_m1
        my_dict["opt_tiles_m2"] = temp_L_3
        my_dict["symbols_on_m2"] = temp_L_symbols_m2
        my_dict["seed"] = self.seed

        my_str = json.dumps(my_dict, ensure_ascii=False, indent=1)
        my_str = re.sub(r'"\[[\d,\s]+\]"',lambda s: s.group(0).replace("\"",""),my_str)

        fichier = open(directory_path, "w")
        fichier.write(my_str) 
        fichier.close()

    def write_instance_in_text_file(self, directory_path):
        #format :
        # [
        #  {
        #  "tiles" : {[N1, N2],[N1, N2, N3],[N2, N4]},
        #  "symbols" : {N1, N2, N3, N4}
        #  "opt_value" : Unknown,
        #  "opt_tiles_m1" :  None,
        #  "symbols_on_m1" : None
        #  "opt_tiles_m2" : None
        #  "symbols_on_m2" : None
        #  "seed" : ...
        #  }
        # ]
        directory_path = directory_path + "\\" + self.name + ".txt"

        my_str = self.full_instance_to_str()

        fichier = open(directory_path, "w")
        fichier.write(my_str) 
        fichier.close()

    