# -*- coding: utf-8 -*


from type_symbol import Symbol
from type_tile import Tile
from type_page import Page

# Functions to test:
# __init__(self):
# __repr__(self):
# add_tile(self, tile):
# __contains__(self, symbol):
# __str__(self):
# def __iter__(self):
# def tile_count(self):
# def symbol_count(self):

def test_characteristics_of_a_page():
    p = Page()

    s1 = Symbol(1, 4)
    s2 = Symbol(2, 2)
    s3 = Symbol(3, 7)

    t1 = Tile({s1, s2})

    p.add_tile(t1)
    print("The page : ", p)

    assert s1 in p, "It says that p does not contain s1 : problem"
    assert s3 not in p, "It says that p contains s3 : problem"

    print("characteristics_of_a_page : everything is fine.\n")  

def test_on_converting_a_page_to_a_str():
    s1 = Symbol(1, 4)
    s2 = Symbol(2, 2)
    s3 = Symbol(3, 7)
    s4 = Symbol(4, 1)

    t1 = Tile({s1, s2})
    t2 = Tile({s2, s4})
    t3 = Tile({s3, s2, s1})

    p = Page()

    p.add_tile(t1)
    p.add_tile(t2)
    p.add_tile(t3)

    print("The page : ", p)
    
    print("more_detailled_test_on_printing_a_page : everything is fine.\n")

def test_on_the_functions_for_the_counts():
    p = Page()

    s1 = Symbol(1, 4)
    s2 = Symbol(2, 2)
    s3 = Symbol(3, 7)
    s4 = Symbol(4, 1)

    t1 = Tile({s1, s2})
    t2 = Tile({s2, s4})
    t3 = Tile({s3, s2, s1})

    p.add_tile(t1)
    p.add_tile(t2)
    p.add_tile(t3)

    nb_symbols = p.symbol_count()
    nb_tiles = p.tile_count()

    reference_tile_set = {"[N1, N2]", "[N2, N4]", "[N1, N2, N3]"}
    set_of_tiles = set()
    print("The tiles on p :")
    for t in p.tiles:
        set_of_tiles.add(str(t))

    assert set_of_tiles == reference_tile_set
    assert nb_symbols == 4, "It says that the number of symbols on the page is not equal to 4 : problem"
    assert nb_tiles == 3, "It says that the number of tiles on the page is not equal to 3 : problem"

    print("tests_on_the_functions_for_the_counts : everything is fine.\n")

def test_on_the_containing_function():
    p = Page()

    s1 = Symbol(1, 4)
    s2 = Symbol(2, 2)
    s3 = Symbol(3, 7)

    t1 = Tile({s1, s2})
    t2 = Tile({s2, s3})

    p.add_tile(t1)

    assert t1 in p, "It says that t1 is not in p : problem"
    assert s1 in p, "It says that s1 is not in p : problem"
    assert t2 not in p, "It says that t2 is in p : problem"
    assert s3 not in p, "It says that s3 is in p : problem"
    print("test_on_the_containing_function : everything is fine.\n")

if __name__ == '__main__':
    print("Begin.\n")
    # test_characteristics_of_a_page()
    # test_on_converting_a_page_to_a_str()
    # test_on_the_functions_for_the_counts()
    # test_on_the_containing_function()
    print("End.")
