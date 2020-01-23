import datetime
import json
import sys
import time
from pathlib import Path

from fptas import Fptas
from instance import Instance

# Read the configuration file

config_path = Path("configs") / ((sys.argv[1] if len(sys.argv) > 1 else "log") + ".json")
config = json.loads(config_path.read_text())
input_dir = config["input_dir"]
output_dir = config["output_dir"]
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

output_path = Path(f"{output_dir}/{output_prefix}_{tile_count}-tiles_{epsilon}-epsilon.txt")
already_processed = set()
if not log and output_path.is_file():
    for line in output_path.read_text().split("\n"):
        already_processed.add(line.partition(";")[0] + ".json")

for instance_path in Path(input_dir).glob("*.json"):

    if str(instance_path) in already_processed:
        print(f"{instance_path} already generated!")
        continue

    solver.set_instance(Instance(instance_path))
    print(f"input number : {instance_path} at {datetime.datetime.now()}")

    if log:
        log_path = Path(f"{output_dir}/{instance_path.stem}_{epsilon}-epsilon.txt")
        log_result = []

    result = [instance_path.stem]
    for engine_name in ["basic", "improved"]:
        solver.set_engine_strategy(engine_name)
        start = time.time()
        solver.run(epsilon)
        elapsed_time = time.time() - start
        print("Time needed for FPTAS: ", elapsed_time)
        print(f"FPTAS : Cmax = {solver.c_max}; {solver.state_count} states generated")
        result.append(solver.c_max)
        result.append(elapsed_time)
        result.append(solver.state_count)
        if log:
            log_result.append(f"FPTAS ({engine_name}):")
            log_result.append("\n".join(solver.log_result))
            log_result.append("")
    if log:
        log_path.write_text("\n".join(log_result))
    else:
        with output_path.open(output_mode) as f:
            print(";".join(map(str, result)), file=f)

print(f"End of the run at {datetime.datetime.now()}")
