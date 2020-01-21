# -*- coding: utf-8 -*
import os
from type_symbol import Symbol
from type_tile import Tile
import tools

def creation_of_a_tile():
    size1 = 4
    size2 = 2
    size3 = 7
    sum_size = size1 + size2 + size3

    s1 = Symbol(1, 4)
    s2 = Symbol(2, 2)
    s3 = Symbol(3, 7)

    t1 = Tile({s2, s3, s1})

    print("Print of the tile (the symbols must be order by increasing number of index):", t1)
    print("The symbols in t1 : ")
    for s in t1.symbols:
        print(s)

    assert t1.size() == sum_size, "It says that the tile size is not equal to 6 : problem"

    print("creation_of_a_tile : everything is fine.\n")

# def creation_of_three_different_tiles():
#     size_s1 = 4
#     size_s2 = 2
#     sum_size_s1_s2 = size_s1 + size_s2

#     s1 = Symbol(1, 4)
#     s2 = Symbol(2, 2)
#     s3 = Symbol(3, 7)
#     s4 = Symbol(4, 1)

#     t1 = Tile({s1, s2})
#     t2 = Tile({s2, s4})
#     t3 = Tile({s3, s2, s1})

#     assert t1 != t2, "It says that the two tiles are identical : problem"
#     assert t1.size() == sum_size_s1_s2, "It says that the size of t1 != 6 : problem"
#     assert t1.is_included_in(t3), "It says that the symbols of t1 are not included in t3 : problem"
#     assert t1.is_included_in_at_least_one_tile_of_the_set({t2, t3}), "It says that t1 is not included in t3 : problem"
#     assert t1.is_included_in_at_least_one_tile_of_the_set({t2}) == False, "It says that t1 is included in t2 : problem"
#     assert t3.includes_at_least_a_tile_of_the_set({t1}), "It says that t3 does not include t1 : problem"
#     assert t3.includes_at_least_a_tile_of_the_set({t2}) == False, "It says that t3 includes t2 : problem"
    
#     print("creation_of_three_different_tiles : everything is fine.\n")       

def test_of_getting_the_leaf_out_of_a_tile():
    
    root = os.path.dirname(__file__)
    abs_path = os.path.join(root, "data_for_tests")
    my_input = tools.load_json_instance_from(abs_path, "H3-nbT5-001")
    
    leaves_reference_values = {9, 10, 11, 14, 15}
    set_of_leaves = set()
    for t in my_input.tileSet:
        set_of_leaves.add(t.leaf_index)

    assert leaves_reference_values == set_of_leaves
        

if __name__ == '__main__':
    print("Begin.\n")
    #creation_of_a_tile()
    #creation_of_three_different_tiles()
    test_of_getting_the_leaf_out_of_a_tile()
    print("End.")
