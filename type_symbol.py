# -*- coding: utf-8 -*

class Symbol :
    # self.size. This class is useful when a symbol is not just a letter and so if the size of a
    # symbol can vary (from 0 to a certain maximum value) like in the FPTAS for 2 | merging, tree | Cmax.
    # The name of a symbol will be the letter 'N' + a number. This number is equal to the index of
    # the corresponding node will have in a Breadth-first search.
    def __init__(self, index, size):
        self.index = index
        self.name = f"N{index}"
        self.size = size
        self.hash = hash(tuple(str(self.index)))
    
    def __str__(self):
        return self.name
    
    # def __len__(self):
    #     return self.size

    def __repr__(self):
        return str(self)

    # def __hash__(self):
    #     return self.hash
    
    # def __eq__(self, other): #eq(a, b) is equivalent to a == b # maybe we should add the comparison of the sizes
    #     return self.index == other.index

    # def __lt__(self, other): # self < other
    #     return self.index < other.index

    # def __le__(self, other): #self <= other
    #     return self.index <= other.index

    # def __ne__(self, other): #self != other
    #     return self.index != other.index

    # def __gt__(self, other): # self > other
    #     return self.index > other.index

    # def __ge__(self, other):
    #     return self.index >= other.index