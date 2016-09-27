import socket
import operator
from collections import defaultdict
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

def accumulative_performances(teams_population, point_ids, sorting_criteria, get_results_per_points):
    sorted_teams = sorted(teams_population, key=lambda team: sorting_criteria(team), reverse = True) # better ones first
    individual_performance = []
    accumulative_performance = []
    best_results_per_point = defaultdict(int)
    for team in sorted_teams:
        total = 0.0
        for key, item in get_results_per_points(team).iteritems():
            if key in point_ids:
                total += item
                if item > best_results_per_point[key]:
                    best_results_per_point[key] = item
        individual_performance.append(round_value(total))
        accumulative_performance.append(round_value(sum(best_results_per_point.values())))
    teams_ids = [t.__repr__() for t in sorted_teams]
    return individual_performance, accumulative_performance, teams_ids

def rank_teams_by_accumulative_score(ind_scores, acc_scores, list_ids, threshold_for_score_improvement = 0.1):
    if len(ind_scores) == 0:
        return []
    best_teams = {}
    
    # adds the first score
    best_teams[list_ids[0]] = acc_scores[0]

    # check if the other scores are good enough
    previous_score = acc_scores[0]
    for score, team_id in zip(acc_scores, list_ids):
        score_improvement = score - previous_score
        if score_improvement > threshold_for_score_improvement:
            if team_id not in best_teams:
                best_teams[team_id] = round_value(score_improvement)
            else:
                if score_improvement > best_teams[team_id]:
                    best_teams[team_id] = round_value(score_improvement)
        previous_score = score
    # sort the best scores
    rank = sorted(best_teams.items(), key=operator.itemgetter(1), reverse=True)
    return rank