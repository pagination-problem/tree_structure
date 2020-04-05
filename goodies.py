import regex
import json


def json_wrapper():
    """Unwrap any list of integers in a JSON string produced by json.dumps()."""
    sub = regex.compile(r"\[\s+((?P<n>-?\d+),?\s+)+\]").sub
    unwrap_int_list = lambda m: f"[{', '.join(m.captures('n'))}]"
    return lambda data: sub(unwrap_int_list, json.dumps(data, indent=2)) + "\n"


data_to_json = json_wrapper()
