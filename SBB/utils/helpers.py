import random
from ..config import RESTRICTIONS

def round_value_to_decimals(value, round_decimals_to = RESTRICTIONS['round_to_decimals']):
    number = float(10**round_decimals_to)
    return int(value * number) / number

def round_array_to_decimals(array, round_decimals_to = RESTRICTIONS['round_to_decimals']):
    new_array = []
    for value in array:
        new_array.append(round_value_to_decimals(value))
    return new_array

def flatten(list_of_lists):
    return sum(list_of_lists, [])

def remove_introns(instructions): # move code to C or Cython?
    """
    Remove introns (ie. instructions that don't affect the final output)
    """
    instructions_without_introns = []
    relevant_registers = [0]
    ignore_previous_if = False
    # Run throught the instructions from the last to the first one
    for instruction in reversed(instructions):
        if instruction.target in relevant_registers or instruction.op in RESTRICTIONS['genotype_options']['if-instructions']:
            if ignore_previous_if and instruction.op in RESTRICTIONS['genotype_options']['if-instructions']:
                continue
            else:
                ignore_previous_if = False
                instructions_without_introns.insert(0, instruction)
                if instruction.mode == 'read-register' and instruction.source not in relevant_registers:
                    relevant_registers.append(instruction.source)
                if instruction.op in RESTRICTIONS['genotype_options']['if-instructions']:
                    if instruction.target not in relevant_registers:
                        relevant_registers.append(instruction.target)
        else:
            ignore_previous_if = True
    return instructions_without_introns

def is_nearly_equal_to(value1, value2):
    if abs(value1 - value2) < 0.1:
        return True
    return False

def weighted_choice(weights):
    """
    Randomly return an index from an array of weights so that higher weights have a higher chance of 
    being selected.
    """
    pick = random.uniform(0, sum(weights))
    current = 0
    for index, f in enumerate(weights):
        current += f
        if current > pick:
            return index
    raise IndexError("weighted_choice() wasn't able to return an index")

def pareto_front(solutions, results_map): # unit test!
    """
    Finds the pareto front, i.e. the pareto dominant solutions.
    Pareto dominance: Given a set of objectives, a solution is said to Pareto dominate another if the 
    first is not inferior to the second in all objectives, and, additionally, there is at least one 
    objective where it is better.
    """
    front = []
    dominateds = []
    i = 0
    for solution, outcomes1 in zip(solutions, results_map):
        is_dominated = False
        j = 0
        for outcomes2 in results_map:
            is_dominated, is_equal = check_if_is_dominated(outcomes1, outcomes2)
            if j < i and is_equal: # also dominated if equal to a previous processed item, since this one would be irrelevant
                is_dominated = True
            if is_dominated:
                break
            j += 1
        if is_dominated:
            dominateds.append(solution)
        else:
            front.append(solution)
        i += 1
    return front, dominateds

def check_if_is_dominated(results1, results2): # unit test!
    """
    Check if a solution is domninated or equal to another, assuming that higher results are better than lower ones.
    """  
    equal = True
    for index in range(len(results1)):
        if not is_nearly_equal_to(results1[index], results2[index]):
            equal = False
            if(results1[index] > results2[index]): # not dominated since "results1" is greater than "results2" in this dimension
                return False, equal
    if equal:
        return False, equal
    else:
        return True, equal

def balance_population_to_up(population, keep_solutions, remove_solutions, to_keep):
    sorted_solutions = sorted(population, key=lambda solution: solution.fitness_, reverse=True)
    for solution in sorted_solutions:
        if solution not in keep_solutions:
            keep_solutions.append(solution)
            remove_solutions.remove(solution)
        if len(keep_solutions) == to_keep:
            break
    return keep_solutions, remove_solutions

def balance_population_to_down(population, keep_solutions, remove_solutions, to_keep):
    sorted_solutions = sorted(population, key=lambda solution: solution.fitness_, reverse=False)
    for solution in sorted_solutions:
        keep_solutions.remove(solution)
        remove_solutions.append(solution)
        if len(keep_solutions) == to_keep:
            break
    return keep_solutions, remove_solutions