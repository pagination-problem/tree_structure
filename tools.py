from type_problem_input import ProblemInput
from type_symbol import Symbol
from type_tile import Tile
import os

import json

def my_range(start, end, step):
    while start <= end:
        yield start
        start += step

def find_symbol_by_index_in_set(index, set_of_interest):
    for s in set_of_interest:
        if s.index == index:
            return s

def creating_the_set_of_all_the_symbols_in_the_intput(the_set, symbols):
    set_of_symbol_indexes = set()
    for temp in the_set:
        my_str = str(temp).replace("[", "")
        my_str = str(my_str).replace("]", "")
        my_str = my_str.replace(" ", "")
        before, separator, after = my_str.partition("-")
        index = int(before.replace("N", ""))
        symbols.add(Symbol(index, int(after)))
        set_of_symbol_indexes.add(index)
    return (symbols, set_of_symbol_indexes)

def transforming_a_tile_into_a_set_of_the_indexes_og_its_symbols(tile_in_str):
    my_str = str(tile_in_str).replace("[", "")
    my_str = str(my_str).replace("]", "")
    my_str = my_str.replace(" ", "")
    my_str = my_str.replace("N", "")
    temp_set = my_str.split(",")
    set_of_indexes_of_symbols_in_tile = set()
    for s in temp_set:
        set_of_indexes_of_symbols_in_tile.add(int(s))

    return set_of_indexes_of_symbols_in_tile

def load_json_instance_from(complete_path_to_input, input_name_without_extension):
    whereToLoad = os.path.join(complete_path_to_input, f"{input_name_without_extension}.json")
    input_in_set = json.loads(open(whereToLoad).read())

    tiles = set()
    height = input_in_set["height"]
    max_symbol_size = input_in_set["max_symbol_size"]

    symbols = set()
    symbols, set_of_symbol_indexes = creating_the_set_of_all_the_symbols_in_the_intput(input_in_set["symbols"], symbols)

    symbols_in_current_tile = set()
    for temp in input_in_set["tiles"]:
        temp_set = transforming_a_tile_into_a_set_of_the_indexes_og_its_symbols(temp)
        for i in temp_set:
            symbols_in_current_tile.add(find_symbol_by_index_in_set(i, symbols))
        tiles.add(Tile(symbols_in_current_tile))
        symbols_in_current_tile = set()

    
    opt_value = input_in_set["opt_value"]
    tiles_on_m1 = set()
    tiles_on_m2 = set()

    print("For now, the loading from json file does NOT load the optimal solution in the file.\n")
    return ProblemInput(tiles, input_name_without_extension, height, max_symbol_size, opt_value, tiles_on_m1, tiles_on_m2)

def generating_one_recap_file(nb_of_tiles, epsilon, where_to_store_the_files):
    #100-tiles_0.3_recap.txt
    name_of_file = str(nb_of_tiles) + "-tiles_" + str(epsilon) + "_recap"
    path = where_to_store_the_files + "\\" + name_of_file + ".txt"
    str_to_write = "intput_name;val_fptas;time_fptas;total_nb_of_generated_states;val_iFPTAS;time_iFPTAS;total_nb_of_generated_states\n"

    fichier = open(path, "w")
    fichier.write(str_to_write) 
    fichier.close()

def generating_all_the_recap_files(nb_of_tiles, range_of_epsilon_values, where_to_store_the_files):
    for epsilon in range_of_epsilon_values:
        generating_one_recap_file(nb_of_tiles, epsilon, where_to_store_the_files)

# if __name__ == '__main__':
#     print("Begin.\n")
#     path = "C:\\Users\\sarah\\Documents\\These\\2,tree-merging,Cmax\\FPTAS_for_tree_Pagination\\Programmation\\Inputs\\test\\"
#     file_name = "IMPORTANT"
#     loaded_input = load_json_instance_from(path, file_name)
#     print(loaded_input)
#     print("End.")

if __name__ == '__main__':
    range_of_epsilon_values = [0.1, 0.3, 0.9]
    # range_of_epsilon_values = [0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9]
    nb_tiles = 5
    path = "C:\\Users\\sarah\\Documents\\These\\Sub-problems\\2__tree-merging__Cmax\\3-Programmation\\Results\\tests\\recap"
    
    generating_all_the_recap_files(nb_tiles, range_of_epsilon_values, path)