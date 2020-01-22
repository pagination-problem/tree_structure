import json
from collections import defaultdict
from pathlib import Path

from regex import match, sub


def unwrap_int_list(m):
    return f"[{', '.join(m.captures('n'))}]"


def normalize(path):
    d = defaultdict(list, json.loads(path.read_text()))

    d["tiles"] = [eval(s.replace("N", "")) for s in d.pop("tiles")]

    for s in d.pop("symbols"):
        m = match(r"\[N(\d+) - (\d+)\]", s)
        d["symbol_names"].append(int(m.group(1)))
        d["symbol_sizes"].append(int(m.group(2)))

    text = json.dumps(d, indent=2)
    text = sub(r"\[\s+((?P<n>\d+),?\s+)+\]", unwrap_int_list, text)
    
    return text


if __name__ == "__main__":
    normalize(Path("tests/input/H3-nbT5-001.json"))
