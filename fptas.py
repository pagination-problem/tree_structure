# -*- coding: utf-8 -*

from type_symbol import Symbol
from type_tile import Tile
from type_page import Page
from type_problem_input import ProblemInput

FLOAT_CORRECTION = 1e-6

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
matrix = []

def filling_the_matrix(the_input, internal_node_offset, leaf_count):
    # As its name says, this function performs the computation of the matrix needed in the FPTAS.
    # It will create a square matrix with leaf_count + 1 rows and leaf_count + 1 columns.
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
    
    matrix.extend([['x' for x in range(leaf_count+1)] for y in range(leaf_count+1)])

    tile_set = sorted(the_input.tileSet, key=lambda tile: tile.leaf_index)
    for t in tile_set:
        leaf_index_t = t.leaf_index
        i = leaf_index_t - internal_node_offset
        matrix[i][0]= len(t)

    for t1 in tile_set:
        for t2 in tile_set:
            set_of_symbols_not_assigned_yet = t1.symbols.difference(t2.symbols)
            i = t1.leaf_index - internal_node_offset
            j = t2.leaf_index - internal_node_offset
            if i >= j:
                matrix[i][j] = sum(symbol.size for symbol in set_of_symbols_not_assigned_yet)

def select_representatives_on_grid(states, delta, upper_bound):
    result = {}
    for state in states:
        coords = (int(state[0] / delta), int(state[1] / delta))
        if coords not in result or state < result[coords]:
            result[coords] = state
    return set(result.values())

def run(the_input, epsilon):

    generated_state_count = 0
    chi_seed = {(0, 0, 0, 0)}

    leaf_count = 2 ** the_input.height
    internal_node_offset = leaf_count - 1

    P = the_input.get_sum_symbol_sizes()
    delta = (epsilon * P) /  (2 * len(the_input))
    
    filling_the_matrix(the_input, internal_node_offset, leaf_count)

    tile_set = sorted(the_input.tileSet, key=lambda tile: tile.leaf_index)

    for t in tile_set:
        chi = set()
        i = t.leaf_index - internal_node_offset #index (in the leaf-only index) of the tile we are about to schedule
        
        for (a, b, j, k) in chi_seed:
            # We add tile t on M1
            m = matrix[i][j]
            chi.add((a + m, b, i, k))

            # We add tile t on M2
            m = matrix[i][k]
            chi.add((a, b + m, j, i))

        # Taking into account the number of states which were generated during this iteration
        generated_state_count += len(chi)

        # Choosing the representatives
        chi_seed = select_representatives_on_grid(chi, delta, P)

        run.may_log(i, chi_seed)

    # c_max = min(chi_seed, key=lambda state: max(state[0], state[1]))
    best_sol = min(chi_seed, key=lambda state: max(state[0], state[1]))
    c_max = max(best_sol[0], best_sol[1])
    return (c_max, generated_state_count)

log_result = []

def set_log_strategy(log):

    def log_states(i, chi):
        log_result.append(f"{i}: {sorted(chi)}")
    
    if log:
        run.may_log = log_states
    else:
        run.may_log = lambda *args : None
        
