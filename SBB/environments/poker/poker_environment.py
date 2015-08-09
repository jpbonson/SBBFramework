import sys
import gc
import math
import errno
import yappi
import socket
import itertools
import time
from socket import error as socket_error
import os
import subprocess
import threading
import random
import numpy
from collections import defaultdict
from opponent_model import OpponentModel
from match_state import MatchState
from poker_point import PokerPoint
from poker_config import PokerConfig
from poker_opponents import PokerRandomOpponent, PokerAlwaysFoldOpponent, PokerAlwaysCallOpponent, PokerAlwaysRaiseOpponent
from tables.normalized_equity_table import NORMALIZED_HAND_EQUITY
from ..reinforcement_environment import ReinforcementEnvironment
from ...utils.helpers import avaliable_ports, round_value, flatten
from ...config import Config

class PokerEnvironment(ReinforcementEnvironment):
    """
    This environment encapsulates all methods to deal with a reinforcement learning task for TicTacToe.
    """

    def __init__(self):
        total_actions = 3 # fold, call, raise
        total_inputs = len(PokerConfig.INPUTS)
        total_labels = len(PokerConfig.CONFIG['hand_equity_labels'].keys())
        coded_opponents_for_training = [PokerAlwaysCallOpponent, PokerAlwaysRaiseOpponent]
        coded_opponents_for_validation = [PokerAlwaysCallOpponent, PokerAlwaysRaiseOpponent]
        point_class = PokerPoint
        super(PokerEnvironment, self).__init__(total_actions, total_inputs, total_labels, coded_opponents_for_training, coded_opponents_for_validation, point_class)
        port1, port2 = avaliable_ports()
        PokerConfig.CONFIG['available_ports'] = [port1, port2]
        PokerConfig.full_deck = self._initialize_deck()

    def _play_match(self, team, opponent, point, mode):
        """

        """
        if mode == Config.RESTRICTIONS['mode']['training']:
            is_training = True
        else:
            is_training = False

        if Config.USER['reinforcement_parameters']['debug_matches'] and not os.path.exists(PokerConfig.CONFIG['acpc_path']+"outputs/"):
            os.makedirs(PokerConfig.CONFIG['acpc_path']+"outputs/")

        # if mode == Config.RESTRICTIONS['mode']['champion']:
        #     # because it wastes too much memmory to save the values for the champion
        #     memories = ({}, {}, {})
        # else:
        memories = (PokerConfig.HAND_STRENGHT_MEMORY[point.point_id_], 
            PokerConfig.HAND_PPOTENTIAL_MEMORY[point.point_id_], 
            PokerConfig.HAND_NPOTENTIAL_MEMORY[point.point_id_])

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

        opponent_use_inputs = False
        if opponent.opponent_id == "hall_of_fame":
            opponent_use_inputs = True

        t1 = threading.Thread(target=PokerEnvironment.execute_player, args=[team, opponent, point, sbb_port, is_training, True, True, memories])
        t2 = threading.Thread(target=PokerEnvironment.execute_player, args=[opponent, team, point, opponent_port, False, False, opponent_use_inputs, memories])
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
                team.extra_metrics_['total_hands']['validation'] += 1
                team.extra_metrics_['total_hands_per_point_type']['validation']['position'][point.position_] += 1
                team.extra_metrics_['total_hands_per_point_type']['validation']['sbb_equity'][point.label_] += 1
                team.extra_metrics_['total_hands_per_point_type']['validation']['sbb_strength'][point.sbb_strength_label_] += 1
            else:
                team.extra_metrics_['total_hands']['champion'] += 1
                team.extra_metrics_['total_hands_per_point_type']['champion']['position'][point.position_] += 1
                team.extra_metrics_['total_hands_per_point_type']['champion']['sbb_equity'][point.label_] += 1
                team.extra_metrics_['total_hands_per_point_type']['champion']['sbb_strength'][point.sbb_strength_label_] += 1
            if team.extra_metrics_['played_last_hand']:
                if mode == Config.RESTRICTIONS['mode']['validation']:
                    team.extra_metrics_['hand_played']['validation'] += 1
                    team.extra_metrics_['hand_played_per_point_type']['validation']['position'][point.position_] += 1
                    team.extra_metrics_['hand_played_per_point_type']['validation']['sbb_equity'][point.label_] += 1
                    team.extra_metrics_['hand_played_per_point_type']['validation']['sbb_strength'][point.sbb_strength_label_] += 1
                else:
                    team.extra_metrics_['hand_played']['champion'] += 1
                    team.extra_metrics_['hand_played_per_point_type']['champion']['position'][point.position_] += 1
                    team.extra_metrics_['hand_played_per_point_type']['champion']['sbb_equity'][point.label_] += 1
                    team.extra_metrics_['hand_played_per_point_type']['champion']['sbb_strength'][point.sbb_strength_label_] += 1
            if team.extra_metrics_['played_last_hand'] and normalized_value > 0.5:
                if mode == Config.RESTRICTIONS['mode']['validation']:
                    team.extra_metrics_['won_hands']['validation'] += 1
                    team.extra_metrics_['won_hands_per_point_type']['validation']['position'][point.position_] += 1
                    team.extra_metrics_['won_hands_per_point_type']['validation']['sbb_equity'][point.label_] += 1
                    team.extra_metrics_['won_hands_per_point_type']['validation']['sbb_strength'][point.sbb_strength_label_] += 1
                else:
                    team.extra_metrics_['won_hands']['champion'] += 1
                    team.extra_metrics_['won_hands_per_point_type']['champion']['position'][point.position_] += 1
                    team.extra_metrics_['won_hands_per_point_type']['champion']['sbb_equity'][point.label_] += 1
                    team.extra_metrics_['won_hands_per_point_type']['champion']['sbb_strength'][point.sbb_strength_label_] += 1

        if Config.USER['reinforcement_parameters']['debug_matches']:
            print "scores: "+str(scores)
            print "players: "+str(players)
            print "normalized_value: "+str(normalized_value)

        point.teams_results_.append(normalized_value)
        point.last_opponent_ = opponent.__repr__()

        return normalized_value

    def reset(self):
        PokerConfig.HAND_STRENGHT_MEMORY = defaultdict(dict)
        PokerConfig.HAND_PPOTENTIAL_MEMORY = defaultdict(dict)
        PokerConfig.HAND_NPOTENTIAL_MEMORY = defaultdict(dict)
        super(PokerEnvironment, self).reset()
        PokerConfig.hole_cards_based_on_equity = self._initialize_hole_cards_based_on_equity()
        gc.collect()
        yappi.clear_stats()

    def setup(self, teams_population):
        super(PokerEnvironment, self).setup(teams_population)
        if Config.USER['reinforcement_parameters']['hall_of_fame']['enabled']:
            for opponent in self.opponent_population_['hall_of_fame']:
                opponent.opponent_model = {}
                opponent.chips = {}
        for point in self.point_population():
            point.teams_results_ = []
        gc.collect()
        yappi.clear_stats()

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

    def validate(self, current_generation, teams_population):
        keys = ['validation', 'champion']
        subkeys = ['position', 'sbb_equity', 'sbb_strength']
        for team in teams_population:
            if team.generation != current_generation:
                team.extra_metrics_['total_hands'] = {}
                team.extra_metrics_['hand_played'] = {}
                team.extra_metrics_['won_hands'] = {}
                team.extra_metrics_['total_hands_per_point_type'] = {}
                team.extra_metrics_['hand_played_per_point_type'] = {}
                team.extra_metrics_['won_hands_per_point_type'] = {}
                for key in keys:
                    team.extra_metrics_['total_hands'][key] = 0
                    team.extra_metrics_['hand_played'][key] = 0
                    team.extra_metrics_['won_hands'][key] = 0
                    team.extra_metrics_['total_hands_per_point_type'][key] = {}
                    team.extra_metrics_['hand_played_per_point_type'][key] = {}
                    team.extra_metrics_['won_hands_per_point_type'][key] = {}
                    for subkey in subkeys:
                        team.extra_metrics_['total_hands_per_point_type'][key][subkey] = defaultdict(int)
                        team.extra_metrics_['hand_played_per_point_type'][key][subkey] = defaultdict(int)
                        team.extra_metrics_['won_hands_per_point_type'][key][subkey] = defaultdict(int)

        if Config.USER['reinforcement_parameters']['hall_of_fame']['enabled']: # initializing
            for opponent in self.opponent_population_['hall_of_fame']:
                opponent.opponent_model = {}
                opponent.chips = {}

        for point in self.validation_population():
            point.teams_results_ = []

        best_team = super(PokerEnvironment, self).validate(current_generation, teams_population)
        return best_team

    def metrics(self):
        msg = ""
        msg += "\n### Environment Info:"
        msg += "\nports: "+str(PokerConfig.CONFIG['available_ports'])
        msg += "\ntotal inputs: "+str(self.total_inputs_)
        msg += "\ninputs: "+str(PokerConfig.INPUTS)
        msg += "\ntotal actions: "+str(self.total_actions_)
        msg += "\nactions mapping: "+str(PokerConfig.ACTION_MAPPING)
        msg += "\npositions: "+str(PokerConfig.CONFIG['positions'])
        msg += "\ntraining opponents: "+str([c.__name__ for c in self.coded_opponents_for_training_])
        msg += "\nvalidation opponents: "+str([c.__name__ for c in self.coded_opponents_for_validation_])
        if Config.USER['reinforcement_parameters']['hall_of_fame']['enabled']:
            msg += "\nhall of fame size: "+str(Config.USER['reinforcement_parameters']['hall_of_fame']['size'])
        return msg

    def _initialize_deck(self):
        deck = []
        for rank in PokerConfig.RANKS:
            for suit in PokerConfig.SUITS:
                deck.append(rank+suit)
        return deck

    def _initialize_hole_cards_based_on_equity(self):
        deck = self._initialize_deck()
        hole_cards = list(itertools.combinations(deck, 2))
        equities = []
        for card1, card2 in hole_cards:
            equities.append(NORMALIZED_HAND_EQUITY[frozenset([card1, card2])])
        total_equities = sum(equities)
        probabilities = [e/float(total_equities) for e in equities]
        hole_cards_indices = numpy.random.choice(range(len(hole_cards)), size = int(len(hole_cards)*0.3), replace = False, p = probabilities)
        final_cards = []
        for index in hole_cards_indices:
            final_cards.append(hole_cards[index])
        return final_cards

    def _remove_points(self, points_to_remove, teams_population):
        super(PokerEnvironment, self)._remove_points(points_to_remove, teams_population)
        for point in points_to_remove:
            del PokerConfig.HAND_STRENGHT_MEMORY[point.point_id_]
            del PokerConfig.HAND_PPOTENTIAL_MEMORY[point.point_id_]
            del PokerConfig.HAND_NPOTENTIAL_MEMORY[point.point_id_]

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
        self._calculate_point_population_metric_per_validation(run_info, lambda x: x.label_, 'sbb_hole_card_equity', PokerConfig.CONFIG['hand_equity_labels'].keys())
        self._calculate_point_population_metric_per_validation(run_info, lambda x: x.opponent_label_, 'opp_hole_card_equity', PokerConfig.CONFIG['hand_equity_labels'].keys())
        self._calculate_point_population_metric_per_validation(run_info, lambda x: x.sbb_strength_label_, 'sbb_hole_card_strength', PokerConfig.CONFIG['hand_strength_labels'].keys())
        self._calculate_point_population_metric_per_validation(run_info, lambda x: x.opponent_strength_label_, 'opp_hole_card_strength', PokerConfig.CONFIG['hand_strength_labels'].keys())

    def _calculate_point_population_metric_per_validation(self, run_info, get_attribute, key, labels):
        for label in labels:
            total = len([point for point in self.point_population() if get_attribute(point) == label])
            if label not in run_info.point_population_distribution_per_validation[key]:
                run_info.point_population_distribution_per_validation[key][label] = []
            run_info.point_population_distribution_per_validation[key][label].append(total)

    def _calculate_validation_population_metrics_per_validation(self, run_info):
        self._calculate_validation_population_metric_per_validation(run_info, lambda x: x.position_, 'position', range(PokerConfig.CONFIG['positions']))
        self._calculate_validation_population_metric_per_validation(run_info, lambda x: x.label_, 'sbb_hole_card_equity', PokerConfig.CONFIG['hand_equity_labels'].keys())
        self._calculate_validation_population_metric_per_validation(run_info, lambda x: x.opponent_label_, 'opp_hole_card_equity', PokerConfig.CONFIG['hand_equity_labels'].keys())
        self._calculate_validation_population_metric_per_validation(run_info, lambda x: x.sbb_strength_label_, 'sbb_hole_card_strength', PokerConfig.CONFIG['hand_strength_labels'].keys())
        self._calculate_validation_population_metric_per_validation(run_info, lambda x: x.opponent_strength_label_, 'opp_hole_card_strength', PokerConfig.CONFIG['hand_strength_labels'].keys())

    def _calculate_validation_population_metric_per_validation(self, run_info, get_attribute, key, labels):
        point_per_distribution = {}
        for label in labels:
            point_per_distribution[label] = [point for point in self.validation_population() if get_attribute(point) == label]
        run_info.validation_population_distribution_per_validation[key] = {}
        for label in labels:
            run_info.validation_population_distribution_per_validation[key][label] = len(point_per_distribution[label])

        for label in labels:
            means_per_position = round_value(numpy.mean(flatten([point.teams_results_ for point in point_per_distribution[label]])))
            if label not in run_info.global_result_per_validation[key]:
                run_info.global_result_per_validation[key][label] = []
            run_info.global_result_per_validation[key][label].append(means_per_position)

        point_per_distribution = {}
        for label in labels:
            point_per_distribution[label] = [point for point in self.champion_population() if get_attribute(point) == label]
        run_info.champion_population_distribution_per_validation[key] = {}
        for label in labels:
            run_info.champion_population_distribution_per_validation[key][label] = len(point_per_distribution[label])

    @staticmethod
    def normalize_winning(value):
        max_small_bet_turn_winning = PokerConfig.CONFIG['small_bet']*4
        max_big_bet_turn_winning = PokerConfig.CONFIG['big_bet']*4
        max_winning = max_small_bet_turn_winning*2 + max_big_bet_turn_winning*2
        max_losing = -max_winning
        return (value - max_losing)/float(max_winning - max_losing)

    @staticmethod
    def execute_player(player, opponent, point, port, is_training, is_sbb, use_inputs, memories):
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
            match_state = MatchState(last_message, PokerConfig.CONFIG['small_bet'], PokerConfig.CONFIG['big_bet'], PokerConfig.full_deck, PokerConfig.hole_cards_based_on_equity)
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
                    if use_inputs:
                        chips = PokerEnvironment.get_chips(player, opponent)
                        if len(chips) == 0:
                            chips = 0.5
                        else:
                            chips = PokerEnvironment.normalize_winning(numpy.mean(chips))
                        inputs = match_state.inputs(memories) + [chips] + PokerEnvironment.get_opponent_model(player, opponent).inputs(match_state)
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
                    action = PokerConfig.ACTION_MAPPING[action]
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

        if use_inputs:
            PokerEnvironment.update_opponent_model_and_chips(player, opponent, previous_messages+partial_messages, debug_file, previous_action)

        if Config.USER['reinforcement_parameters']['debug_matches']:
            debug_file.write("The end.\n\n")
            print player.__repr__()+": The end.\n"
            debug_file.close()

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
    def update_opponent_model_and_chips(player, opponent, messages, debug_file, previous_action):
        for partial_msg in reversed(messages):
            if partial_msg:
                partial_match_state = MatchState(partial_msg, PokerConfig.CONFIG['small_bet'], PokerConfig.CONFIG['big_bet'], PokerConfig.full_deck, PokerConfig.hole_cards_based_on_equity)
                self_actions, opponent_actions = partial_match_state.actions_per_player()
                if partial_match_state.is_showdown():
                    if Config.USER['reinforcement_parameters']['debug_matches']:
                        debug_file.write("partial_msg: "+str(partial_msg)+", previous_action: "+str(previous_action)+"\n\n")
                        print player.__repr__()+": partial_msg: "+str(partial_msg)+", previous_action: "+str(previous_action)+"\n"
                    self_folded = False
                    opponent_folded = False
                    winner = partial_match_state.get_winner_of_showdown()
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
                                debug_file.write("partial_msg: "+str(partial_msg)+", I folded (1)\n\n")
                                print player.__repr__()+": partial_msg: "+str(partial_msg)+", I folded (1)\n"
                            self_folded = True
                            opponent_folded = False
                            PokerEnvironment.get_chips(player, opponent).append(-(partial_match_state.calculate_pot()))
                    elif opponent_actions and opponent_actions[-1] == 'f':
                        if Config.USER['reinforcement_parameters']['debug_matches']:
                            debug_file.write("partial_msg: "+str(partial_msg)+", opponent folded (1)\n\n")
                            print player.__repr__()+": partial_msg: "+str(partial_msg)+", opponent folded (1)\n"
                        self_folded = False
                        opponent_folded = True
                        PokerEnvironment.get_chips(player, opponent).append(+(partial_match_state.calculate_pot()))
                    elif previous_action == 'f':
                        print "Warning! (1)"
                        if Config.USER['reinforcement_parameters']['debug_matches']:
                            debug_file.write("partial_msg: "+str(partial_msg)+", I folded (2)\n\n")
                            print player.__repr__()+": partial_msg: "+str(partial_msg)+", I folded (2)\n"
                        self_folded = True
                        opponent_folded = False
                        PokerEnvironment.get_chips(player, opponent).append(-(partial_match_state.calculate_pot()))
                    else:
                        print "Warning! (2)"
                        if Config.USER['reinforcement_parameters']['debug_matches']:
                            debug_file.write("partial_msg: "+str(partial_msg)+", opponent folded (2)\n\n")
                            print player.__repr__()+": partial_msg: "+str(partial_msg)+", opponent folded (2)\n"
                        self_folded = False
                        opponent_folded = True
                        PokerEnvironment.get_chips(player, opponent).append(+(partial_match_state.calculate_pot()))
                PokerEnvironment.get_opponent_model(player, opponent).update_overall_agressiveness(len(partial_match_state.rounds), self_actions, opponent_actions, self_folded, opponent_folded, previous_action)
                break