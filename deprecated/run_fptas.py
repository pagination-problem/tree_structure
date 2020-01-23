import os
import tools
import fptas
import time
from improved_fptas import improved_FPTAS

dir_path_for_inputs = ""
dir_path_for_results = ""
dir_path_for_recap = ""

def files_in(directory_path):
    filesList = list()
    for name in os.listdir(directory_path):
        filesList.append(str(name))

    return filesList

def writing_in_file(name_of_file, path_to_file, str_to_write, opening_option):
    path = path_to_file + "\\" + name_of_file + ".txt"

    if opening_option == "a" :
        fichier = open(path, "a")
    else:
        fichier = open(path, "w")

    fichier.write(str_to_write) 
    fichier.close()

def average (my_list, number_of_elements):
    res = 0
    for i in range(0, number_of_elements):
        res += my_list[i]
    return res/number_of_elements

def computing_fptas_on_one_instance_for_all_epsilons(my_input, number_of_iterations):
    global dir_path_for_recap
    
    full_results_to_str = ""
    summary_to_str = ""
    for epsilon in range(1, 10):
        list_time_values = []
        list_sol_values = []
        list_nb_of_generated_state = []
        for i in range (0,number_of_iterations):
            start_time = time.time()
            (Cmax, number_of_generated_states) = fptas.FPTAS(my_input, epsilon/10)
            interval = time.time() - start_time
            list_sol_values.append(Cmax)
            list_nb_of_generated_state.append(number_of_generated_states)
            list_time_values.append(interval)
            full_results_to_str += str(i+1) + ";"
            full_results_to_str += str(epsilon/10) + ";"
            full_results_to_str += str(list_sol_values[i])
            full_results_to_str += ";" + str(list_time_values[i])
            full_results_to_str += ";" + str(number_of_generated_states)
            full_results_to_str += "\n"

        average_value = average(list_sol_values, number_of_iterations)
        average_time = average(list_time_values, number_of_iterations)
        average_state_number = average(list_nb_of_generated_state, number_of_iterations)
        summary_to_str += str(epsilon/10) + ";" + str(number_of_iterations) + ";" + str(average_value)  + ";" + str(average_time) + ";" + str(average_state_number) + ";\n"
        nb_of_tiles = len(my_input.tileSet)
        
        my_str = "\n" + str(my_input.name) + ";" +  str(average_value) + ";" + str(average_time) + ";" + str(average_state_number)
        writing_in_file(str(nb_of_tiles) + "-tiles_" + str(epsilon/10) + "_recap", dir_path_for_recap, my_str, "a")

    return (full_results_to_str, summary_to_str)

def computing_improved_fptas_on_one_instance_for_all_epsilons(my_input, number_of_iterations):
    global dir_path_for_recap
    
    full_results_to_str = ""
    summary_to_str = ""
    for epsilon in range(1, 10):
        list_time_values = []
        list_sol_values = []
        list_nb_of_generated_state = []
        for i in range (0,number_of_iterations):
            start_time = time.time()
            (Cmax, number_of_generated_states) = improved_FPTAS(my_input, epsilon/10)
            interval = time.time() - start_time
            list_sol_values.append(Cmax)
            list_time_values.append(interval)
            list_nb_of_generated_state.append(number_of_generated_states)
            full_results_to_str += str(i+1) + ";"
            full_results_to_str += str(epsilon/10) + ";"
            full_results_to_str += str(list_sol_values[i])
            full_results_to_str += ";" + str(list_time_values[i])
            full_results_to_str += ";" + str(number_of_generated_states)
            full_results_to_str += "\n"

        average_value = average(list_sol_values, number_of_iterations)
        average_time = average(list_time_values, number_of_iterations)
        average_state_number = average(list_nb_of_generated_state, number_of_iterations)
        summary_to_str += str(epsilon/10) + ";" + str(number_of_iterations) + ";" + str(average_value) + ";" + str(average_time) +  ";" + str(average_state_number) + ";\n"
        nb_of_tiles = len(my_input.tileSet)
        
        my_str = ";" +  str(average_value) + ";" + str(average_time) + ";" + str(average_state_number)
        writing_in_file(str(nb_of_tiles) + "-tiles_" + str(epsilon/10) + "_recap", dir_path_for_recap, my_str, "a")

    return (full_results_to_str, summary_to_str)

def computing_fptas_on_one_instance_for_some_epsilons(my_input, number_of_iterations, range_for_epsilon_values):
    global dir_path_for_recap

    full_results_to_str = ""
    summary_to_str = ""
    for epsilon in range_for_epsilon_values:
        list_time_values = []
        list_sol_values = []
        list_nb_of_generated_state = []
        for i in range (0,number_of_iterations):
            print("Computing the FPTAS with epsilon = ", epsilon, "and i =", i)
            start_time = time.time()
            (Cmax, number_of_generated_states) = fptas.FPTAS(my_input, epsilon)
            interval = time.time() - start_time
            list_sol_values.append(Cmax)
            list_nb_of_generated_state.append(number_of_generated_states)
            list_time_values.append(interval)
            full_results_to_str += str(i+1) + ";"
            full_results_to_str += str(epsilon) + ";"
            full_results_to_str += str(list_sol_values[i])
            full_results_to_str += ";" + str(list_time_values[i])
            full_results_to_str += ";" + str(number_of_generated_states)
            full_results_to_str += "\n"

        average_value = average(list_sol_values, number_of_iterations)
        average_time = average(list_time_values, number_of_iterations)
        average_state_number = average(list_nb_of_generated_state, number_of_iterations)
        summary_to_str += str(epsilon) + ";" + str(number_of_iterations) + ";" + str(average_value)  + ";" + str(average_time) + ";" + str(average_state_number) + ";\n"
        nb_of_tiles = len(my_input.tileSet)
        
        my_str = "\n" + str(my_input.name) + ";" +  str(average_value) + ";" + str(average_time) + ";" + str(average_state_number)
        writing_in_file(str(nb_of_tiles) + "-tiles_" + str(epsilon) + "_recap", dir_path_for_recap, my_str, "a")

    return (full_results_to_str, summary_to_str)

def computing_improved_fptas_on_one_instance_for_some_epsilons(my_input, number_of_iterations, range_for_epsilon_values):
    global dir_path_for_recap
    full_results_to_str = ""
    summary_to_str = ""
    for epsilon in range_for_epsilon_values:
        list_time_values = []
        list_sol_values = []
        list_nb_of_generated_state = []
        for i in range (0,number_of_iterations):
            print("Computing the iFPTAS with epsilon = ", epsilon, "and i =", i)
            start_time = time.time()
            (Cmax, number_of_generated_states) = improved_FPTAS(my_input, epsilon)
            interval = time.time() - start_time
            list_sol_values.append(Cmax)
            list_time_values.append(interval)
            list_nb_of_generated_state.append(number_of_generated_states)
            full_results_to_str += str(i+1) + ";"
            full_results_to_str += str(epsilon) + ";"
            full_results_to_str += str(list_sol_values[i])
            full_results_to_str += ";" + str(list_time_values[i])
            full_results_to_str += ";" + str(number_of_generated_states)
            full_results_to_str += "\n"

        average_value = average(list_sol_values, number_of_iterations)
        average_time = average(list_time_values, number_of_iterations)
        average_state_number = average(list_nb_of_generated_state, number_of_iterations)
        summary_to_str += str(epsilon) + ";" + str(number_of_iterations) + ";" + str(average_value) + ";" + str(average_time) +  ";" + str(average_state_number) + ";\n"
        nb_of_tiles = len(my_input.tileSet)
        
        my_str = ";" +  str(average_value) + ";" + str(average_time) + ";" + str(average_state_number)
        writing_in_file(str(nb_of_tiles) + "-tiles_" + str(epsilon) + "_recap", dir_path_for_recap, my_str, "a")

    return (full_results_to_str, summary_to_str)

def pre_filling_the_file(name_of_file, path_to_file, str_to_write, opening_option):
    path = path_to_file + "\\" + name_of_file + ".txt"

    if opening_option == "a" :
        fichier = open(path, "a")
    else:
        fichier = open(path, "w")

    fichier.write(str_to_write) 
    fichier.close()

if __name__ == '__main__':
    # global dir_path_for_inputs
    # global dir_path_for_results
    # global dir_path_for_recap
    # This declaration is not necessary as this part of the code is NOT in a new (and so different) block from the
    # block where the declarations actually occur.

    number_of_tiles = 600
    number_of_iterations = 3
    range_for_epsilon_values = [0.1, 0.3, 0.9]

    if number_of_tiles == "mix":
        dir_path_for_inputs = "C:\\Users\\sarah\\Documents\\These\\Sub-problems\\2__tree-merging__Cmax\\3-Programmation\\Inputs\\mix\\"
        dir_path_for_results = "C:\\Users\\sarah\\Documents\\These\\Sub-problems\\2__tree-merging__Cmax\\3-Programmation\\Results\\mix\\"
        dir_path_for_recap = "C:\\Users\\sarah\\Documents\\These\\Sub-problems\\2__tree-merging__Cmax\\3-Programmation\\Results\\mix\\recap\\"
   
    elif number_of_tiles == "test":
        dir_path_for_inputs = "C:\\Users\\sarah\\Documents\\These\\Sub-problems\\2__tree-merging__Cmax\\3-Programmation\\Inputs\\inputs_for_tests"
        dir_path_for_results = "C:\\Users\\sarah\\Documents\\These\\Sub-problems\\2__tree-merging__Cmax\\3-Programmation\\Results\\tests"
        dir_path_for_recap = "C:\\Users\\sarah\\Documents\\These\\Sub-problems\\2__tree-merging__Cmax\\3-Programmation\\Results\\tests\\recap"
    
    else:
        dir_path_for_inputs = "C:\\Users\\sarah\\Documents\\These\\Sub-problems\\2__tree-merging__Cmax\\3-Programmation\\Inputs\\" + str(number_of_tiles) + "_tiles"
        dir_path_for_results = "C:\\Users\\sarah\\Documents\\These\\Sub-problems\\2__tree-merging__Cmax\\3-Programmation\\Results\\" + str(number_of_tiles) + "_tiles"
        dir_path_for_recap = "C:\\Users\\sarah\\Documents\\These\\Sub-problems\\2__tree-merging__Cmax\\3-Programmation\\Results\\" + str(number_of_tiles) + "_tiles\\recap"

    filenames_with_extension = files_in(dir_path_for_inputs)
    filenames_without_extension = list()

    for filename in filenames_with_extension:
        before, separator, after = filename.partition(".")
        filenames_without_extension.append(before)


    # Recap files
    if number_of_tiles == "mix":
        tools.generating_all_the_recap_files(100, range_for_epsilon_values, dir_path_for_recap)
        tools.generating_all_the_recap_files(200, range_for_epsilon_values, dir_path_for_recap)
        tools.generating_all_the_recap_files(400, range_for_epsilon_values, dir_path_for_recap)
    elif number_of_tiles == "test":
        tools.generating_all_the_recap_files(100, range_for_epsilon_values, dir_path_for_recap)
    else:
        tools.generating_all_the_recap_files(number_of_tiles, range_for_epsilon_values, dir_path_for_recap)

    print("Is everything ready ? Are you in the right folder ? Did you create the recap folder in your results ? Did you choose the right \noption for your tests ? Did you save the previous results ? Did \nyou turn off the wifi ? Is your laptop at its maximum workload capacity ?")
    print("Here are the characteristics for this run :")
    print(f"Number of tiles : {number_of_tiles}")
    print("Number of iterations : ", number_of_iterations)
    print("Set of values for epsilon : ", range_for_epsilon_values)
    print("Source : ", dir_path_for_inputs)
    print("Ending : ", dir_path_for_results)
    print("Do you have anything to change ? Well DO IT NOW, YOU IDIOT")
    rep = input ("Enter your answer.")

    start = time.time()
    print("Beginning of run.")
    for filename in filenames_without_extension:
        my_input = tools.load_json_instance_from(dir_path_for_inputs, filename)
        print("Now computing the instance ", my_input.name)
        print("Program running for ", (time.time() - start)/60, "minutes now")
 
        #Computing the FPTAS
        my_str = my_input.full_instance_to_str()
        my_str += "\n\nResults of the FPTAS :\nrun_number;epsilon;Cmax;Time_needed;total_nb_of_generated_states\n"
        pre_filling_the_file(my_input.name + "_full_results", dir_path_for_results, my_str, "w")
        my_str = "FPTAS :\nepsilon;number_of_iterations;average_value;average_time;total_nb_of_generated_states\n"
        pre_filling_the_file(my_input.name + "_result_summary", dir_path_for_results, my_str, "w")
        (full_results_to_str, summary_to_str) = computing_fptas_on_one_instance_for_some_epsilons(my_input, number_of_iterations, range_for_epsilon_values)
        writing_in_file(my_input.name + "_full_results", dir_path_for_results, full_results_to_str, "a")
        writing_in_file(my_input.name + "_result_summary", dir_path_for_results, summary_to_str, "a")

        #Computing the improved FPTAS
        my_str = "\n\nImproved FPTAS :\nepsilon;number_of_iterations;average_value;average_time;total_nb_of_generated_states\n"
        pre_filling_the_file(my_input.name + "_full_results", dir_path_for_results, my_str, "a")
        my_str = "\n\nImproved FPTAS :\nepsilon;number_of_iterations;average_value;average_time;total_nb_of_generated_states\n"
        pre_filling_the_file(my_input.name + "_result_summary", dir_path_for_results, my_str, "a")
        
        (full_results_to_str, summary_to_str) = computing_improved_fptas_on_one_instance_for_some_epsilons(my_input, number_of_iterations, range_for_epsilon_values)
        
        writing_in_file(my_input.name + "_full_results", dir_path_for_results, full_results_to_str, "a")
        writing_in_file(my_input.name + "_result_summary", dir_path_for_results, summary_to_str, "a")

    print("End of run after", time.time() - start," seconds, ", (time.time() - start)/60, "minutes, ", ((time.time() - start)/60)/60, "hours.")



# Astuce que j'ai suivi pour que le fichier de recap ait le format que je voulais.
# Je veux que dans le fichier concernant un epsilon particulier, il y ait, sur une même ligne,
# le nom de l'instance ; la valeur trouvée par le FPTAS ; le temps pris par le FPTAS ; la valeur trouvée par
# le FPTAS amélioré (improved FPTAS <-> iFPTAS) ; le temps pris par le FPTAS amélioré.
# Puisque dans mon code, pour chaque instance, j'appliquais le FPTAS puis après le FPTAS amélioré, j'ai fait 
# que dans la fonction "computing_improved_fptas_on_one_instance_for_all_epsilons" les résultats s'écrivent sans
# sauter de ligne. Ainsi, ils s'écrivent à la ligne suivant de ce qui a déjà été écrit... les résultats du FPTAS
# pour le epsilon en question.