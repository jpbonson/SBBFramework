import sys
import gc
import math
import json
import yappi
import operator
import itertools
import os
import subprocess
import threading
import random
import numpy
import linecache
from collections import defaultdict
from opponent_model import OpponentModel
from poker_point import PokerPoint
from poker_config import PokerConfig
from poker_metrics import PokerMetrics
from poker_player_execution import PokerPlayerExecution
from poker_opponents import PokerRandomOpponent, PokerAlwaysFoldOpponent, PokerAlwaysCallOpponent, PokerAlwaysRaiseOpponent, PokerLooseAgressiveOpponent, PokerLoosePassiveOpponent, PokerTightAgressiveOpponent, PokerTightPassiveOpponent
from ..reinforcement_environment import ReinforcementEnvironment
from ...utils.helpers import available_ports, round_value, flatten
from ...config import Config

class PokerEnvironment(ReinforcementEnvironment):
    """
    This environment encapsulates all methods to deal with a reinforcement learning task for TicTacToe.
    """

    def __init__(self):
        total_actions = 3 # fold, call, raise
        total_inputs = len(PokerConfig.CONFIG['inputs'])
        total_labels = len(PokerConfig.CONFIG['hand_strength_labels'].keys())
        coded_opponents_for_training = [PokerLooseAgressiveOpponent, PokerLoosePassiveOpponent]
        coded_opponents_for_validation = [PokerLooseAgressiveOpponent, PokerLoosePassiveOpponent]
        point_class = PokerPoint
        super(PokerEnvironment, self).__init__(total_actions, total_inputs, total_labels, coded_opponents_for_training, coded_opponents_for_validation, point_class)
        PokerConfig.CONFIG['labels_per_subdivision']['opponent'] = self.opponent_names_for_validation_
        port1, port2 = available_ports()
        PokerConfig.CONFIG['available_ports'] = [port1, port2]
        self.num_lines_per_file_ = []
        self.backup_points_per_label =[]

    def _initialize_random_population_of_points(self, population_size):
        if len(self.num_lines_per_file_) == 0:
            for label in range(self.total_labels_):
                self.num_lines_per_file_.append(sum([1 for line in open("SBB/environments/poker/hand_types/"+Config.USER['reinforcement_parameters']['poker']['balance_based_on']+"/hands_type_"+str(label)+".json")]))
        population_size_per_label = population_size/self.total_labels_
        data = self._sample_point_per_label(population_size_per_label)
        data = flatten(data)
        random.shuffle(data)
        return data

    def _points_to_add_per_label(self, total_points_to_add):
        total_points_to_add_per_label = total_points_to_add/self.total_labels_
        return self._sample_point_per_label(total_points_to_add_per_label)

    def _sample_point_per_label(self, population_size_per_label):
        if len(self.backup_points_per_label) == 0:
            data = []
            for label in range(self.total_labels_):
                idxs = random.sample(range(1, self.num_lines_per_file_[label]+1), population_size_per_label*PokerConfig.CONFIG['point_cache_size'])
                result = [linecache.getline("SBB/environments/poker/hand_types/"+Config.USER['reinforcement_parameters']['poker']['balance_based_on']+"/hands_type_"+str(label)+".json", i) for i in idxs]
                data.append([PokerPoint(label, json.loads(r)) for r in result])
            self.backup_points_per_label = data
        data = []
        for sample in self.backup_points_per_label:
            data.append(sample[:population_size_per_label])
            sample = sample[population_size_per_label:]
        return data

    def _play_match(self, team, opponent, point, mode):
        """

        """
        if mode == Config.RESTRICTIONS['mode']['training']:
            is_training = True
        else:
            is_training = False

        if Config.USER['reinforcement_parameters']['debug_matches'] and not os.path.exists(PokerConfig.CONFIG['acpc_path']+"outputs/"):
            os.makedirs(PokerConfig.CONFIG['acpc_path']+"outputs/")

        if point.position_ == 0:
            sbb_port = PokerConfig.CONFIG['available_ports'][0]
            opponent_port = PokerConfig.CONFIG['available_ports'][1]
            player1 = 'sbb'
            player2 = 'opponent'
        else:
            sbb_port = PokerConfig.CONFIG['available_ports'][1]
            opponent_port = PokerConfig.CONFIG['available_ports'][0]
            player1 = 'opponent'
            player2 = 'sbb'

        opponent_use_inputs = None
        if opponent.opponent_id == "hall_of_fame":
            opponent_use_inputs = 'all'
        if opponent.opponent_id in PokerConfig.CONFIG['rule_based_opponents']:
            opponent_use_inputs = 'rule_based_opponent'

        t1 = threading.Thread(target=PokerPlayerExecution.execute_player, args=[team, opponent, point, sbb_port, is_training, True, 'all'])
        t2 = threading.Thread(target=PokerPlayerExecution.execute_player, args=[opponent, team, point, opponent_port, False, False, opponent_use_inputs])
        args = [PokerConfig.CONFIG['acpc_path']+'dealer', 
                PokerConfig.CONFIG['acpc_path']+'outputs/match_output', 
                PokerConfig.CONFIG['acpc_path']+'holdem.limit.2p.reverse_blinds.game', 
                "1", # total hands 
                str(point.seed_),
                player1, player2, 
                '-p', str(PokerConfig.CONFIG['available_ports'][0])+","+str(PokerConfig.CONFIG['available_ports'][1])]
        if not Config.USER['reinforcement_parameters']['debug_matches']:
            args.append('-l')
        p = subprocess.Popen(args, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        t1.start()
        t2.start()
        out, err = p.communicate()
        t1.join()
        t2.join()

        if Config.USER['reinforcement_parameters']['debug_matches']:
            with open(PokerConfig.CONFIG['acpc_path']+"outputs/match.log", "w") as text_file:
                text_file.write(str(err))
        score = out.split("\n")[1]
        score = score.replace("SCORE:", "")
        splitted_score = score.split(":")
        scores = splitted_score[0].split("|")
        players = splitted_score[1].split("|")
        if players[0] == 'sbb':
            sbb_position = 0
            opponent_position = 1
        else:
            sbb_position = 1
            opponent_position = 0

        normalized_value = PokerMetrics.normalize_winning(float(scores[sbb_position]))

        PokerPlayerExecution.get_chips(team, opponent).append(normalized_value)
        if opponent.opponent_id == "hall_of_fame":
            PokerPlayerExecution.get_chips(opponent, team).append(PokerMetrics.normalize_winning(float(scores[opponent_position])))

        if not is_training:
            if mode == Config.RESTRICTIONS['mode']['validation']:
                self._update_team_extra_metrics_for_poker(team, point, normalized_value, 'validation')
                point.last_validation_opponent_id_ = opponent.opponent_id
                if team.extra_metrics_['played_last_hand']:
                    team.extra_metrics_['hands_played_or_not_per_point'][point.point_id_] = 1.0
                    if normalized_value > 0.5:
                        team.extra_metrics_['hands_won_or_lost_per_point'][point.point_id_] = 1.0
                    else:
                        team.extra_metrics_['hands_won_or_lost_per_point'][point.point_id_] = 0.0
                else:
                    team.extra_metrics_['hands_played_or_not_per_point'][point.point_id_] = 0.0
                    team.extra_metrics_['hands_won_or_lost_per_point'][point.point_id_] = 0.0
            else:
                self._update_team_extra_metrics_for_poker(team, point, normalized_value, 'champion')

        if Config.USER['reinforcement_parameters']['debug_matches']:
            print "scores: "+str(scores)
            print "players: "+str(players)
            print "normalized_value: "+str(normalized_value)

        point.teams_results_.append(normalized_value)

        return normalized_value

    def _update_team_extra_metrics_for_poker(self, team, point, normalized_value, mode_label):
        team.extra_metrics_['total_hands'][mode_label] += 1
        team.extra_metrics_['total_hands_per_point_type'][mode_label]['position'][point.position_] += 1
        team.extra_metrics_['total_hands_per_point_type'][mode_label]['sbb_label'][point.label_] += 1
        team.extra_metrics_['total_hands_per_point_type'][mode_label]['sbb_extra_label'][point.sbb_extra_label_] += 1
        team.extra_metrics_['total_hands_per_point_type'][mode_label]['sbb_sd'][point.sbb_sd_label_] += 1
        if team.extra_metrics_['played_last_hand']:
            team.extra_metrics_['hand_played'][mode_label] += 1
            team.extra_metrics_['hand_played_per_point_type'][mode_label]['position'][point.position_] += 1
            team.extra_metrics_['hand_played_per_point_type'][mode_label]['sbb_label'][point.label_] += 1
            team.extra_metrics_['hand_played_per_point_type'][mode_label]['sbb_extra_label'][point.sbb_extra_label_] += 1
            team.extra_metrics_['hand_played_per_point_type'][mode_label]['sbb_sd'][point.sbb_sd_label_] += 1
            if normalized_value > 0.5:
                team.extra_metrics_['won_hands'][mode_label] += 1
                team.extra_metrics_['won_hands_per_point_type'][mode_label]['position'][point.position_] += 1
                team.extra_metrics_['won_hands_per_point_type'][mode_label]['sbb_label'][point.label_] += 1
                team.extra_metrics_['won_hands_per_point_type'][mode_label]['sbb_extra_label'][point.sbb_extra_label_] += 1
                team.extra_metrics_['won_hands_per_point_type'][mode_label]['sbb_sd'][point.sbb_sd_label_] += 1

    def reset(self):
        super(PokerEnvironment, self).reset()
        gc.collect()
        yappi.clear_stats()

    def setup(self, teams_population):
        super(PokerEnvironment, self).setup(teams_population)
        if Config.USER['reinforcement_parameters']['hall_of_fame']['enabled']:
            self._clear_hall_of_fame_memory()
        for point in self.point_population():
            point.teams_results_ = []
        gc.collect()
        yappi.clear_stats()

    def _clear_hall_of_fame_memory(self):
        for opponent in self.opponent_population_['hall_of_fame']:
            opponent.opponent_model = {}
            opponent.chips = {}

    def evaluate_team(self, team, mode):
        team.opponent_model = {}
        team.chips = {} # Chips (the stacks are infinite, but it may be useful to play more conservative if it is losing a lot)
        super(PokerEnvironment, self).evaluate_team(team, mode)
        if mode != Config.RESTRICTIONS['mode']['training']:
            self_long_term_agressiveness = []
            self_agressiveness_preflop = []
            self_agressiveness_postflop = []
            for key, item in team.opponent_model.iteritems():
                self_long_term_agressiveness += item.self_agressiveness
                self_agressiveness_preflop += item.self_agressiveness_preflop
                self_agressiveness_postflop += item.self_agressiveness_postflop
            agressiveness = -1
            volatility = -1
            if len(self_long_term_agressiveness) > 0:
                agressiveness = numpy.mean(self_long_term_agressiveness)
            if len(self_agressiveness_preflop) > 0 and len(self_agressiveness_postflop) > 0:
                volatility = OpponentModel.calculate_volatility(self_agressiveness_postflop, self_agressiveness_preflop)
            if mode == Config.RESTRICTIONS['mode']['validation']:
                team.extra_metrics_['agressiveness'] = agressiveness
                team.extra_metrics_['volatility'] = volatility
            if mode == Config.RESTRICTIONS['mode']['champion']:
                team.extra_metrics_['agressiveness_champion'] = agressiveness
                team.extra_metrics_['volatility_champion'] = volatility
        # to clean memmory
        team.opponent_model = {}
        team.chips = {}

    def _initialize_extra_metrics_for_points(self):
        extra_metrics_points = {}
        extra_metrics_points['position'] = defaultdict(list)
        extra_metrics_points['sbb_label'] = defaultdict(list)
        extra_metrics_points['sbb_extra_label'] = defaultdict(list)
        extra_metrics_points['sbb_sd'] = defaultdict(list)
        extra_metrics_points['opp_label'] = defaultdict(list)
        extra_metrics_points['opp_extra_label'] = defaultdict(list)
        return extra_metrics_points

    def _update_extra_metrics_for_points(self, extra_metrics_points, point, result):
        extra_metrics_points['position'][point.position_].append(result)
        extra_metrics_points['sbb_label'][point.label_].append(result)
        extra_metrics_points['sbb_extra_label'][point.sbb_extra_label_].append(result)
        extra_metrics_points['sbb_sd'][point.sbb_sd_label_].append(result)
        extra_metrics_points['opp_label'][point.opp_label_].append(result)
        extra_metrics_points['opp_extra_label'][point.opp_extra_label_].append(result)
        return extra_metrics_points

    def validate(self, current_generation, teams_population):
        if Config.USER['reinforcement_parameters']['hall_of_fame']['enabled']:
            self._clear_hall_of_fame_memory()

        keys = ['validation', 'champion']
        subkeys = ['position', 'sbb_label', 'sbb_extra_label', 'sbb_sd']
        metrics_with_counts = ['total_hands', 'hand_played', 'won_hands']
        metrics_with_dicts = ['total_hands_per_point_type', 'hand_played_per_point_type', 'won_hands_per_point_type']
        for team in teams_population:
            if team.generation != current_generation:
                for metric in (metrics_with_counts + metrics_with_dicts):
                    team.extra_metrics_[metric] = {}
                team.extra_metrics_['hands_played_or_not_per_point'] = {}
                team.extra_metrics_['hands_won_or_lost_per_point'] = {}
                for key in keys:
                    for metric in metrics_with_counts:
                        team.extra_metrics_[metric][key] = 0
                    for metric in metrics_with_dicts:
                        team.extra_metrics_[metric][key] = {}
                        for subkey in subkeys:
                            team.extra_metrics_[metric][key][subkey] = defaultdict(int)

        for point in self.validation_population():
            point.teams_results_ = []

        best_team = super(PokerEnvironment, self).validate(current_generation, teams_population)
        return best_team

    def metrics(self):
        msg = ""
        msg += "\n### Environment Info:"
        msg += "\nports: "+str(PokerConfig.CONFIG['available_ports'])
        msg += "\ntotal inputs: "+str(self.total_inputs_)
        msg += "\ninputs: "+str([str(index)+": "+value for index, value in enumerate(PokerConfig.CONFIG['inputs'])])
        msg += "\ntotal actions: "+str(self.total_actions_)
        msg += "\nactions mapping: "+str(PokerConfig.CONFIG['action_mapping'])
        msg += "\npositions: "+str(PokerConfig.CONFIG['positions'])
        msg += "\ntraining opponents: "+str([c.__name__ for c in self.coded_opponents_for_training_])
        msg += "\nvalidation opponents: "+str([c.__name__ for c in self.coded_opponents_for_validation_])
        if Config.USER['reinforcement_parameters']['hall_of_fame']['enabled']:
            msg += "\nhall of fame size: "+str(Config.USER['reinforcement_parameters']['hall_of_fame']['size'])
        return msg

    def calculate_poker_metrics_per_validation(self, run_info):
        self._calculate_point_population_metrics_per_validation(run_info)
        self._calculate_validation_population_metrics_per_validation(run_info)

    def _calculate_point_population_metrics_per_validation(self, run_info):
        self._calculate_point_population_metric_per_validation(run_info, lambda x: x.position_, 'position', range(PokerConfig.CONFIG['positions']))
        self._calculate_point_population_metric_per_validation(run_info, lambda x: x.label_, 'sbb_label', PokerConfig.CONFIG['hand_strength_labels'].keys())
        self._calculate_point_population_metric_per_validation(run_info, lambda x: x.opp_label_, 'opp_label', PokerConfig.CONFIG['hand_strength_labels'].keys())
        self._calculate_point_population_metric_per_validation(run_info, lambda x: x.sbb_extra_label_, 'sbb_extra_label', PokerConfig.CONFIG['hand_strength_labels'].keys())
        self._calculate_point_population_metric_per_validation(run_info, lambda x: x.opp_extra_label_, 'opp_extra_label', PokerConfig.CONFIG['hand_strength_labels'].keys())
        self._calculate_point_population_metric_per_validation(run_info, lambda x: x.sbb_sd_label_, 'sd_label', range(3))

    def _calculate_point_population_metric_per_validation(self, run_info, get_attribute, key, labels):
        for label in labels:
            total = len([point for point in self.point_population() if get_attribute(point) == label])
            if label not in run_info.point_population_distribution_per_validation[key]:
                run_info.point_population_distribution_per_validation[key][label] = []
            run_info.point_population_distribution_per_validation[key][label].append(total)

    def _calculate_validation_population_metrics_per_validation(self, run_info):
        self._calculate_validation_population_metric_per_validation(run_info, lambda x: x.position_, 'position', range(PokerConfig.CONFIG['positions']))
        self._calculate_validation_population_metric_per_validation(run_info, lambda x: x.label_, 'sbb_label', PokerConfig.CONFIG['hand_strength_labels'].keys())
        self._calculate_validation_population_metric_per_validation(run_info, lambda x: x.opp_label_, 'opp_label', PokerConfig.CONFIG['hand_strength_labels'].keys())
        self._calculate_validation_population_metric_per_validation(run_info, lambda x: x.sbb_extra_label_, 'sbb_extra_label', PokerConfig.CONFIG['hand_strength_labels'].keys())
        self._calculate_validation_population_metric_per_validation(run_info, lambda x: x.opp_extra_label_, 'opp_extra_label', PokerConfig.CONFIG['hand_strength_labels'].keys())
        self._calculate_validation_population_metric_per_validation(run_info, lambda x: x.sbb_sd_label_, 'sd_label', range(3))

    def _calculate_validation_population_metric_per_validation(self, run_info, get_attribute, key, labels):
        point_per_distribution = {}
        for label in labels:
            point_per_distribution[label] = [point for point in self.validation_population() if get_attribute(point) == label]
        run_info.validation_population_distribution_per_validation[key] = {}
        for label in labels:
            run_info.validation_population_distribution_per_validation[key][label] = len(point_per_distribution[label])

        for label in labels:
            temp = flatten([point.teams_results_ for point in point_per_distribution[label]])
            if len(temp) > 0:
                means_per_position = round_value(numpy.mean(temp))
            else:
                means_per_position = 0.0
            if label not in run_info.global_result_per_validation[key]:
                run_info.global_result_per_validation[key][label] = []
            run_info.global_result_per_validation[key][label].append(means_per_position)

        point_per_distribution = {}
        for label in labels:
            point_per_distribution[label] = [point for point in self.champion_population() if get_attribute(point) == label]
        run_info.champion_population_distribution_per_validation[key] = {}
        for label in labels:
            run_info.champion_population_distribution_per_validation[key][label] = len(point_per_distribution[label])

    def calculate_accumulative_performances(self, run_info, teams_population, current_generation):
        older_teams = [team for team in teams_population if team.generation != current_generation]

        for metric in ['score', 'hands_played', 'hands_won']:
            if metric == 'score':
                sorting_criteria = lambda x: x.extra_metrics_['validation_score']
                get_results_per_points = lambda x: x.results_per_points_for_validation_
            if metric == 'hands_played':
                sorting_criteria = lambda x: numpy.mean(x.extra_metrics_['hands_played_or_not_per_point'].values())
                get_results_per_points = lambda x: x.extra_metrics_['hands_played_or_not_per_point']
            if metric == 'hands_won':
                sorting_criteria = lambda x: numpy.mean(x.extra_metrics_['hands_won_or_lost_per_point'].values())
                get_results_per_points = lambda x: x.extra_metrics_['hands_won_or_lost_per_point']
            point_ids = [point.point_id_ for point in self.validation_population()]
            individual_performance, accumulative_performance, teams_ids = self._accumulative_performance(older_teams, point_ids, sorting_criteria, get_results_per_points)
            run_info.individual_performance_in_last_generation[metric] = individual_performance
            run_info.accumulative_performance_in_last_generation[metric] = accumulative_performance
            run_info.ids_for_acc_performance_in_last_generation[metric] = teams_ids

            for subdivision in PokerConfig.CONFIG['labels_per_subdivision'].keys():
                run_info.individual_performance_per_label_in_last_generation[metric][subdivision] = {}
                run_info.accumulative_performance_per_label_in_last_generation[metric][subdivision] = {}
                run_info.ids_for_acc_performance_per_label_in_last_generation[metric][subdivision] = {}
                for label in PokerConfig.CONFIG['labels_per_subdivision'][subdivision]:
                    point_ids = [point.point_id_ for point in self.validation_population() if PokerConfig.CONFIG['attributes_per_subdivision'][subdivision](point) == label]
                    if metric == 'score':
                        sorting_criteria_per_label = lambda x: numpy.mean([x.results_per_points_for_validation_[point_id] for point_id in point_ids])
                    if metric == 'hands_played':
                        sorting_criteria_per_label = lambda x: numpy.mean([x.extra_metrics_['hands_played_or_not_per_point'][point_id] for point_id in point_ids])
                    if metric == 'hands_won':
                        sorting_criteria_per_label = lambda x: numpy.mean([x.extra_metrics_['hands_won_or_lost_per_point'][point_id] for point_id in point_ids])
                    individual_performance, accumulative_performance, teams_ids = self._accumulative_performance(older_teams, point_ids, sorting_criteria_per_label, get_results_per_points)
                    run_info.individual_performance_per_label_in_last_generation[metric][subdivision][label] = individual_performance
                    run_info.accumulative_performance_per_label_in_last_generation[metric][subdivision][label] = accumulative_performance
                    run_info.ids_for_acc_performance_per_label_in_last_generation[metric][subdivision][label] = teams_ids

    def _accumulative_performance(self, teams_population, point_ids, sorting_criteria, get_results_per_points):
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