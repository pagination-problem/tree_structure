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
    #input_directory = os.path.join(root, "tests") #remove line as soon as this test file is in the good folder and use only the line bellow
    input_directory = os.path.join(root, "input")  #line to use when the test file will be in the good folder
    #input_directory = os.path.join(input_directory, "input") #delete this line when the file is in the good folder
    my_input = tools.load_json_instance_from(input_directory, input_filename)
    leaf_count = 8
    internal_node_offset = 7

    fptas.filling_the_matrix(my_input, internal_node_offset, leaf_count)

    reference_matrix = [['x' for i in range(9)] for i in range(9)]
    reference_matrix[2][0] = 8
    reference_matrix[2][2] = 0
    reference_matrix[3][0] = 8
    reference_matrix[3][2] = 3
    reference_matrix[3][3] = 0
    reference_matrix[4][0] = 11
    reference_matrix[4][2] = 6
    reference_matrix[4][3] = 4
    reference_matrix[4][4] = 0
    reference_matrix[7][0] = reference_matrix[7][2] = reference_matrix[7][3] = reference_matrix[7][4] = 12   
    reference_matrix[7][7] = 0
    reference_matrix[8][0] = reference_matrix[8][2] = reference_matrix[8][3] = reference_matrix[8][4] = 14
    reference_matrix[8][7] = 5
    reference_matrix[8][8] = 0

    assert reference_matrix == fptas.matrix
    print("test_for_the_matrix: everything is fine.\n")

if __name__ == '__main__':
    print("Begin.\n")
    test_for_the_matrix ()
    print("End.")

