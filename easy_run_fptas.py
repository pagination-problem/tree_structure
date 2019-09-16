# -*- coding: utf-8 -*
import tools
import time
import fptas

if __name__ == '__main__':
    dir_path_for_inputs = "C:\\Users\\sarah\\Documents\\These\\Sub-problems\\2__tree-merging__Cmax\\4-Shared_programmation\\tree_structure\\inputs"
    filename = "H3-nbT5-001"
    my_input = tools.load_json_instance_from(dir_path_for_inputs, filename)

    number_of_tiles = 5
    number_of_iterations = 3
    epsilon = 0.1
 
    print("Beginning of the run.")
    start = time.time()
    (Cmax, number_of_generated_states) = fptas.FPTAS(my_input, epsilon/10)
    stop = time.time()
    duration = stop - start
    print("Time needed : ", duration)
    print(f"Cmax =  {Cmax}; number of states generated = {number_of_generated_states}")
    