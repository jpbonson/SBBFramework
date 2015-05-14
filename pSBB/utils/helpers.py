from collections import defaultdict
from ..config import RESTRICTIONS

def round_value_to_decimals(value, round_decimals_to = RESTRICTIONS['round_to_decimals']):
    number = float(10**round_decimals_to)
    return int(value * number) / number

def round_array_to_decimals(array, round_decimals_to = RESTRICTIONS['round_to_decimals']):
    new_array = []
    for value in array:
        new_array.append(round_value_to_decimals(value))
    return new_array

def get_X(data):
    return [x[:-1] for x in data]

def get_Y(data):
    Y = [x[-1:] for x in data]
    Y = sum(Y, [])
    Y = [int(y) for y in Y]
    if 0 not in Y:
        Y = [y-1 for y in Y]  # added -1 due to class labels starting at 1
    return Y

def get_class_distribution(Y):
    cont = defaultdict(int)
    for y in Y:
        cont[y] += 1
    print("Class Distributions: "+str(cont)+", for a total of "+str(len(Y))+" samples")
    return cont

def read_inputs_already_partitioned(data_name):
    train = read_space_separated_file(RESTRICTIONS['working_path']+"datasets/"+data_name+".train")
    test = read_space_separated_file(RESTRICTIONS['working_path']+"datasets/"+data_name+".test")
    return train, test

def read_space_separated_file(file_path):
    with open(file_path) as f:
        content = f.readlines()
        content = [x.strip('\n').strip() for x in content]
        content = [x.split(' ') for x in content]
        content = [[float(y) for y in x]for x in content]
    return content

def remove_introns(instructions): # move code to C or Cython?
    """ Remove introns (ie. instructions that don't affect the final output) """
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