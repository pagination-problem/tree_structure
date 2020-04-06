from datetime import datetime
import json
import math
import sys
from time import time
from pathlib import Path

from instance import Instance
from goodies import data_to_json

SOLVERS = {
    "FPTAS": __import__("solver_fptas").Fptas,
    "naive_cut": __import__("solver_naive_cut").NaiveCut,
}

MAX_LOG_SIZE = 10


class Runner:
    def __init__(self, filename):
        if not filename.endswith(".json"):
            filename += ".json"
        path = Path("solutions") / filename
        config = json.loads(path.read_text())
        self.solver = SOLVERS[config["solver"]]()
        self.solver.set_engine_strategy(config["engine"])
        self.solver.set_log_strategy(config["log"])
        self.solver.set_parameters(**config["parameters"])
        self.input_dir = Path(config["input_dir"])
        self.output_dir = Path(config["output_dir"])
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.total_elapsed_time = 0
        self.solved_instance_count = 0

    def solve_one(self, instance):
        self.solver.set_instance(instance)
        starting_time = time()
        self.solver.run()
        elapsed_time = time() - starting_time
        print(f"{self.solver.c_max:4} | solved in {elapsed_time:.2e} s.")
        self.total_elapsed_time += elapsed_time
        self.solved_instance_count += 1
        solution = self.solver.retrieve_solution()
        report = {
            "duration_magnitude": int(math.log10(elapsed_time)),
            "c_max": self.solver.c_max,
        }
        if self.solver.log_result:
            report["solution"] = solution
            report["log"] = (
                self.solver.log_result
                if len(self.solver.log_result) < MAX_LOG_SIZE
                else f"not dumped (too long)."
            )
        return report

    def __call__(self):
        print(f"Input directory: {self.input_dir}")
        print(f"Output directory: {self.output_dir}")
        print()
        print("   # |     time | name                             | best | duration")
        print("-----+----------+----------------------------------+------+-----------------------")
        for (i, instance_path) in enumerate(sorted(self.input_dir.glob("*.json")), 1):
            now = datetime.now().isoformat(timespec="seconds").partition("T")[2]
            instance = Instance(instance_path)
            print(f"{i:4} | {now} | {instance.name} | ", end="", flush=True)
            output_path = self.output_dir / instance.name
            if output_path.exists():
                c_max = json.loads(output_path.read_text())["c_max"]
                print(f"{c_max:4} | already solved")
                continue
            report = self.solve_one(instance)
            text = data_to_json(report)
            output_path.write_text(text)
        print()
        if self.solved_instance_count:
            print(f"{self.solved_instance_count} instances solved", end=" ")
            print(f"in {round(self.total_elapsed_time, 2)} seconds.")
        else:
            print(f"All {i} instances already solved.")


if __name__ == "__main__":
    if len(sys.argv) > 1:
        filename = sys.argv[1]
        run = Runner(filename)
        run()
    else:
        filenames = [
            "1_config_basic_fptas.json",
            "1_config_naive_cut.json",
        ]
        for filename in filenames:
            run = Runner(filename)
            run()
            print()
