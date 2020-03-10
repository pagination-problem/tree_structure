# -*- coding: utf-8 -*
from time import sleep

from type_symbol import Symbol
from type_tile import Tile
from type_page import Page
from type_problem_input import ProblemInput

# Steps :
# 1 - Choose the height of the complete and balanced tree
# 2 - Choose the number of tiles
# 3 - Compute the number of leaves in the tree
# 4 - Pick as many leaves as we want tiles
# 5 - Create the symbols
# 6 - For each symbol/node, randomly pick a size
# 7 - Create the tiles

# Example of work :
# 1 - height H = 3
# 2 - nb_tiles = 5
# 3 - nb_leaves = 8
# The tree :
#          N1
#        /    \
#       /      \
#      /        \
#     /          \
#    N2          N3
#   /  \       /    \
#  N4   N5    N6    N7
# / \  / \   /  \  /  \
# 1 2  3  4  5  6  7   8
# 1 <-> N8  ; 2  <-> N9  ; 3  <-> N10 ; 4  <-> N11 ;
# 5 <-> N12 ; 6  <-> N13 ; 7  <-> N14 ; 8  <-> N15

# There are two indexes in the tree :
#   - the numbers without the letter 'N' (1 to 8) is the index of leaves only going from 1 to 2^H
#   - the numbers with the letter 'N'  (N1 to N15) is the index a node will get in a Breadth-first search.
# Both will be used in the generation.

# 4 - Leaves we picked (using their numbers) : 2,   4,   5,   6,   8
# 4 - Leaves we picked (using their numbers) : N9, N11, N12, N13, N15

# 5 - |N1| = 3 ; |N2| = 5 ; ....

import random
import math
import time

#Global variables
set_of_indexes_of_already_created_symbols = set()
set_of_all_the_symbols = set()
set_of_symbols_in_the_current_tile = set()

def find_father_index_of(index):
    """!! We assume that the index given in parameter is in the "full numbering", the one for all the nodes
    going from "N1" (the root) to "N??" the right most leaf."""
    return math.floor(index / 2)

def changing_the_numbering_of(index, height):
    # This function takes a leaf index in the leaf-only numbering and return the index of the same node
    # but with its index with the numbering for all the node (going from "N1" (the root)
    # to "N??" the right most leaf)
    nb_internal_nodes = 0
    for i in range(0, height):
        nb_internal_nodes += 2**i
    
    return nb_internal_nodes + index

def find_symbol_of_index_in_set(index, set_of_interest):
    for s in set_of_interest:
        if s.index == index:
            return s

def update_of_the_sets_about_symbols(symbol):
    global set_of_indexes_of_already_created_symbols
    global set_of_all_the_symbols
    global set_of_symbols_in_the_current_tile
    set_of_symbols_in_the_current_tile.add(symbol)
    set_of_indexes_of_already_created_symbols.add(symbol.index)
    set_of_all_the_symbols.add(symbol)

def input_creation(input_name, height, nb_tiles, max_size, seed):
    # 3 - Compute the number of leaves in the tree
    nb_leaves = 2**height

    # 4 - Pick as many leaves as we want tiles
    set_of_index_of_of_chosen_tiles = set()
    while (len(set_of_index_of_of_chosen_tiles) < nb_tiles):
        random_index = random.randint(1, nb_leaves) # return a random integer k such that LB <= N <= UP.
        set_of_index_of_of_chosen_tiles.add(random_index)

    set_of_future_tiles_in_input = set()
    global set_of_indexes_of_already_created_symbols
    global set_of_all_the_symbols
    global set_of_symbols_in_the_current_tile

    # 5 - For each tile, randomly pick a size for each intern node
    for i in set_of_index_of_of_chosen_tiles:
        index_full_numbering = changing_the_numbering_of(i, height)
        
        if index_full_numbering == 1: #The root can't have a size = 0
            random_size = random.randint(1, max_size)
        else:
            random_size = random.randint(0, max_size)

        s = Symbol(index_full_numbering, random_size)

        update_of_the_sets_about_symbols(s)

        for j in range(0, height):
            father_index = find_father_index_of(index_full_numbering)

            if father_index not in set_of_indexes_of_already_created_symbols:
                if father_index == 1: #The root can't have a size = 0
                    random_size = random.randint(1, max_size)
                else:
                    random_size = random.randint(0, max_size)
                
                father_s = Symbol(father_index, random_size)
                update_of_the_sets_about_symbols(father_s)
            else:
                temp_symbol = find_symbol_of_index_in_set(father_index, set_of_all_the_symbols)
                set_of_symbols_in_the_current_tile.add(temp_symbol)
            index_full_numbering = father_index

        set_of_symbols_in_the_current_tile = sorted(set_of_symbols_in_the_current_tile)
        set_of_future_tiles_in_input.add(Tile(set_of_symbols_in_the_current_tile))
        set_of_symbols_in_the_current_tile = set() #we empty the set for the next tile

    #Conclusion
    my_input = ProblemInput(set_of_future_tiles_in_input, input_name, height, max_size, seed)
    #print(my_input)
    #print("input_creation : everything is fine.\n")
    return my_input

def generate_the_write_name(height,  nb_tiles, i):
    if 1 <= i <= 9:
        return "H" + str(height) + "-nbT" + str(nb_tiles) + "-00" + str(i)
    elif 10 <= i <= 99:
        return "H" + str(height) + "-nbT" + str(nb_tiles) + "-0" + str(i)
    else: # 100 <= i <= 999:
        return "H" + str(height) + "-nbT" + str(nb_tiles) + "-" + str(i)

def generating_inputs(nb_inputs, height, nb_tiles, symbol_size_max, full_path_for_where_to_store_them):
    #name_base = "H" + str(height) + "-nbT" + str(nb_tiles)
    i = 1
    while i <= nb_inputs:
        name = generate_the_write_name(height,  nb_tiles, i)
        sleep(1)
        seed = time.time()
        random.seed(seed)
        my_input = input_creation(name, height, nb_tiles, symbol_size_max, seed)
        my_input.write_instance_in_json_file(full_path_for_where_to_store_them)
        with open(full_path_for_where_to_store_them +  "sizes.txt", "a") as f:
            print(f"{i};{my_input.get_sum_symbol_sizes()}", file=f)
        print(f"size of input {i} = {my_input.get_sum_symbol_sizes()}")
        i = i + 1

if __name__ == '__main__':
    print("Begin.\n")
    start_time = time.time()

    height = 9
    nb_tiles = 500
    nb_of_generated_inputs = 100
    symbol_size_max = 50
    no_type = 3
    no_sub_type = "d"
    
    #full_path_for_where_to_store_them = "C:\\Users\\sarah\\Documents\\These\\Sub-problems\\2__tree-merging__Cmax\\3-Programmation\\Inputs\\inputs_for_tests\\"
    #full_path_for_where_to_store_them = "C:/Users/sarah/Documents/These/Sub-problems/2__tree-merging__Cmax/3-Programmation/Inputs/2" + str(nb_tiles) + "_tiles/"
    # C:\Users\sarah\Documents\These\Sub-problems\2__tree-merging__Cmax\4-Shared_programmation\tree_structure\inputs
    full_path_for_where_to_store_them = f"C:/Users/sarah/Documents/These/Sub-problems/2__tree-merging__Cmax/4-Shared_programmation/tree_structure/inputs/type_{no_type}/{no_sub_type}/"
    print(full_path_for_where_to_store_them)
    generating_inputs(nb_of_generated_inputs, height, nb_tiles, symbol_size_max, full_path_for_where_to_store_them)
    
    interval = time.time() - start_time  
    print ("input_creation : required time to generate ", nb_of_generated_inputs, " inputs with ", nb_tiles, " tiles is ", interval, " seconds.\n")
    print("End.")



# height = 5
    # nb_tiles = 5
    # nb_of_generated_inputs = 100
    # symbol_size_max = 50

    # height = 5
    # nb_tiles = 20
    # nb_of_generated_inputs = 100

    # height = 6
    # nb_tiles = 50
    # nb_of_generated_inputs = 500

    # height = 7
    # nb_tiles = 70
    # nb_of_generated_inputs = 200

    # height = 7
    # nb_tiles = 80
    # nb_of_generated_inputs = 200

    # height = 7
    # nb_tiles = 90
    # nb_of_generated_inputs = 200

    # height = 7
    # nb_tiles = 100
    # nb_of_generated_inputs = 400
    # symbol_size_max = 30

    # height = 8
    # nb_tiles = 200
    # nb_of_generated_inputs = 100
    # symbol_size_max = 30

    # height = 10
    # nb_tiles = 400
    # nb_of_generated_inputs = 50
    # symbol_size_max = 50

    # height = 12
    # nb_tiles = 600
    # nb_of_generated_inputs = 25
    # symbol_size_max = 50