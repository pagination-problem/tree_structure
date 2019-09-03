# -*- coding: utf-8 -*

import math

class Solution(list) :
    """
    For now, there are two attributs in this class but maybe I should create a list of machines even for the
    smallest studied case.
    It will make some computations easier (for example: the __repre__)

    I also store :
        - the name of the studied input in order to be able to link the solution found by the
    heuristic with the input.
        - the beta used to compute this solution

    So the attributes of this class are :
        - name : str
        - beta : float
        - machine1 : Page
        - machine2 : Page
        - Cmax : int
        - opt_value : the optimal value. If unknown, will be None
    """
    def __init__(self, name, beta, machine1, machine2, opt_value = None):
        self.machine1 = machine1
        self.machine2 = machine2
        self.name = name
        self.beta = beta
        self.opt_value = opt_value

    def __repr__(self):

        """
        Print a solution that way :
        For input : 'self.name'
        Beta : 'self.beta'
        Machine 1 (C1) : tile | tile | tile | ... | END
        Machine 2 (C2) : tile | tile | ... | END
        Cmax = max(C1, C2)
        """

        listTemp = []
        listTemp.append("For input : " + self.name)
        listTemp.append("Beta : " + str(self.beta))
        listTemp.append(f"Machine 2 (C2 = {self.machine2.usedCapacity}) : " + " | ".join( map(str, self.machine2)) + " | END")
        listTemp.append(f"Cmax = {max(self.machine1.usedCapacity, self.machine2.usedCapacity)}")

        return "\n".join(listTemp)

        # str1 = "Machine 1 : "
        # for tile in self.machine1:
        #     str1 += str(tile) + " | "
        # str1 += " END \nMachine 2 : "

        # for tile in self.machine2:
        #     str1 += str(tile) + " | "
        # str1 += " END "

        # return str1

    def __str__(self):
        """
        Print a solution that way :
        For input : 'self.name'
        Beta : 'self.beta'
        Machine 1 (C1) : tile | tile | tile | ... | END
        Machine 2 (C2) : tile | tile | ... | END
        Cmax = max(C1, C2)
        """

        listTemp = []
        listTemp.append("For input : " + self.name)
        listTemp.append("Beta : " + str(self.beta))
        listTemp.append(f"Machine 1 (C1 = {self.machine1.symbol_count()}) : " + " | ".join( map(str, self.machine1)) + " | END")
        listTemp.append(f"Machine 2 (C2 = {self.machine2.symbol_count()}) : " + " | ".join( map(str, self.machine2)) + " | END")
        listTemp.append(f"Cmax = {max(self.machine1.symbol_count(), self.machine2.symbol_count())}")
        listTemp.append(f"OPT = {self.opt_value}")

        return "\n".join(listTemp)

    def writing_in_file(self, dir_path_all, path_recap):
        """
        For the instances of A.Grange
        The format of 'name' given in input will be for example : C015_A020_T020_P00-3
        which means that this input is the third one described in json file C015_A020_T020_P00.

        For the instances
        """
        #before, separator, after = self.name.partition("-")
        before = self.name
        filename =  dir_path_all + "\\" + before + ".txt"
        sol_in_str = str(self)

        fichier = open(filename, "a")
        fichier.write("\n------------------------------------------------------------------------\n")
        fichier.write(sol_in_str) 
        fichier.close()

        filename = path_recap + "\\" + before + "_recap.txt"
        before, separator, after = self.name.partition(".") #Now 'before' will contain C015_A020_T020_P00-3 (and so with the number 3 at the end)

        fichier = open(filename, "a")
        C1 = self.machine1.symbol_count()
        C2 = self.machine2.symbol_count()
        Cmax = max(C1, C2)
        strTemp = "\n" + before + ";" + str(self.beta) + ";" + str(C1)
        strTemp += ";" + str(C2) + ";" + str(Cmax) + ";" + str(self.opt_value)
        if self.beta >= 0.9:
            strTemp += "\n------------------------------------------------------------------------"
        fichier.write(strTemp)
        fichier.close()


        