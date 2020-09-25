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

import xlsxwriter
import glob
import os.path
import traceback
import winsound
import gc

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
            self.output_path = config["output_dir"]
            self.start = config.get("start", 0)
            self.stop = config.get("stop")
            self.total_elapsed_time = 0
            self.solved_instance_count = 0
            if "experiments" in config["output_dir"]:
                self.solver_name = config["solver_name"]
                self.output_filename = config["output_filename"]
                if "FPTAS" in self.solver_name:
                    self.epsilon = config["parameters"]["hash_epsilon"]
                self.run_one_config_csv()
            else:
                self.run_one_config()
            self.cost_mean = 0
            self.cost_standard_deviation = 0

    def solve_one(self, instance):
        self.solver.set_instance(instance)
        starting_time = time()
        (c_max, min_state) = self.solver.run()
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
            "min_state": min_state,
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

    def copy_with_hashed_symbols(self, instance, epsilon): 
        data = instance.get_data() 
        data["symbol_weight_bound"] = math.ceil(instance.symbol_weight_bound * epsilon) 
        data["symbol_weights"] = [math.ceil(s.weight * epsilon) for s in sorted(instance.symbols)] 
        return Instance(data) 

    def run_one_config_excel(self):
        print(f"Input:  {self.input_dir}")
        print(f"Output: {self.output_dir}")
        print()

        files = sorted(self.input_dir.glob("*.json"))
        if "FPTAS" in self.solver_name:
            workbook = xlsxwriter.Workbook(self.output_path + self.output_filename + "__eps=" + str(self.epsilon) + '.xlsx')
        else:
            workbook = xlsxwriter.Workbook(self.output_path + self.output_filename + '.xlsx')
        worksheet = workbook.add_worksheet()
        
        # Create two formats to use in the merged range.
        merge_format = workbook.add_format(
            {
            'bold': 1,
            'border': 1,
            'align': 'center',
            'valign': 'vcenter',
            'fg_color': 'white'
            }
        )

        worksheet.merge_range(0,0,1,2,'instance', merge_format) # l,c,l,c,"text_inside_merged_cells", the_format
        worksheet.merge_range(0,3,0,5, self.solver_name, merge_format)
        if "FPTAS" in self.solver_name:
            worksheet.merge_range(1,3,1,5, "eps="+str(self.epsilon), merge_format)
        
        worksheet.write(2, 0, "name")
        worksheet.write(2, 1, "cost mean")
        worksheet.write(2, 2, "cost SD")
        worksheet.write(2, 3, "time")
        worksheet.write(2, 4, "step count")
        worksheet.write(2, 5, "Cmax")

        for (self.i, instance_path) in enumerate(files[self.start : self.stop], self.start):
            instance = Instance(instance_path)
            print(f"no. {self.i}: {instance.name}")
            
            if self.solver_name == "FPTAS 2":
                instance = self.copy_with_hashed_symbols(instance, self.epsilon)
            
            results = self.solve_one(instance)

            worksheet.write(self.i+3, 0, instance.name)
            worksheet.write(self.i+3, 1, instance.cost_mean)
            worksheet.write(self.i+3, 2, instance.cost_standard_deviation)
            worksheet.write(self.i+3, 3, round(results['elapsed_time'], 2))
            worksheet.write(self.i+3, 4, results["step_count"])
            worksheet.write(self.i+3, 5, results["c_max"])
            
        workbook.close()

    def run_one_config_csv(self):
        print(f"Input:  {self.input_dir}")
        print(f"Output: {self.output_dir}")
        print(f"{self.solver_name}")
        print()

        files = sorted(self.input_dir.glob("*.json"))

        if "FPTAS" in self.solver_name:
            filename = self.output_path + self.output_filename + "__eps=" + str(self.epsilon) + '.txt'
        else:
            filename = self.output_path + self.output_filename + '.txt'
        
        my_file = Path(filename)
        if my_file.is_file():
            f = open(filename, "a")
        else:
            f = open(filename, "w")
            f.write("instance;;;;")
            f.write(self.solver_name+";;;\n")
            if "FPTAS" in self.solver_name:
                f.write(";;;eps="+str(self.epsilon)+";\n")
            else:
                f.write(" ; ;\n")
            f.write("name;")
            f.write("tile count;")
            f.write("cost mean;")
            f.write("cost SD;")
            f.write("time;")
            f.write("step count;")
            f.write("Cmax;\n")

        f.close()

        if "FPTAS" in self.solver_name:
            print(f"epsilon = {self.epsilon}\n")

        for (self.i, instance_path) in enumerate(files[self.start : self.stop], self.start):
            instance = Instance(instance_path)
            print(f"no. {self.i}: {instance.name} begun at {datetime.now()}")
            
            if self.solver_name == "FPTAS 2":
                data = instance.get_data()
                instance_save = Instance(data)
                instance = instance.copy_with_hashed_symbols(self.epsilon)

            f = open(filename, "a")
            f.write(instance.name + ";")
            f.write(str(instance.tile_count) + ";")
            f.write(str(instance.cost_mean) + ";")
            f.write(str(instance.cost_standard_deviation) + ";")
            f.close()
            try:
                results = self.solve_one(instance)
            except Exception:
                f = open(filename, "a")
                f.write("MemoryError;\n")
                f.close()
                gc.collect()
                winsound.Beep(440, 350)
                winsound.Beep(440, 350)
                # traceback.print_exc()
                # print("Error message: ", e)
            else:
                if self.solver_name == "FPTAS 2":
                    # Computation of the real Cmax of the solution
                    tiles_on_P1 = results["min_state"][4]
                    last_on_P1 = instance_save.tile_count
                    last_on_P2 = instance_save.tile_count
                    C1 = 0
                    C2 = 0
                    for i in range(instance_save.tile_count) :
                        if i in tiles_on_P1:
                            C1 = C1 + instance_save.costs[i][last_on_P1]
                            last_on_P1 = i
                        else:
                            C2 = C2 + instance_save.costs[i][last_on_P2]
                            last_on_P2 = i
                    results["c_max"] = max(C1, C2)
                
                f = open(filename, "a")
                f.write(str(round(results['elapsed_time'], 2)) + ";")
                f.write(str(results["step_count"]) + ";")
                f.write(str(results["c_max"]) + ";\n")
                f.close()
                gc.collect()
                winsound.Beep(440, 350)

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
    # filename = "solutions/snapshots.json" if len(sys.argv) <= 1 else sys.argv[1]
    # filename = "experiments/results/h=6__i1__low_mean.json" if len(sys.argv) <= 1 else sys.argv[1]
    # alternatively:   "solutions/snapshots.json"
    # alternatively:   "solutions/sarah/run_for_stats.json"
    # run = Runner(filename)
    # run()

    files = sorted(glob.glob("experiments/results/configs/*.json"))
    for filename in files:
        run = Runner(filename)
        run()

    winsound.Beep(440, 350)
    winsound.Beep(440, 350)
    winsound.Beep(440, 350)
    