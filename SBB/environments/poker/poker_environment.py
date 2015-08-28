import sys
import gc
import math
import json
import errno
import yappi
import socket
import operator
import itertools
import time
from socket import error as socket_error
import os
import subprocess
import threading
import random
import numpy
import linecache
from collections import defaultdict
from opponent_model import OpponentModel
from match_state import MatchState
from poker_point import PokerPoint
from poker_config import PokerConfig
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

        t1 = threading.Thread(target=PokerEnvironment.execute_player, args=[team, opponent, point, sbb_port, is_training, True, 'all'])
        t2 = threading.Thread(target=PokerEnvironment.execute_player, args=[opponent, team, point, opponent_port, False, False, opponent_use_inputs])
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
        else:
            sbb_position = 1
        normalized_value = PokerEnvironment.normalize_winning(float(scores[sbb_position]))
        if not is_training:
            if mode == Config.RESTRICTIONS['mode']['validation']:
                self._update_team_extra_metrics_for_poker(team, point, normalized_value, 'validation')
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
        point.last_opponent_ = opponent.__repr__()

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

    def calculate_poker_metrics_per_generation(self, run_info, current_generation):
        if run_info.balanced_point_population is None:
            current_subsets_per_class = self._get_data_per_label(self.point_population_)
            array = [len(a) for a in current_subsets_per_class]
            if array.count(array[0]) == len(array):
                run_info.balanced_point_population = current_generation

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
                        sorting_criteria_per_label = lambda x: x.extra_metrics_['validation_points'][subdivision][label]
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

    @staticmethod
    def normalize_winning(value):
        max_small_bet_turn_winning = PokerConfig.CONFIG['small_bet']*4
        max_big_bet_turn_winning = PokerConfig.CONFIG['big_bet']*4
        max_winning = max_small_bet_turn_winning*2 + max_big_bet_turn_winning*2
        max_losing = -max_winning
        return (value - max_losing)/float(max_winning - max_losing)

    @staticmethod
    def execute_player(player, opponent, point, port, is_training, is_sbb, inputs_type):
        if is_sbb and not is_training:
            player.extra_metrics_['played_last_hand'] = True

        socket_tmp = socket.socket()

        total = 100
        attempt = 0
        while True:
            try:
                socket_tmp.connect(("localhost", port))
                break
            except socket_error as e:
                attempt += 1
                if e.errno == errno.ECONNREFUSED:
                    time.sleep(1)
                if attempt > total:
                    raise ValueError("Could not connect to port "+str(port))

        debug_file = None
        if Config.USER['reinforcement_parameters']['debug_matches']:
            debug_file = open(PokerConfig.CONFIG['acpc_path']+'outputs/player'+str(port)+'.log','w')
            print player.__repr__()+": started"
        socket_tmp.send("VERSION:2.0.0\r\n")
        previous_action = None
        partial_messages = []
        previous_messages = None
        player.initialize(point.seed_) # so a probabilistic opponent will always play equal for the same hands and actions
        while True:
            try:
                message = socket_tmp.recv(1000)
            except socket_error as e:
                if e.errno == errno.ECONNRESET:
                    break
                else:
                    raise e
            if not message:
                break
            message = message.replace("\r\n", "")
            previous_messages = list(partial_messages)
            partial_messages = message.split("MATCHSTATE")
            last_message = partial_messages[-1] # only cares about the last message sent (ie. the one where this player should act)
            match_state = MatchState(last_message, PokerConfig.CONFIG['small_bet'], PokerConfig.CONFIG['big_bet'])
            if match_state.is_showdown():
                previous_action = None
                if Config.USER['reinforcement_parameters']['debug_matches']:
                    debug_file.write("showdown\n")
                    print player.__repr__()+":showdown\n\n"
            elif match_state.is_current_player_to_act():
                if match_state.is_last_action_a_fold():
                    previous_action = None
                    if Config.USER['reinforcement_parameters']['debug_matches']:
                        debug_file.write("opponent folded\n")
                        print player.__repr__()+":opponent folded\n\n"
                else:
                    if inputs_type:
                        if inputs_type == 'all':
                            if is_sbb:
                                point_inputs = point.inputs(len(match_state.rounds))
                            else:
                                point_inputs = point.inputs_for_opponent(len(match_state.rounds))
                            chips = PokerEnvironment._calculate_chips_input(player, opponent)
                            inputs = point_inputs + match_state.inputs() + [chips] + PokerEnvironment.get_opponent_model(player, opponent).inputs(match_state)
                        elif inputs_type == 'rule_based_opponent':
                            inputs = []
                            inputs.append(point.hand_strength_[len(match_state.rounds)-1])
                            inputs.append(match_state.calculate_bet()*Config.RESTRICTIONS['multiply_normalization_by'])
                    else:
                        inputs = []
                    action = player.execute(point.point_id_, inputs, match_state.valid_actions(), is_training)
                    if action is None:
                        action = 1
                    if is_sbb and is_training:
                        player.action_sequence_.append(str(action))
                    if is_sbb and not is_training:
                        if len(match_state.rounds) == 1 and len(match_state.rounds[0]) < 2 and action == 0: # first action of first round is a fold
                            player.extra_metrics_['played_last_hand'] = False
                    action = PokerConfig.CONFIG['action_mapping'][action]
                    previous_action = action
                    send_msg = "MATCHSTATE"+last_message+":"+action+"\r\n"
                    try:
                        socket_tmp.send(send_msg)
                    except socket_error as e:
                        if e.errno == errno.ECONNRESET:
                            break
                    if Config.USER['reinforcement_parameters']['debug_matches']:
                        debug_file.write("match_state: "+str(match_state)+"\n\n")
                        debug_file.write("inputs: "+str(inputs)+"\n\n")
                        debug_file.write("send_msg: "+str(send_msg)+"\n\n")
                        print player.__repr__()+":match_state: "+str(match_state)+"\n"
                        print player.__repr__()+":inputs: "+str(inputs)+"\n"
                        print player.__repr__()+":send_msg: "+str(send_msg)+"\n"
            else:
                if not previous_action == 'f':
                    previous_action = None
                if Config.USER['reinforcement_parameters']['debug_matches']:
                    debug_file.write("nothing to do\n\n")
                    print player.__repr__()+":nothing to do\n"
        socket_tmp.close()

        if inputs_type and inputs_type == 'all':
            PokerEnvironment._update_opponent_model_and_chips(player, opponent, point, previous_messages+partial_messages, debug_file, previous_action)

        if Config.USER['reinforcement_parameters']['debug_matches']:
            debug_file.write("The end.\n\n")
            print player.__repr__()+": The end.\n"
            debug_file.close()

    @staticmethod
    def _calculate_chips_input(player, opponent):
        chips = PokerEnvironment.get_chips(player, opponent)
        if len(chips) == 0:
            chips = 0.5
        else:
            chips = PokerEnvironment.normalize_winning(numpy.mean(chips))
        chips = chips*Config.RESTRICTIONS['multiply_normalization_by']
        return chips

    @staticmethod
    def get_chips(player, opponent):
        opponent_id = PokerEnvironment.get_opponent_id(opponent)
        if opponent_id not in player.chips:
            player.chips[opponent_id] = []
        return player.chips[opponent_id]

    @staticmethod
    def get_opponent_model(player, opponent):
        opponent_id = PokerEnvironment.get_opponent_id(opponent)
        if opponent_id not in player.opponent_model:
            player.opponent_model[opponent_id] = OpponentModel()
        return player.opponent_model[opponent_id]

    @staticmethod
    def get_opponent_id(opponent):
        if opponent.opponent_id == "hall_of_fame" or opponent.opponent_id == "sbb":
            opponent_id = opponent.team_id_
        else:
            opponent_id = opponent.opponent_id
        return opponent_id

    @staticmethod
    def _update_opponent_model_and_chips(player, opponent, point, messages, debug_file, previous_action):
        for partial_msg in reversed(messages):
            if partial_msg:
                partial_match_state = MatchState(partial_msg, PokerConfig.CONFIG['small_bet'], PokerConfig.CONFIG['big_bet'])
                self_actions, opponent_actions = partial_match_state.actions_per_player()
                if partial_match_state.is_showdown():
                    if Config.USER['reinforcement_parameters']['debug_matches']:
                        debug_file.write("partial_msg: "+str(partial_msg)+", previous_action: "+str(previous_action)+"\n\n")
                        print player.__repr__()+": partial_msg: "+str(partial_msg)+", previous_action: "+str(previous_action)+"\n"
                    self_folded = False
                    opponent_folded = False
                    winner = point.winner_of_showdown()
                    if Config.USER['reinforcement_parameters']['debug_matches'] and winner is None:
                        debug_file.write("showdown, draw\n\n")
                        print player.__repr__()+": showdown, draw\n"
                    else:
                        if winner == partial_match_state.position:
                            if Config.USER['reinforcement_parameters']['debug_matches']:
                                debug_file.write("showdown, I won\n\n")
                                print player.__repr__()+": showdown, I won\n"
                            PokerEnvironment.get_chips(player, opponent).append(+(partial_match_state.calculate_pot()))
                        else:
                            if Config.USER['reinforcement_parameters']['debug_matches']:
                                debug_file.write("showdown, I lost\n\n")
                                print player.__repr__()+": showdown, I lost\n"
                            PokerEnvironment.get_chips(player, opponent).append(-(partial_match_state.calculate_pot()))
                else:
                    last_player = partial_match_state.last_player_to_act()
                    if last_player == partial_match_state.position:
                        if self_actions and self_actions[-1] == 'f':
                            if Config.USER['reinforcement_parameters']['debug_matches']:
                                debug_file.write("partial_msg: "+str(partial_msg)+", I folded\n\n")
                                print player.__repr__()+": partial_msg: "+str(partial_msg)+", I folded\n"
                            self_folded = True
                            opponent_folded = False
                            PokerEnvironment.get_chips(player, opponent).append(-(partial_match_state.calculate_pot()))
                    elif opponent_actions and opponent_actions[-1] == 'f':
                        if Config.USER['reinforcement_parameters']['debug_matches']:
                            debug_file.write("partial_msg: "+str(partial_msg)+", opponent folded\n\n")
                            print player.__repr__()+": partial_msg: "+str(partial_msg)+", opponent folded\n"
                        self_folded = False
                        opponent_folded = True
                        PokerEnvironment.get_chips(player, opponent).append(+(partial_match_state.calculate_pot()))
                    else:
                        raise ValueError("An unexpected behavior occured during the poker match!")
                PokerEnvironment.get_opponent_model(player, opponent).update_overall_agressiveness(len(partial_match_state.rounds), self_actions, opponent_actions, self_folded, opponent_folded, previous_action)
                break