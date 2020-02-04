# -*- coding: utf-8 -*
import context
import os
import tools
import fptas

# To test:
# filling_the_matrix(the_input, internal_node_offset, leaf_count)
# select_representatives_on_grid(states, delta, upper_bound)
# run(the_input, epsilon):


def test_for_the_matrix ():
    input_filename = "H3-nbT5-001"
    root = os.path.dirname(__file__)
    input_directory = os.path.join(root, "input")
    my_input = tools.load_json_instance_from(input_directory, input_filename)
    leaf_count = 8
    internal_node_offset = 7

    fptas.filling_the_matrix(my_input, internal_node_offset, leaf_count)

    reference_matrix = [
        ['x', 'x', 'x', 'x', 'x', 'x', 'x', 'x', 'x'],
        ['x', 'x', 'x', 'x', 'x', 'x', 'x', 'x', 'x'], 
        [  8, 'x',   0, 'x', 'x', 'x', 'x', 'x', 'x'], 
        [  8, 'x',   3,   0, 'x', 'x', 'x', 'x', 'x'], 
        [ 11, 'x',   6,   4,   0, 'x', 'x', 'x', 'x'], 
        ['x', 'x', 'x', 'x', 'x', 'x', 'x', 'x', 'x'], 
        ['x', 'x', 'x', 'x', 'x', 'x', 'x', 'x', 'x'], 
        [ 12, 'x',  12,  12,  12, 'x', 'x',   0, 'x'], 
        [ 14, 'x',  14,  14,  14, 'x', 'x',   5,   0],
    ]

    assert reference_matrix == fptas.matrix
    print("test_for_the_matrix: everything is fine.\n")

def test_of_the_run():
    input_filename = "H3-nbT5-001"
    root = os.path.dirname(__file__)
    input_directory = os.path.join(root, "input")
    my_input = tools.load_json_instance_from(input_directory, input_filename)
    epsilon = 0.1

    fptas.set_log_strategy(False)
    (Cmax1, number_of_generated_states1) = fptas.run(my_input, epsilon)

    assert Cmax1 == 17
    assert number_of_generated_states1 == 42
    
    print("test_of_the_run: everything is fine.\n")

if __name__ == '__main__':
    print("Begin.\n")
    test_for_the_matrix ()
    test_of_the_run()
    print("End.")

