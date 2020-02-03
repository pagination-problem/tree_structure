# -*- coding: utf-8 -*
import os
from Pagination_tree_structure import tools
#import tools

# To test:
# filling_the_matrix(the_input, internal_node_offset, leaf_count)
# select_representatives_on_grid(states, delta, upper_bound)
# run(the_input, epsilon):


def test_for_the_matrix ():
    input_filename = "H3-nbT5-001"
    root = os.path.dirname(__file__)
    input_directory = os.path.join(root, "input")
    my_input = tools.load_json_instance_from(input_directory, input_filename)
    print("test_for_the_matrix: everything is fine.\n")

if __name__ == '__main__':
    print("Begin.\n")
    test_for_the_matrix ()
    print("End.")