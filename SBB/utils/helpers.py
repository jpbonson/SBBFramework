import random
from ..config import Config

"""
This file contains small and simple methods that help other classes.
"""

def round_value(value, round_decimals_to = Config.RESTRICTIONS['round_to_decimals']):
    number = float(10**round_decimals_to)
    return int(value * number) / number

def round_array(array, round_decimals_to = Config.RESTRICTIONS['round_to_decimals']):
    new_array = []
    for value in array:
        new_array.append(round_value(value))
    return new_array

def flatten(list_of_lists):
    return sum(list_of_lists, [])

def is_nearly_equal_to(value1, value2):
    if abs(value1 - value2) < Config.RESTRICTIONS['is_nearly_equal_threshold']:
        return True
    return False