# -*- coding: utf-8 -*
import tools
import time
import fptas
from improved_fptas import improved_FPTAS
import datetime

if __name__ == '__main__':
    dir_path_for_inputs = "inputs/200-tiles"
    root = "H3-nbT5-"
    epsilon = 0.1
    path = f"results/txt/results_200-tiles_{epsilon}-epsilon.txt"  

    print(f"Beginning of the run at {datetime.datetime.now()}")

    for i in range(1, 101): # ! Upper bound not included
        filename = f"{root}{i:03}"

        Cmax1 = number_of_generated_states1 = 0
        Cmax2 = number_of_generated_states2 = 0
        my_input = tools.load_json_instance_from(dir_path_for_inputs, filename)
        
        print(f"input number : {filename} at {datetime.datetime.now()}")

        start1 = time.time()
        (Cmax1, number_of_generated_states1) = fptas.FPTAS(my_input, epsilon)
        stop1 = time.time()
        print("Time needed for FPTAS: ", stop1 - start1)
        print(f"FPTAS : Cmax =  {Cmax1}; number of states generated = {number_of_generated_states1}")

        start2 = time.time()
        (Cmax2, number_of_generated_states2) =  improved_FPTAS(my_input, epsilon)
        stop2 = time.time()
        print("Time needed for iFPTAS: ", stop2 - start2)
        print(f"iFPTAS : Cmax =  {Cmax2}; number of states generated = {number_of_generated_states2}")
        
        my_str = f"\n{filename};{Cmax1};{stop1-start1};{number_of_generated_states1};{Cmax2};{stop2-start2};{number_of_generated_states2};"
        file = open(path, "a")
        file.write(my_str) 
        file.close()

    print(f"End of the run at {datetime.datetime.now()}")
    