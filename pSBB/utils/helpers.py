from ..config import RESTRICTIONS

def round_value_to_decimals(value, round_decimals_to = RESTRICTIONS['round_to_decimals']):
    number = float(10**round_decimals_to)
    return int(value * number) / number

def round_array_to_decimals(array, round_decimals_to = RESTRICTIONS['round_to_decimals']):
    new_array = []
    for value in array:
        new_array.append(round_value_to_decimals(value))
    return new_array

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