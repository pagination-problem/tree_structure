import sys
import json
from pathlib import Path
from datetime import datetime

from generate_instances import InstanceMaker, dump_instances
from instance import Instance

from statistics import mean, pstdev
from functools import reduce

# Aim of this code:
# Generate a lot of instances with the "stats" method (meaning we control the mean and
# standard ddviation) and we check if the instances have the the good mean and an
# acceptable standard deviation.

def verification():
    file = open("instances/sarah/verifs/00_recap_verifs.txt","w") 
    now = datetime.now()
    dt_string = now.strftime("%d/%m/%Y %H:%M:%S")
    file.write("Started at " + dt_string + "\n")
    file.close()

    filename = "instances/sarah/config_for_verif.json" if len(sys.argv) <= 1 else sys.argv[1]
    dump_instances(filename)

    input_dir = "instances/sarah/verifs"
    files = sorted(Path(input_dir).glob("*.json"))
    for (i, instance_path) in enumerate(files):
        instance = Instance(instance_path)

        costs = [[tile.weight] * (instance.tile_count + 1) for tile in instance.tiles]
        for (new, new_tile) in enumerate(instance.tiles):
            for (last, last_tile) in enumerate(instance.tiles[:new]):
                costs[new][last] = sum(symbol.weight for symbol in new_tile - last_tile)
        
        lower_triangle_costs = [row[: i + 1] for (i, row) in enumerate(costs)]
        flattened_costs = reduce(lambda x, y: x + y, lower_triangle_costs)
        cost_mean = mean(flattened_costs)
        cost_standard_deviation = pstdev(flattened_costs) 

        if 2.99 > cost_standard_deviation or cost_standard_deviation > 10.001:
            file = open("instances/sarah/verifs/00_recap_verifs.txt","a") 
            problem_into_str = str(instance_path) + ": 2.99 <= " + str(cost_standard_deviation) + " <= 10.001\n"
            file.write(problem_into_str)
            file.close() 

        if 49.9999 > cost_mean or cost_mean > 50.1:
            file = open("instances/sarah/verifs/00_recap_verifs.txt","a") 
            problem_into_str = str(instance_path) + ": 49.9999 <= " + str(cost_mean) + " <= 50.1\n"
            file.write(problem_into_str)
            file.close() 

    file = open("instances/sarah/verifs/00_recap_verifs.txt","a") 
    now = datetime.now()
    dt_string = now.strftime("%d/%m/%Y %H:%M:%S")
    file.write("Ended at " + dt_string + "\n")
    file.close()

if __name__ == "__main__":
    verification()