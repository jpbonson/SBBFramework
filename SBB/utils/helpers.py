import random
from ..config import RESTRICTIONS

"""
This file contains small and simple methods that help other classes.
"""

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