# -*- coding: utf-8 -*
import tools
import time
from fptas_object import Fptas
import improved_fptas
import datetime
import sys
import os
import json

if __name__ == '__main__':

    # Read the configuration file

    config_path = os.path.join("configs", (sys.argv[1] if len(sys.argv) > 1 else "log") + ".json")
    with open(config_path) as f:
        config = json.loads(f.read())
    input_directory = config["input_directory"]
    output_directory = config["output_directory"]
    output_prefix = config["output_prefix"]
    log = config["log"]
    input_prefix = config["input_prefix"]
    epsilon = config["epsilon"]
    tile_count = config["tile_count"]

    # Apply log strategy

    solver = Fptas()
    output_mode = "w" if log else "a"
    solver.set_log_strategy(log)
    improved_fptas.set_log_strategy(log)

    # Run

    print(f"Beginning of the run at {datetime.datetime.now()}")

    output_filename = f"{output_directory}/{output_prefix}_{tile_count}-tiles_{epsilon}-epsilon.txt"
    already_processed = set()
    if not log and os.path.isfile(f"{output_filename}"):
        with open(output_filename) as f:
            already_processed = set(line.partition(";")[0] + ".json" for line in f.read().split("\n"))
    
    for filename in sorted(os.listdir(input_directory)):
        if not filename.endswith(".json"):
            continue

        my_input = tools.load_json_instance_from(input_directory, filename[:-5])
        if filename in already_processed:
            print(f"{filename} already generated!")
            continue
        
        Cmax1 = number_of_generated_states1 = 0
        Cmax2 = number_of_generated_states2 = 0
        print(f"input number : {filename} at {datetime.datetime.now()}")

        start1 = time.time()
        solver.initialize(my_input)
        (Cmax1, number_of_generated_states1) = solver.run(epsilon)
        stop1 = time.time()
        print("Time needed for FPTAS: ", stop1 - start1)
        print(f"FPTAS : Cmax =  {Cmax1}; number of states generated = {number_of_generated_states1}")

        start2 = time.time()
        (Cmax2, number_of_generated_states2) =  improved_fptas.run(my_input, epsilon)
        stop2 = time.time()
        print("Time needed for iFPTAS: ", stop2 - start2)
        print(f"iFPTAS : Cmax =  {Cmax2}; number of states generated = {number_of_generated_states2}")
        
        if not log:
            my_str = f"{filename[:-5]};{Cmax1};{stop1-start1};{number_of_generated_states1};{Cmax2};{stop2-start2};{number_of_generated_states2}"
            with open(output_filename, output_mode) as f:
                print(my_str, file=f)

        if log:
            log_filename = f"{output_directory}/{filename[:-5]}_{epsilon}-epsilon.txt"
            result = [
                "FPTAS:",
                "\n".join(solver.log_result),
                "Improved FPTAS:",
                "\n".join(improved_fptas.log_result),
            ]
            with open(log_filename, "w") as f:
                f.write("\n".join(result))
    print(f"End of the run at {datetime.datetime.now()}")
