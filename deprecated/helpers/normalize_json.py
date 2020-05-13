import json
from collections import defaultdict
from pathlib import Path

from regex import match, sub


def unwrap_int_list(m):
    return f"[{', '.join(m.captures('n'))}]"


def normalize(deprecated_data):
    d = defaultdict(list, deprecated_data)

    for s in d.pop("symbols"):
        m = match(r"\[N(\d+) - (\d+)\]", s)
        d["symbol_indexes"].append(int(m.group(1)))
        d["symbol_sizes"].append(int(m.group(2)))
    
    d["tiles"] = [eval(s.replace("N", "")) for s in d.pop("tiles")]

    text = json.dumps(d, indent=2)
    text = sub(r"\[\s+((?P<n>\d+),?\s+)+\]", unwrap_int_list, text)
    text = text.replace("max_symbol_size", "symbol_size_bound")

    return text


def convert_all():
    for path in Path("inputs").rglob("*.json"):
        data = json.loads(path.read_text())
        if "tiles" in data and "symbols" in data:
            result = normalize(data)
            output_path = Path(str(path.parent).replace("inputs", "input")) / path.name
            output_path.write_text(result)
            print(output_path)


if __name__ == "__main__":
    path = Path("tests/input/H3-nbT5-001.json")
    deprecated_data = json.loads(path.read_text())
    print(normalize(deprecated_data))
    # convert_all()
