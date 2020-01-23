import tools
import time
from fptas import Fptas
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
    solver.set_log_strategy(log)
    output_mode = "w" if log else "a"

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
        if filename in already_processed:
            print(f"{filename} already generated!")
            continue

        solver.set_instance(tools.load_json_instance_from(input_directory, filename[:-5]))
        print(f"input number : {filename} at {datetime.datetime.now()}")
        
        if log:
            log_filename = f"{output_directory}/{filename[:-5]}_{epsilon}-epsilon.txt"
            log_result = []


        result = [filename[:-5]]
        for engine_name in ["basic", "improved"]:
            solver.set_engine_strategy(engine_name)
            start = time.time()
            solver.run(epsilon)
            elapsed_time = time.time() - start
            print("Time needed for FPTAS: ", elapsed_time)
            print(f"FPTAS : Cmax = {solver.c_max}; number of states generated = {solver.generated_state_count}")
            result.append(solver.c_max)
            result.append(elapsed_time)
            result.append(solver.generated_state_count)
            if log:
                log_result.append(f"FPTAS ({engine_name}):")
                log_result.append("\n".join(solver.log_result))
                log_result.append("")
        if log:
            with open(log_filename, "w") as f:
                f.write("\n".join(log_result))
        else:
            with open(output_filename, output_mode) as f:
                print(";".join(map(str, result)), file=f)
    print(f"End of the run at {datetime.datetime.now()}")
