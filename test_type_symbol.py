# -*- coding: utf-8 -*

from type_symbol import Symbol

def characteristics_of_a_symbol():
    s = Symbol(4, 2)

    print("Symbol name : ", s.name)
    print("Symbol size : ", s.size)
    print("characteristics_of_a_symbol : everything is fine.\n")   

def creation_of_two_different_symbols():
    symb1 = Symbol(1, 4)
    symb2 = Symbol(2, 2)

    assert symb1 != symb2, "It says that symb1 and symb2 are the same : problem"
    assert symb1.size == 4, "The size of symbol1 is supposed to be equal to 4 and it is not : problem"
    print("First symbol : ", symb1)
    print("creation_of_two_different_symbols : everything is fine.\n")       

def creation_of_two_identical_symbols():
    symb1 = Symbol(1, 4)
    symb2 = Symbol(1, 4)

    assert symb1 == symb2, "It says that symb1 and symb2 are different : problem"
    assert symb1.size == 4, "The size of symbol1 is supposed to be equal to 4 and it is not : problem"
    print("First symbol : ", symb1)
    print("creation_of_two_identical_symbols : everything is fine.\n")

def comparison_of_two_different_symbols():
    s1 = Symbol(2, 2)
    s2 = Symbol(100, 10)

    assert s1 < s2, "it says that s1 is greater than s2 : problem"
    assert s1 != s2, "it says that s1 is equal to s2 : problem"
    print("comparison_of_two_different_symbols : everything is fine.\n")

if __name__ == '__main__':
    print("Begin.\n")
    #characteristics_of_a_symbol()
    creation_of_two_different_symbols()
    creation_of_two_identical_symbols()
    comparison_of_two_different_symbols()
    print("End.")
