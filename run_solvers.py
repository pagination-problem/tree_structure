import json
import math
import sys
from datetime import datetime
from functools import partial, reduce
from pathlib import Path
from statistics import mean, pstdev
from time import time

import colorama
from colorama import Fore

from goodies import data_to_json
from instance import Instance

colorama.init()

SOLVERS = {
    "FPTAS": __import__("solver_fptas").Solver,
    "naive_cut": __import__("solver_naive_cut").Solver,
}

MAX_LOG_SIZE = 1000

# Configuration options
#
# input_dir: [mandatory]
# output_dir: [mandatory]
# start: index of the first file to process [default: 0]
# stop: index of the last file to process, excluded [default: (last file)]
# solver: "FPTAS" or "naive_cut"
# parameters: parameters of the specific solver
# log: boolean
# skip: boolean
# if_exists: what to do when there already exists a solution file
#   - "nothing": just display this solution, without running the solver
#   - "dry": run the solver, display the results and compare them with the previous ones
#   - "update" (or anything else): idem, and update the file
# if_not_exists: what to do when no solution file exists yet
#   - "nothing": skip this instance
#   - "dry": run the solver and display the results
#   - "write" (or anything else): idem, and write the results


class Table:
    def __init__(self, runner):
        self.columns = []
        self.runner = runner

    def add_column(self, label, attribute=None, width=None, align="right"):
        attribute = attribute or label
        width = width or len(label)
        align = {
            "left": lambda s: s.ljust(width),
            "right": lambda s: s.rjust(width),
            "center": lambda s: s.center(width),
        }[align]
        self.columns.append((label, attribute, width, align))

    def print_header(self):
        labels = " | ".join(align(label) for (label, _, _, align) in self.columns)
        rule = "-+-".join("-" * width for (_, _, width, _) in self.columns)
        result = f" {labels} \n-{rule}-"
        print(result)

    def print_half_row(self, middle_label=None):
        result = []
        for (label, attribute, _, align) in self.columns:
            s = str(getattr(self.runner, attribute))
            if s.startswith("<R>"):
                (prefix, s, suffix) = (Fore.RED, s[3:], Fore.BLACK)
            elif s.startswith("<G>"):
                (prefix, s, suffix) = (Fore.GREEN, s[3:], Fore.BLACK)
            else:
                (prefix, suffix) = ("", "")
            result.append(f"{prefix}{align(s)}{suffix}")
            if label == middle_label:
                yield print(f" {' | '.join(result)} |", end="", flush=True)
                result = []
        yield print(f" {' | '.join(result)} ")

    def print_row(self):
        next(self.print_half_row())


class Runner:
    def __init__(self, filename):
        self.configs = json.loads(Path(filename).read_text())

    def __call__(self):
        for config in self.configs:
            if config.get("skip"):
                continue
            self.solver_parameters = config.get("parameters", {})
            self.solver = SOLVERS[config["solver"]](self.solver_parameters)
            self.solver.set_log_strategy(config["log"])
            self.input_dir = Path(config["input_dir"])
            self.output_dir = Path(config["output_dir"])
            self.output_dir.mkdir(parents=True, exist_ok=True)
            self.existing_strategy = config.get("if_exists", "nothing")
            self.non_existing_strategy = config.get("if_not_exists", "nothing")
            self.start = config.get("start", 0)
            self.stop = config.get("stop")
            self.total_elapsed_time = 0
            self.solved_instance_count = 0
            self.run_one_config()
            self.cost_mean = 0
            self.cost_standard_deviation = 0

    def solve_one(self, instance):
        self.solver.set_instance(instance)
        starting_time = time()
        c_max = self.solver.run()
        # lower_triangle_costs = [row[: i + 1] for (i, row) in enumerate(self.solver.costs)]
        # flattened_costs = reduce(lambda x, y: x + y, lower_triangle_costs)
        # cost_mean = mean(flattened_costs)
        # cost_standard_deviation = pstdev(flattened_costs)
        elapsed_time = time() - starting_time + 10e-20
        self.total_elapsed_time += elapsed_time
        self.solved_instance_count += 1
        results = {
            "duration_magnitude": int(math.log10(elapsed_time)),
            "c_max": c_max,
            "solution": self.solver.may_retrieve_solution(),
            "step_count": self.solver.step_count,
            "elapsed_time": elapsed_time,
            "log": "",
        }
        if self.solver.log_result:
            results["log"] = (
                self.solver.log_result
                if results["step_count"] < MAX_LOG_SIZE
                else f"not dumped (too long)."
            )
        return results

    @staticmethod
    def ratio(old, new):
        if old == new:
            return ""
        try:
            s = f"{100 * new / old - 100:+.1f} %"
        except TypeError:
            return "N/A"
        else:
            color = "<R>" if s.startswith("+") else "<G>"
            return f"{color}{s}"

    def run_one_config(self):
        print(f"Input:  {self.input_dir}")
        print(f"Output: {self.output_dir}")
        print()

        table = Table(self)
        table.add_column("#", attribute="i", width=3)
        table.add_column("time", attribute="now", width=8)
        table.add_column("name", attribute="instance_name", width=27, align="left")
        table.add_column("cost mean", attribute="cost_mean")
        table.add_column("cost SD", attribute="cost_standard_deviation")
        table.add_column("step count", attribute="step_count", width=10)
        if self.existing_strategy != "nothing":
            table.add_column("ratio", attribute="step_count_delta", width=8)
        table.add_column("best", attribute="c_max", width=5)
        if self.existing_strategy != "nothing":
            table.add_column("ratio", attribute="c_max_delta", width=8)
        table.add_column("duration", align="left", width=21)
        table.print_header()

        files = sorted(self.input_dir.glob("*.json"))
        for (self.i, instance_path) in enumerate(files[self.start : self.stop], self.start):

            instance = Instance(instance_path)
            self.now = datetime.now().isoformat(timespec="seconds").partition("T")[2]
            self.instance_name = instance.name.replace(".json", "")
            self.step_count = "N/A"
            self.step_count_delta = "N/A"
            self.c_max = "N/A"
            self.c_max_delta = "N/A"
            self.duration = "N/A"
            self.cost_mean = "N/A"
            self.cost_standard_deviation = "N/A"

            previous_results = {}
            output_path = self.output_dir / instance.name
            if output_path.exists():
                previous_results.update(json.loads(output_path.read_text()))
                if self.existing_strategy == "nothing":
                    self.step_count = previous_results["step_count"]
                    self.c_max = previous_results["c_max"]
                    magnitude = previous_results["duration_magnitude"]
                    self.duration = f"previously in ~1e{magnitude} s."
                    self.cost_mean = previous_results["cost_mean"]
                    self.cost_standard_deviation = previous_results["cost_standard_deviation"]
                    table.print_row()
                    continue
            elif self.non_existing_strategy == "nothing":
                table.print_row()
                continue

            print_half_row = table.print_half_row("name")
            next(print_half_row)
            results = self.solve_one(instance)
            self.step_count = results["step_count"]
            self.c_max = results["c_max"]
            self.duration = f"solved in {results['elapsed_time']:.2e} s."
            self.cost_mean = "%.2f" % instance.cost_mean
            self.cost_standard_deviation = "%.2f" % instance.cost_standard_deviation

            if previous_results:
                self.step_count_delta = self.ratio(previous_results["step_count"], self.step_count)
                self.c_max_delta = self.ratio(previous_results["c_max"], self.c_max)

            next(print_half_row)

            if previous_results and self.existing_strategy == "dry":
                continue
            if not previous_results and self.non_existing_strategy == "dry":
                continue

            report = {
                "solver_parameters": self.solver_parameters,
                "duration_magnitude": results["duration_magnitude"],
                "c_max": results["c_max"],
                "solution": results["solution"],
                "step_count": results["step_count"],
                "cost_mean": instance.cost_mean,
                "cost_standard_deviation": instance.cost_standard_deviation,
                "log": results["log"],
            }
            output_path.write_text(data_to_json(report))

        print()
        if self.solved_instance_count:
            print(f"{self.solved_instance_count} instances solved", end=" ")
            print(f"in {round(self.total_elapsed_time, 2)} seconds.")
        else:
            print(f"All {self.i + 1} instances already solved.")
        print()


if __name__ == "__main__":
    filename = "solutions/sarah/run_for_stats.json" if len(sys.argv) <= 1 else sys.argv[1]
    # alternatively:   "solutions/snapshots.json"
    run = Runner(filename)
    run()
