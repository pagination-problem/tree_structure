import regex
import json


def json_formatter():
    def instance_to_json(data):
        text = json.dumps(data, indent=2)
        return sub(unwrap_int_list, text)

    unwrap_int_list = lambda m: f"[{', '.join(m.captures('n'))}]"
    sub = regex.compile(r"\[\s+((?P<n>\d+),?\s+)+\]").sub
    return instance_to_json


instance_to_json = json_formatter()
