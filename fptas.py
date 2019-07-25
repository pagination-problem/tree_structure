# -*- coding: utf-8 -*

from type_symbol import Symbol
from type_tile import Tile
from type_page import Page
from type_problem_input import ProblemInput

# matrix[i][j] = the quantity to add to a machine if we want to assign to it
# the tile i and if the last tile assigned to it was j
# i and j are in the LEAF-ONLY INDEX
# which means that if j = 4 and i = 7 : we are considering adding the tile [N1, N3, N7, N14]
# with the tile [N1, N2, N5, N11] already assigned
# The tree :
#          N1
#        /    \
#       /      \
#      /        \
#     /          \
#    N2          N3
#   /  \       /    \
#  N4   N5    N6    N7
# / \  / \   /  \  /  \
# 1 2  3  4  5  6  7   8
# 1 <-> N8  ; 2  <-> N9  ; 3  <-> N10 ; 4  <-> N11 ;
# 5 <-> N12 ; 6  <-> N13 ; 7  <-> N14 ; 8  <-> N15
matrix = [[]]

def filling_the_matrix(the_input, nb_internal_nodes, nb_leaves):
    # As its name says, this function performs the computation of the matrix needed in the FPTAS.
    # It will create a square matrix with nb_leaves + 1 rows and nb_leaves + 1 columns.
    # The first row will be left empty and shall never be looked at.
    # the first colomn should be interpreted as follows: if nothing has been scheduled on the machine, how
    # many symbols should I add to the machine to be able to assign the tile number i (with i a row number). Of
    # course this number equals the size of the tile.
    # Then, the rest of the matrix is used as usual : M[i][j] = number of symbols I must add to a machine if the
    # last scheduled tile is j and if I want to add the tile i.
    #
    # There will be empty cells for two reasons : 
    #       - There is a condition inherent to the method which is i >= j. So this means half of the matrix is empty
    #       - There are as many rows (and columns) as there are leaves in the starting tree but maybe not all of leaves
    #           are kept in the input. The cells for these not-used leaves are left empty (with an 'x' inside in fact)
    #
    # Of course, all the indexes used in the matrix are in LEAF-ONLY index. See the top of
    # this document to have explanation of whats does this mean.
    
    global matrix
    matrix = [['x' for x in range(nb_leaves+1)] for y in range(nb_leaves+1)]

    tile_set = sorted(the_input.tileSet, key=lambda tile: tile.index_of_leaf)
    for t in tile_set:
        leaf_index_t = t.get_leaf_symbol().index
        i = leaf_index_t - nb_internal_nodes
        matrix[i][0]= t.size()

    for t1 in tile_set:
        for t2 in tile_set:
            set_of_symbols_not_assigned_yet = (t1.symbols).difference(t2.symbols)
            leaf_index_t1 = t1.get_leaf_symbol().index
            leaf_index_t2 = t2.get_leaf_symbol().index

            i = leaf_index_t1 - nb_internal_nodes
            j = leaf_index_t2 - nb_internal_nodes

            if i >= j:
                size_to_add = 0
                for s in set_of_symbols_not_assigned_yet:
                    size_to_add += s.size
                matrix[i][j] = size_to_add

def selecting_a_representative_for_an_interval(begin, end, the_set):
    """
    In this function, we will go through the_set and for each value 'a' between 'begin' and 'end'
    (begin <= a <= end), we will save the state with the smallest b
    """
    save_tuple = None
    the_min = float('inf')
    for t in the_set:
        if begin <= t[0] <= end:
            if t[1] < the_min:
                save_tuple = t
                the_min = t[1]

    return save_tuple

def FPTAS(the_input, epsilon):
    number_of_generated_states = 0
    global matrix
    Cmax = float('inf')
    chi_i_minus_one = set()
    chi_i_minus_one.add((0,0,0,0))

    nb_leaves = 2**the_input.height
    nb_internal_nodes = nb_leaves - 1

    P = the_input.get_sum_symbol_sizes()
    delta = (epsilon * P) /  (2 * len(the_input))
    
    filling_the_matrix(the_input, nb_internal_nodes, nb_leaves)

    tile_set = sorted(the_input.tileSet, key=lambda tile: tile.index_of_leaf)

    for t in tile_set:
        chi_i = set()
        leaf_index_t = t.get_leaf_symbol().index
        i = leaf_index_t - nb_internal_nodes #index of the tile we are about to schedule
        
        for my_tuple in chi_i_minus_one:
            a = my_tuple[0]
            b = my_tuple[1]
            j = my_tuple[2]
            k = my_tuple[3]

            # We add the tile t on M1
            m = matrix[i][j]
            my_tuple = (a + m, b, i, k)
            chi_i.add(my_tuple)

            # We add the tile t on M2
            m = matrix[i][k]
            my_tuple = (a, b + m, j, i)
            chi_i.add(my_tuple)

        # Taking into account the number of states which were generated during this iteration
        number_of_generated_states += len(chi_i)
        
        # Choosing the representative
        temp_set = sorted(chi_i, key=lambda my_tuple: my_tuple[0])
        d = 0
        chi_i_minus_one = set()
        while d <= P:
            end = d + delta
            the_representative = selecting_a_representative_for_an_interval(d, end, temp_set)
            if (the_representative != None):
                chi_i_minus_one.add(the_representative)
            d = d + delta

    for my_tuple in chi_i_minus_one:
        a = my_tuple[0]
        b = my_tuple[1]

        val = max(a,b)

        if val < Cmax:
            Cmax = val
    
    return (Cmax, number_of_generated_states)

    #C:\Users\sarah\Documents\These\2,tree-merging,Cmax\FPTAS_for_tree_Pagination\Programmation\Tests