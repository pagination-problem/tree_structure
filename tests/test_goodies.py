import json

import context
from goodies import data_to_json

raw_dump = """\
{
  "height": 4,
  "symbol_size_bound": 5,
  "symbol_count": 5,
  "symbol_sizes": [
    4,
    5,
    3,
    4,
    1
  ],
  "tiles": [
    [
      0,
      1,
      2,
      4
    ],
    [
      0,
      1,
      3
    ]
  ]
}"""

improved_dump = """\
{
  "height": 4,
  "symbol_size_bound": 5,
  "symbol_count": 5,
  "symbol_sizes": [4, 5, 3, 4, 1],
  "tiles": [
    [0, 1, 2, 4],
    [0, 1, 3]
  ]
}
"""


def test_data_to_json():
    data = {
        "height": 4,
        "symbol_size_bound": 5,
        "symbol_count": 5,
        "symbol_sizes": [4, 5, 3, 4, 1],
        "tiles": [[0, 1, 2, 4], [0, 1, 3]],
    }
    assert raw_dump == json.dumps(data, indent=2)
    assert improved_dump == data_to_json(data)
