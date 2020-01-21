# -*- coding: utf-8 -*
import os
from type_problem_input import ProblemInput
from type_symbol import Symbol
from type_tile import Tile

# To test :
# __init__(self, tiles, name, opt_value = None, opt_tiles_m1 = None, opt_tiles_m2 = None)
# __contains__(self, tile)
# __repr__(self)
# __str__(self)
# __len__(self)
# toList(self)
# add(self,tile)
# remove(self,tileOrIndex)
# isEmpty(self)
# getTiles(self)
# full_instance_to_str(self)
# write_instance_in_file(self, directory_path)

def test_of_the_creation_and_of_the_characterics():
   
    s1 = Symbol(1, 4)
    s2 = Symbol(2, 2)
    s3 = Symbol(3, 7)
    s4 = Symbol(4, 1)

    t1 = Tile({s1, s2})
    t2 = Tile({s2, s4})
    t3 = Tile({s3, s2, s1})

    my_input = ProblemInput({t1, t2, t3}, "input_test")
    print(my_input)
    print(my_input.full_instance_to_str())
    root = os.path.dirname(__file__)
    abs_path = os.path.join(root, "data_for_tests")
    my_input.write_instance_in_text_file(abs_path)
    print("test_of_the_creation_and_of_the_characterics : everything is fine.\n")

def test_of_the_creation_and_of_the_characterics_with_opt():
    
    s1 = Symbol(1, 4)
    s2 = Symbol(2, 5)
    s3 = Symbol(3, 2)
    s4 = Symbol(4, 3)
    s5 = Symbol(5, 4)
    s6 = Symbol(6, 4)

    t1 = Tile({s1, s2})
    t2 = Tile({s2, s3})
    t3 = Tile({s4, s5})
    t4 = Tile({s5, s6})

    C1 = t1.size() + t2.size() - s2.size
    C2 = t3.size() + t4.size() - s5.size
    Cmax = max(C1, C2)

    my_input = ProblemInput({t1, t2, t3, t4}, "input_test_with_opt", -1, -1, Cmax, {t1, t2}, {t3, t4})
    print(my_input)
    print(my_input.full_instance_to_str())
    my_input.write_instance_in_text_file("C:\\Users\\sarah\\Documents\\These\\2,tree-merging,Cmax\\FPTAS_for_tree_Pagination\\Programmation\\Inputs\\test\\")
    print("test_of_the_creation_and_of_the_characterics : everything is fine.\n")

def test_of_json_writing():
    s1 = Symbol(1, 4)
    s2 = Symbol(2, 5)
    s3 = Symbol(3, 2)
    s4 = Symbol(4, 3)
    s5 = Symbol(5, 4)
    s6 = Symbol(6, 4)

    t1 = Tile({s1, s2})
    t2 = Tile({s2, s3})
    t3 = Tile({s4, s5})
    t4 = Tile({s5, s6})

    C1 = t1.size() + t2.size() - s2.size
    C2 = t3.size() + t4.size() - s5.size
    Cmax = max(C1, C2)

    my_input = ProblemInput({t1, t2, t3, t4}, "IMPORTANT", -1, -1, Cmax, {t1, t2}, {t3, t4})
    my_input.write_instance_in_json_file("C:\\Users\\sarah\\Documents\\These\\2,tree-merging,Cmax\\FPTAS_for_tree_Pagination\\Programmation\\Inputs\\test\\")
    print("test_of_json_writing : everything is fine.\n")

def truc():
     
    print("truc : everything is fine.\n")

if __name__ == '__main__':
    print("Begin.\n")
    test_of_the_creation_and_of_the_characterics()
    test_of_the_creation_and_of_the_characterics_with_opt()
    test_of_json_writing()
    print("End.")