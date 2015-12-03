import socket
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
        new_array.append(round_value(value, round_decimals_to))
    return new_array

def flatten(list_of_lists):
    return sum(list_of_lists, [])

def is_nearly_equal_to(value1, value2, threshold = Config.RESTRICTIONS['is_nearly_equal_threshold']):
    if abs(value1 - value2) < threshold:
        return True
    return False

def available_ports():
    socket_tmp1 = socket.socket()
    socket_tmp1.bind(('', 0))
    socket_tmp2 = socket.socket()
    socket_tmp2.bind(('', 0))
    port1 = socket_tmp1.getsockname()[1]
    port2 = socket_tmp2.getsockname()[1]
    socket_tmp1.close()
    socket_tmp2.close()
    return port1, port2
