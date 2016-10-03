import sys
import math
import time
import json
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
from match_state import MatchState
from poker_match import PokerMatch
from poker_opponents import PokerRandomOpponent, PokerAlwaysCallOpponent, PokerAlwaysRaiseOpponent, PokerLooseAgressiveOpponent, PokerLoosePassiveOpponent, PokerTightAgressiveOpponent, PokerTightPassiveOpponent
from ..reinforcement_environment import ReinforcementEnvironment
from ...utils.helpers import round_value, flatten, accumulative_performances, rank_teams_by_accumulative_score
from ...config import Config

class PokerEnvironment(ReinforcementEnvironment):
    """
    This environment encapsulates all methods to deal with a reinforcement learning task for TicTacToe.
    """

    def __init__(self):
        total_actions = Config.USER['reinforcement_parameters']['environment_parameters']['actions_total'] # fold, call, raise
        total_inputs = Config.USER['reinforcement_parameters']['environment_parameters']['inputs_total']
        total_labels = Config.USER['reinforcement_parameters']['environment_parameters']['point_labels_total']
        PokerConfig.CONFIG['inputs'] = MatchState.INPUTS+OpponentModel.INPUTS
        if total_inputs != len(PokerConfig.CONFIG['inputs']):
            raise ValueError("Wrong value for 'total_inputs'")
        if total_labels != len(PokerConfig.CONFIG['labels_per_subdivision']['sbb_label']):
            raise ValueError("Wrong value for 'total_labels'")

        available_opponents = [PokerRandomOpponent, PokerAlwaysCallOpponent, PokerAlwaysRaiseOpponent, 
            PokerLooseAgressiveOpponent, PokerLoosePassiveOpponent, PokerTightAgressiveOpponent, 
            PokerTightPassiveOpponent]
        t_opponents = []
        for opponent in available_opponents:
            if opponent.OPPONENT_ID in Config.USER['reinforcement_parameters']['environment_parameters']['training_opponents_labels']:
                t_opponents.append(opponent)
        v_opponents = []
        for opponent in available_opponents:
            if opponent.OPPONENT_ID in Config.USER['reinforcement_parameters']['environment_parameters']['validation_opponents_labels']:
                v_opponents.append(opponent)

        point_class = PokerPoint
        super(PokerEnvironment, self).__init__(total_actions, total_inputs, total_labels, t_opponents, v_opponents, point_class)
        PokerConfig.CONFIG['labels_per_subdivision']['opponent'] = self.opponent_names_for_validation_
        self.num_lines_per_file_ = []
        self.backup_points_per_label = None

    def _initialize_random_population_of_points(self, population_size, ignore_cache = False):
        if len(self.num_lines_per_file_) == 0:
            for label in range(self.total_labels_):
                self.num_lines_per_file_.append(sum([1 for line in open("SBB/environments/poker/hand_generator/poker_hands/hands_type_"+str(label)+".json")]))
        population_size_per_label = population_size/self.total_labels_
        data = self._sample_point_per_label(population_size_per_label, ignore_cache)
        data = flatten(data)
        random.shuffle(data)
        return data

    def _points_to_add_per_label(self, total_points_to_add):
        total_points_to_add_per_label = total_points_to_add/self.total_labels_
        return self._sample_point_per_label(total_points_to_add_per_label, ignore_cache = False)

    def _sample_point_per_label(self, population_size_per_label, ignore_cache):
        if ignore_cache or self._cache_dont_have_enough_data(population_size_per_label):
            size = population_size_per_label
            if not ignore_cache and size < PokerConfig.CONFIG['point_cache_size']:
                size = PokerConfig.CONFIG['point_cache_size']
            data = []
            for label in range(self.total_labels_):
                idxs = random.sample(range(1, self.num_lines_per_file_[label]+1), size)
                result = [linecache.getline("SBB/environments/poker/hand_generator/poker_hands/hands_type_"+str(label)+".json", i) for i in idxs]
                data.append([PokerPoint(label, json.loads(r)) for r in result])
            if ignore_cache:
                return data
            self.backup_points_per_label = data
        data2 = []
        temp = []
        for sample in self.backup_points_per_label:
            data2.append(sample[:population_size_per_label])
            temp.append(sample[population_size_per_label:])
        self.backup_points_per_label = temp
        return data2

    def _cache_dont_have_enough_data(self, population_size_per_label):
        if self.backup_points_per_label is None:
            return True
        for data in self.backup_points_per_label:
            if len(data) < population_size_per_label:
                return True
        return False

    def _play_match(self, team, opponent, point, mode, match_id):
        match = PokerMatch(team, opponent, point, mode, match_id)
        result = match.run()
        if mode != Config.RESTRICTIONS['mode']['training']:
            self._update_team_metrics_for_poker(team, opponent, point, result, mode)
        return result

    def _update_team_metrics_for_poker(self, team, opponent, point, normalized_value, mode):
        if mode == Config.RESTRICTIONS['mode']['validation']:
            self._update_team_hand_metrics_for_poker(team, point, normalized_value, 'validation')
            point.last_validation_opponent_id_ = opponent.opponent_id

            if team.extra_metrics_['played_last_hand']:
                team.extra_metrics_['hands_played_or_not_per_point'][point.point_id_] = 1.0
            else:
                team.extra_metrics_['hands_played_or_not_per_point'][point.point_id_] = 0.0
            
            if normalized_value > 0.5:
                team.extra_metrics_['hands_won_or_lost_per_point'][point.point_id_] = 1.0
            elif normalized_value == 0.5:
                team.extra_metrics_['hands_won_or_lost_per_point'][point.point_id_] = 0.5
            else:
                team.extra_metrics_['hands_won_or_lost_per_point'][point.point_id_] = 0.0

        else:
            self._update_team_hand_metrics_for_poker(team, point, normalized_value, 'champion')

    def _update_team_hand_metrics_for_poker(self, team, point, normalized_value, mode_label):
        team.extra_metrics_['total_hands'][mode_label] += 1
        team.extra_metrics_['total_hands_per_point_type'][mode_label]['position'][point.players['team']['position']] += 1
        team.extra_metrics_['total_hands_per_point_type'][mode_label]['sbb_label'][point.label_] += 1
        team.extra_metrics_['total_hands_per_point_type'][mode_label]['sbb_sd'][point.sbb_sd_label_] += 1
        if team.extra_metrics_['played_last_hand']:
            team.extra_metrics_['hand_played'][mode_label] += 1
            team.extra_metrics_['hand_played_per_point_type'][mode_label]['position'][point.players['team']['position']] += 1
            team.extra_metrics_['hand_played_per_point_type'][mode_label]['sbb_label'][point.label_] += 1
            team.extra_metrics_['hand_played_per_point_type'][mode_label]['sbb_sd'][point.sbb_sd_label_] += 1
        if normalized_value > 0.5:
            team.extra_metrics_['won_hands'][mode_label] += 1
            team.extra_metrics_['won_hands_per_point_type'][mode_label]['position'][point.players['team']['position']] += 1
            team.extra_metrics_['won_hands_per_point_type'][mode_label]['sbb_label'][point.label_] += 1
            team.extra_metrics_['won_hands_per_point_type'][mode_label]['sbb_sd'][point.sbb_sd_label_] += 1

    def setup(self, teams_population):
        super(PokerEnvironment, self).setup(teams_population)
        if Config.USER['reinforcement_parameters']['hall_of_fame']['enabled']:
            self._clear_hall_of_fame_memory()
        for point in self.point_population():
            point.teams_results_ = []

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
            self_tight_loose = []
            self_passive_aggressive = []
            self_bluffing = []
            self_bluffing_only_raise = []
            for key, item in team.opponent_model.iteritems():
                self_long_term_agressiveness += item.self_agressiveness
                self_tight_loose += item.self_tight_loose
                self_passive_aggressive += item.self_passive_aggressive
                self_bluffing += item.self_bluffing
                self_bluffing_only_raise += item.self_bluffing_only_raise
            agressiveness = 0.5
            tight_loose = 0.5
            passive_aggressive = 0.5
            bluffing = 0.0
            bluffing_only_raise = 0.0
            if len(self_long_term_agressiveness) > 0:
                agressiveness = numpy.mean(self_long_term_agressiveness)
            if len(self_tight_loose) > 0:
                tight_loose = numpy.mean(self_tight_loose)
            if len(self_passive_aggressive) > 0:
                passive_aggressive = numpy.mean(self_passive_aggressive)
            if len(self_bluffing) > 0:
                bluffing = numpy.mean(self_bluffing)
            if len(self_bluffing_only_raise) > 0:
                bluffing_only_raise = numpy.mean(self_bluffing_only_raise)
            if mode == Config.RESTRICTIONS['mode']['validation']:
                team.extra_metrics_['agressiveness'] = agressiveness
                team.extra_metrics_['tight_loose'] = tight_loose
                team.extra_metrics_['passive_aggressive'] = passive_aggressive
                team.extra_metrics_['bluffing'] = bluffing
                team.extra_metrics_['bluffing_only_raise'] = bluffing_only_raise
            if mode == Config.RESTRICTIONS['mode']['champion']:
                team.extra_metrics_['agressiveness_champion'] = agressiveness
                team.extra_metrics_['tight_loose_champion'] = tight_loose
                team.extra_metrics_['passive_aggressive_champion'] = passive_aggressive
                team.extra_metrics_['bluffing_champion'] = bluffing
                team.extra_metrics_['bluffing_only_raise_champion'] = bluffing_only_raise
        # to clean memmory
        team.opponent_model = {}
        team.chips = {}

    def _initialize_extra_metrics_for_points(self):
        extra_metrics_points = {}
        extra_metrics_points['position'] = defaultdict(list)
        extra_metrics_points['sbb_label'] = defaultdict(list)
        extra_metrics_points['sbb_sd'] = defaultdict(list)
        return extra_metrics_points

    def _update_extra_metrics_for_points(self, extra_metrics_points, point, result):
        extra_metrics_points['position'][point.position_].append(result)
        extra_metrics_points['sbb_label'][point.label_].append(result)
        extra_metrics_points['sbb_sd'][point.sbb_sd_label_].append(result)
        return extra_metrics_points

    def validate(self, current_generation, teams_population):
        if Config.USER['reinforcement_parameters']['hall_of_fame']['enabled']:
            self._clear_hall_of_fame_memory()

        keys = ['validation', 'champion']
        subkeys = ['position', 'sbb_label', 'sbb_sd']
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
        msg += "\ntotal inputs: "+str(self.total_inputs_)
        msg += "\ninputs: "+str([str(index)+": "+value for index, value in enumerate(PokerConfig.CONFIG['inputs'])])
        msg += "\ntotal actions: "+str(self.total_actions_)
        msg += "\nactions mapping: "+str(PokerConfig.CONFIG['action_mapping'])
        msg += "\npositions: "+str(PokerConfig.CONFIG['positions'])
        msg += "\ntraining opponents: "+str(self.opponent_names_for_training_)
        msg += "\nvalidation opponents: "+str(self.opponent_names_for_validation_)
        if Config.USER['reinforcement_parameters']['hall_of_fame']['enabled']:
            msg += "\nhall of fame size: "+str(Config.USER['reinforcement_parameters']['hall_of_fame']['size'])
        return msg

    def calculate_poker_metrics_per_validation(self, run_info):
        self._calculate_point_population_metrics_per_validation(run_info)
        self._calculate_validation_population_metrics_per_validation(run_info)

    def _calculate_point_population_metrics_per_validation(self, run_info):
        self._calculate_point_population_metric_per_validation(run_info, lambda x: x.players['team']['position'], 'position', range(PokerConfig.CONFIG['positions']))
        self._calculate_point_population_metric_per_validation(run_info, lambda x: x.label_, 'sbb_label', PokerConfig.CONFIG['labels_per_subdivision']['sbb_label'])
        self._calculate_point_population_metric_per_validation(run_info, lambda x: x.sbb_sd_label_, 'sd_label', range(3))

    def _calculate_point_population_metric_per_validation(self, run_info, get_attribute, key, labels):
        for label in labels:
            total = len([point for point in self.point_population() if get_attribute(point) == label])
            if label not in run_info.point_population_distribution_per_validation[key]:
                run_info.point_population_distribution_per_validation[key][label] = []
            run_info.point_population_distribution_per_validation[key][label].append(total)

    def _calculate_validation_population_metrics_per_validation(self, run_info):
        self._calculate_validation_population_metric_per_validation(run_info, lambda x: x.players['team']['position'], 'position', range(PokerConfig.CONFIG['positions']))
        self._calculate_validation_population_metric_per_validation(run_info, lambda x: x.label_, 'sbb_label', PokerConfig.CONFIG['labels_per_subdivision']['sbb_label'])
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

    def calculate_final_validation_metrics(self, run_info, teams_population, current_generation):
        super(PokerEnvironment, self).calculate_final_validation_metrics(run_info, teams_population, current_generation)
        self._get_validation_scores_per_subcategory(run_info, teams_population, current_generation)

    def _calculate_accumulative_performances(self, run_info, teams_population, current_generation):
        older_teams = [team for team in teams_population if team.generation != current_generation]
        metrics = ['score', 'hands_played', 'hands_won']

        for metric in metrics:
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
            individual_performance, accumulative_performance, teams_ids = accumulative_performances(older_teams, point_ids, sorting_criteria, get_results_per_points)
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
                    individual_performance, accumulative_performance, teams_ids = accumulative_performances(older_teams, point_ids, sorting_criteria_per_label, get_results_per_points)
                    run_info.individual_performance_per_label_in_last_generation[metric][subdivision][label] = individual_performance
                    run_info.accumulative_performance_per_label_in_last_generation[metric][subdivision][label] = accumulative_performance
                    run_info.ids_for_acc_performance_per_label_in_last_generation[metric][subdivision][label] = teams_ids

    def _summarize_accumulative_performances(self, run_info, metrics = ['score', 'hands_played', 'hands_won']):
        super(PokerEnvironment, self)._summarize_accumulative_performances(run_info, metrics)

    def _get_validation_scores_per_subcategory(self, run_info, teams_population, current_generation):
        older_teams = [team for team in teams_population if team.generation != current_generation]
        run_info.final_teams_validations_ids = [team.__repr__() for team in older_teams]
        for subcategory in PokerConfig.CONFIG['labels_per_subdivision'].keys():
            for subdivision in PokerConfig.CONFIG['labels_per_subdivision'][subcategory]:
                run_info.final_teams_validations_per_subcategory[subcategory][subdivision] = []
                for team in older_teams:
                    if subcategory == 'opponent':
                        scores = team.extra_metrics_['opponents'][subdivision]
                    else:
                        scores = team.extra_metrics_['points'][subcategory][subdivision]
                    mean_score = numpy.mean(scores)
                    if not math.isnan(mean_score):
                        mean_score = round_value(mean_score)
                    run_info.final_teams_validations_per_subcategory[subcategory][subdivision].append(mean_score)

    def _initialize_extra_metrics_for_points(self):
        extra_metrics_points = {}
        extra_metrics_points['position'] = defaultdict(list)
        extra_metrics_points['sbb_label'] = defaultdict(list)
        extra_metrics_points['sbb_sd'] = defaultdict(list)
        return extra_metrics_points

    def _update_extra_metrics_for_points(self, extra_metrics_points, point, result):
        extra_metrics_points['position'][point.players['team']['position']].append(result)
        extra_metrics_points['sbb_label'][point.label_].append(result)
        extra_metrics_points['sbb_sd'][point.sbb_sd_label_].append(result)
        return extra_metrics_points

    def _get_highest_ranks(self, rank):
        best_teams = {}
        for team_id, score in rank:
            if team_id not in best_teams:
                best_teams[team_id] = score
            else:
                if score > best_teams[team_id]:
                    best_teams[team_id] = score
        rank = sorted(best_teams.items(), key=operator.itemgetter(1), reverse=True)
        return rank