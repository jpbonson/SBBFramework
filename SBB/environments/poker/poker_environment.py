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
from tables.strenght_table_for_2cards import STRENGTH_TABLE_FOR_2_CARDS
from poker_opponents import PokerRandomOpponent, PokerAlwaysFoldOpponent, PokerAlwaysCallOpponent, PokerAlwaysRaiseOpponent
from ..reinforcement_environment import ReinforcementEnvironment, ReinforcementPoint
from ...utils.helpers import avaliable_ports
from ...config import Config

class PokerPoint(ReinforcementPoint):
    """
    Encapsulates a poker opponent, seeded hand, and position as a point.
    """

    def __init__(self, point_id, opponent):
        self.seed_ = random.randint(0, Config.RESTRICTIONS['max_seed'])
        self.position_ = random.randint(0, PokerEnvironment.CONFIG['positions']-1)
        point_id = "("+str(point_id)+","+str(self.seed_)+")"
        super(PokerPoint, self).__init__(point_id, opponent)
        self.sbb_hole_cards = None
        self.opponent_hole_cards = None
        self.board_cards = None

    def update_metrics(self):
        if self.sbb_hole_cards:
            self.sbb_2card_strength = STRENGTH_TABLE_FOR_2_CARDS[frozenset(self.sbb_hole_cards)]
        if self.opponent_hole_cards:
            self.opponent_2card_strength = STRENGTH_TABLE_FOR_2_CARDS[frozenset(self.opponent_hole_cards)]
        if self.board_cards:
            if self.sbb_hole_cards:
                self.sbb_5card_strength = MatchState.calculate_hand_strength(self.sbb_hole_cards, self.board_cards, PokerEnvironment.full_deck, {})
            if self.opponent_hole_cards:
                self.opponent_5card_strength = MatchState.calculate_hand_strength(self.opponent_hole_cards, self.board_cards, PokerEnvironment.full_deck, {})

    def __str__(self):
        msg = str(self.opponent)+","+str(self.position_)+","+str(self.seed_)
        extra = "empty"
        if self.board_cards:
            extra = str(self.sbb_hole_cards)+","+str(self.opponent_hole_cards)+","+str(self.board_cards)
            extra += ": "+str(self.sbb_2card_strength)+","+str(self.opponent_2card_strength)+","+str(self.sbb_5card_strength)+","+str(self.opponent_5card_strength)
        return "<"+msg+": "+extra+">"

    def __repr__(self):
        msg = str(self.opponent)+","+str(self.position_)+","+str(self.seed_)
        extra = "empty"
        if self.board_cards:
            extra = str(self.sbb_hole_cards)+","+str(self.opponent_hole_cards)+","+str(self.board_cards)
            extra += ": "+str(self.sbb_2card_strength)+","+str(self.opponent_2card_strength)+","+str(self.sbb_5card_strength)+","+str(self.opponent_5card_strength)
        return "<"+msg+": "+extra+">"

class PokerEnvironment(ReinforcementEnvironment):
    """
    This environment encapsulates all methods to deal with a reinforcement learning task for TicTacToe.
    """

    ACTION_MAPPING = {0: 'f', 1: 'c', 2: 'r'}
    INPUTS = MatchState.INPUTS+['chips']+OpponentModel.INPUTS
    RANKS = ['2', '3', '4', '5', '6', '7', '8', '9', 'T', 'J', 'Q', 'K', 'A']
    SUITS = ['s', 'd', 'h', 'c']
    HAND_STRENGHT_MEMORY = None
    HAND_PPOTENTIAL_MEMORY = None
    HAND_NPOTENTIAL_MEMORY = None
    CONFIG = {
        'acpc_path': "SBB/environments/poker/ACPC/",
        'available_ports': [],
        'small_bet': 10,
        'big_bet': 20,
        'positions': 2,
    }

    def __init__(self):
        total_actions = 3 # fold, call, raise
        total_inputs = len(PokerEnvironment.INPUTS)
        coded_opponents_for_training = [PokerAlwaysFoldOpponent, PokerAlwaysCallOpponent, PokerAlwaysRaiseOpponent]
        coded_opponents_for_validation = [PokerAlwaysFoldOpponent, PokerAlwaysCallOpponent, PokerAlwaysRaiseOpponent]
        super(PokerEnvironment, self).__init__(total_actions, total_inputs, coded_opponents_for_training, coded_opponents_for_validation)
        port1, port2 = avaliable_ports()
        PokerEnvironment.CONFIG['available_ports'] = [port1, port2]

    def _instantiate_point_for_coded_opponent_class(self, opponent_class):
        instance = opponent_class()
        return PokerPoint(str(instance), instance)

    def _instantiate_point_for_sbb_opponent(self, team, opponent_id):
        point = PokerPoint(team.__repr__(), team)
        point.opponent.opponent_id = opponent_id
        return point

    def _play_match(self, team, point, mode):
        """

        """
        if mode == Config.RESTRICTIONS['mode']['training']:
            is_training = True
        else:
            is_training = False

        if Config.USER['reinforcement_parameters']['debug_matches'] and not os.path.exists(PokerEnvironment.CONFIG['acpc_path']+"outputs/"):
            os.makedirs(PokerEnvironment.CONFIG['acpc_path']+"outputs/")

        if Config.USER['reinforcement_parameters']['balanced_opponent_populations']:
            memories = (PokerEnvironment.HAND_STRENGHT_MEMORY[point.point_id], 
                PokerEnvironment.HAND_PPOTENTIAL_MEMORY[point.point_id], 
                PokerEnvironment.HAND_NPOTENTIAL_MEMORY[point.point_id])
        else:
            if is_training:
                if self.current_population_ != 'sbb':
                    memories = (PokerEnvironment.HAND_STRENGHT_MEMORY[self.current_population_][point.point_id], 
                        PokerEnvironment.HAND_PPOTENTIAL_MEMORY[self.current_population_][point.point_id], 
                        PokerEnvironment.HAND_NPOTENTIAL_MEMORY[self.current_population_][point.point_id])
                else:
                    memories = ({}, {}, {})
            else:
                memories = (PokerEnvironment.HAND_STRENGHT_MEMORY['validation'][point.point_id], 
                    PokerEnvironment.HAND_PPOTENTIAL_MEMORY['validation'][point.point_id], 
                    PokerEnvironment.HAND_NPOTENTIAL_MEMORY['validation'][point.point_id])

        if point.position_ == 0:
            port1 = PokerEnvironment.CONFIG['available_ports'][0]
            port2 = PokerEnvironment.CONFIG['available_ports'][1]
        else:
            port1 = PokerEnvironment.CONFIG['available_ports'][1]
            port2 = PokerEnvironment.CONFIG['available_ports'][0]

        t1 = threading.Thread(target=PokerEnvironment.execute_player, args=[team, port1, point, is_training, True, memories])
        t2 = threading.Thread(target=PokerEnvironment.execute_player, args=[point.opponent, port2, point, False, False, memories])
        args = [PokerEnvironment.CONFIG['acpc_path']+'dealer', 
                PokerEnvironment.CONFIG['acpc_path']+'outputs/match_output', 
                PokerEnvironment.CONFIG['acpc_path']+'holdem.limit.2p.reverse_blinds.game', 
                "1", # total hands 
                str(point.seed_),
                'sbb', 'opponent', 
                '-p', str(PokerEnvironment.CONFIG['available_ports'][0])+","+str(PokerEnvironment.CONFIG['available_ports'][1])]
        if not Config.USER['reinforcement_parameters']['debug_matches']:
            args.append('-l')
        p = subprocess.Popen(args, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        t1.start()
        t2.start()
        out, err = p.communicate()
        t1.join()
        t2.join()

        if Config.USER['reinforcement_parameters']['debug_matches']:
            with open(PokerEnvironment.CONFIG['acpc_path']+"outputs/match.log", "w") as text_file:
                text_file.write(str(err))
        score = out.split("\n")[1]
        score = score.replace("SCORE:", "")
        splitted_score = score.split(":")
        scores = splitted_score[0].split("|")
        players = splitted_score[1].split("|")
        if players[0] != 'sbb':
            print "\nbug!\n"
            raise SystemExit
        normalized_value = PokerEnvironment.normalize_winning(float(scores[0]))
        if not is_training:
            if mode == Config.RESTRICTIONS['mode']['validation']:
                team.extra_metrics_['total_hands_validation'] += 1
            else:
                team.extra_metrics_['total_hands_champion'] += 1
            if team.extra_metrics_['played_last_hand']:
                if mode == Config.RESTRICTIONS['mode']['validation']:
                    team.extra_metrics_['hand_played_validation'] += 1
                else:
                    team.extra_metrics_['hand_played_champion'] += 1
            if team.extra_metrics_['played_last_hand'] and normalized_value > 0.5:
                if mode == Config.RESTRICTIONS['mode']['validation']:
                    team.extra_metrics_['won_hands_validation'] += 1
                else:
                    team.extra_metrics_['won_hands_champion'] += 1
        if Config.USER['reinforcement_parameters']['debug_matches']:
            print "scores: "+str(scores)
            print "players: "+str(players)
            print "avg score: "+str(avg_score)
            print "normalized_value: "+str(normalized_value)
        return normalized_value

    def reset(self):
        PokerEnvironment.HAND_STRENGHT_MEMORY = defaultdict(dict)
        PokerEnvironment.HAND_PPOTENTIAL_MEMORY = defaultdict(dict)
        PokerEnvironment.HAND_NPOTENTIAL_MEMORY = defaultdict(dict)
        if not Config.USER['reinforcement_parameters']['balanced_opponent_populations']:
            for key in self.point_population_per_opponent_.keys():
                PokerEnvironment.HAND_STRENGHT_MEMORY[key] = defaultdict(dict)
                PokerEnvironment.HAND_PPOTENTIAL_MEMORY[key] = defaultdict(dict)
                PokerEnvironment.HAND_NPOTENTIAL_MEMORY[key] = defaultdict(dict)
            PokerEnvironment.HAND_STRENGHT_MEMORY['validation'] = defaultdict(dict)
            PokerEnvironment.HAND_PPOTENTIAL_MEMORY['validation'] = defaultdict(dict)
            PokerEnvironment.HAND_NPOTENTIAL_MEMORY['validation'] = defaultdict(dict)
        super(PokerEnvironment, self).reset()
        PokerEnvironment.full_deck = self._initialize_deck()
        PokerEnvironment.hand_strength_hole_cards = self._initialize_hole_cards_based_on_hand_strength()
        gc.collect()
        yappi.clear_stats()

    def setup(self, teams_population):
        super(PokerEnvironment, self).setup(teams_population)
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
        for team in teams_population:
            if team.generation != current_generation:
                team.extra_metrics_['total_hands_validation'] = 0
                team.extra_metrics_['total_hands_champion'] = 0
                team.extra_metrics_['hand_played_validation'] = 0
                team.extra_metrics_['hand_played_champion'] = 0
                team.extra_metrics_['won_hands_validation'] = 0
                team.extra_metrics_['won_hands_champion'] = 0
        best_team = super(PokerEnvironment, self).validate(current_generation, teams_population)
        return best_team

    def metrics(self):
        msg = ""
        msg += "\n### Environment Info:"
        msg += "\nports: "+str(PokerEnvironment.CONFIG['available_ports'])
        msg += "\ntotal inputs: "+str(self.total_inputs_)
        msg += "\ninputs: "+str(PokerEnvironment.INPUTS)
        msg += "\ntotal actions: "+str(self.total_actions_)
        msg += "\nactions mapping: "+str(PokerEnvironment.ACTION_MAPPING)
        msg += "\npositions: "+str(PokerEnvironment.CONFIG['positions'])
        msg += "\nmatches per opponents: "+str(self.population_size_)
        msg += "\ntraining opponents: "+str([c.__name__ for c in self.coded_opponents_for_training_])
        msg += "\nvalidation opponents: "+str([c.__name__ for c in self.coded_opponents_for_validation_])
        return msg

    def _initialize_deck(self):
        deck = []
        for rank in PokerEnvironment.RANKS:
            for suit in PokerEnvironment.SUITS:
                deck.append(rank+suit)
        return deck

    def _initialize_hole_cards_based_on_hand_strength(self):
        hole_cards = STRENGTH_TABLE_FOR_2_CARDS.keys()
        strengths = [x for x in STRENGTH_TABLE_FOR_2_CARDS.values()]
        total_strengths = sum(strengths)
        probabilities = [e/total_strengths for e in strengths]
        hole_cards = numpy.random.choice(hole_cards, size = len(hole_cards)*1/2, replace = False, p = probabilities)
        final_cards = []
        for cards in hole_cards:
            final_cards.append(list(cards))
        return final_cards

    def _remove_points(self, points_to_remove, teams_population):
        super(PokerEnvironment, self)._remove_points(points_to_remove, teams_population)
        if Config.USER['reinforcement_parameters']['balanced_opponent_populations']:
            for point in points_to_remove:
                del PokerEnvironment.HAND_STRENGHT_MEMORY[point.point_id]
                del PokerEnvironment.HAND_PPOTENTIAL_MEMORY[point.point_id]
                del PokerEnvironment.HAND_NPOTENTIAL_MEMORY[point.point_id]
        else:
            if self.last_population_ != 'hall_of_fame' and self.last_population_ != 'sbb':
                for point in points_to_remove:
                    del PokerEnvironment.HAND_STRENGHT_MEMORY[self.last_population_][point.point_id]
                    del PokerEnvironment.HAND_PPOTENTIAL_MEMORY[self.last_population_][point.point_id]
                    del PokerEnvironment.HAND_NPOTENTIAL_MEMORY[self.last_population_][point.point_id]

    def _remove_point_from_hall_of_fame(self, point):
        super(PokerEnvironment, self)._remove_point_from_hall_of_fame(point)
        if Config.USER['reinforcement_parameters']['balanced_opponent_populations']:
            if point.point_id in PokerEnvironment.HAND_STRENGHT_MEMORY:
                del PokerEnvironment.HAND_STRENGHT_MEMORY[point.point_id]
                del PokerEnvironment.HAND_PPOTENTIAL_MEMORY[point.point_id]
                del PokerEnvironment.HAND_NPOTENTIAL_MEMORY[point.point_id]
        else:
            if point.point_id in PokerEnvironment.HAND_STRENGHT_MEMORY['hall_of_fame']:
                del PokerEnvironment.HAND_STRENGHT_MEMORY['hall_of_fame'][point.point_id]
                del PokerEnvironment.HAND_PPOTENTIAL_MEMORY['hall_of_fame'][point.point_id]
                del PokerEnvironment.HAND_NPOTENTIAL_MEMORY['hall_of_fame'][point.point_id]

    @staticmethod
    def normalize_winning(value):
        max_small_bet_turn_winning = PokerEnvironment.CONFIG['small_bet']*4
        max_big_bet_turn_winning = PokerEnvironment.CONFIG['big_bet']*4
        max_winning = max_small_bet_turn_winning*2 + max_big_bet_turn_winning*2
        max_losing = -max_winning
        return (value - max_losing)/float(max_winning - max_losing)

    @staticmethod
    def execute_player(player, port, point, is_training, is_sbb, memories):
        if is_sbb and not is_training:
            player.extra_metrics_['played_last_hand'] = False

        socket_tmp = socket.socket()

        total = 10
        attempt = 0
        while True:
            try:
                socket_tmp.connect(("localhost", port))
                break
            except socket_error as e:
                attempt += 1
                if e.errno == errno.ECONNREFUSED:
                    time.sleep(10)
                if attempt > total:
                    raise ValueError("Could not connect to port "+str(port))

        debug_file = None
        if Config.USER['reinforcement_parameters']['debug_matches']:
            debug_file = open(PokerEnvironment.CONFIG['acpc_path']+'outputs/player'+str(port)+'.log','w')
        socket_tmp.send("VERSION:2.0.0\r\n")
        previous_action = None
        partial_messages = []
        previous_messages = None
        player.initialize() # so a probabilistic opponent will always play equal for the same hands and actions
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
            match_state = MatchState(last_message, PokerEnvironment.CONFIG['small_bet'], PokerEnvironment.CONFIG['big_bet'], PokerEnvironment.full_deck, PokerEnvironment.hand_strength_hole_cards)
            if match_state.is_showdown():
                previous_action = None
                if Config.USER['reinforcement_parameters']['debug_matches']:
                    debug_file.write("showdown\n\n")
            elif match_state.is_current_player_to_act():
                if match_state.is_last_action_a_fold():
                    previous_action = None
                    if Config.USER['reinforcement_parameters']['debug_matches']:
                        debug_file.write("opponent folded\n\n")
                else:
                    chips = PokerEnvironment.get_chips(player, point, is_sbb)
                    if len(chips) == 0:
                        chips = 0.5
                    else:
                        chips = PokerEnvironment.normalize_winning(numpy.mean(chips))
                    inputs = match_state.inputs(memories) + [chips] + PokerEnvironment.get_opponent_model(player, point, is_sbb).inputs()
                    action = player.execute(point.point_id, inputs, match_state.valid_actions(), is_training)
                    if action is None:
                        action = 1
                    if is_sbb and is_training:
                        player.action_sequence_.append(str(action))
                    if is_sbb and not is_training:
                        if len(match_state.rounds) == 1 and len(match_state.rounds[0]) < 2 and action != 0: # first action of first round wasnt a fold
                            player.extra_metrics_['played_last_hand'] = True
                    action = PokerEnvironment.ACTION_MAPPING[action]
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
            else:
                if not previous_action == 'f':
                    previous_action = None
                if Config.USER['reinforcement_parameters']['debug_matches']:
                    debug_file.write("nothing to do\n\n")
        socket_tmp.close()
        if Config.USER['reinforcement_parameters']['debug_matches']:
            debug_file.write("The end.\n\n")
            debug_file.close()

        if is_sbb:
            PokerEnvironment.update_opponent_model_and_chips(player, point, previous_messages+partial_messages, debug_file, previous_action)

        updated = False
        if match_state.board_cards and not point.board_cards:
            point.board_cards = match_state.board_cards
            updated = True
        if is_sbb and not point.sbb_hole_cards:
            point.sbb_hole_cards = match_state.current_hole_cards
            updated = True
        if not is_sbb and not point.opponent_hole_cards:
            point.opponent_hole_cards = match_state.current_hole_cards
            updated = True
        if updated:
            point.update_metrics()

    @staticmethod
    def get_chips(player, point, is_sbb):
        if not is_sbb:
            return []
        opponent_id = PokerEnvironment.get_opponent_id(player, point, is_sbb)
        if opponent_id not in player.chips:
            player.chips[opponent_id] = []
        return player.chips[opponent_id]

    @staticmethod
    def get_opponent_id(player, point, is_sbb):
        if point.opponent.opponent_id == "hall_of_fame" or point.opponent.opponent_id == "sbb":
            opponent_id = point.opponent.team_id_
        else:
            opponent_id = point.opponent.opponent_id
        return opponent_id

    @staticmethod
    def get_opponent_model(player, point, is_sbb):
        if not is_sbb:
            return OpponentModel() # empty opponent model
        opponent_id = PokerEnvironment.get_opponent_id(player, point, is_sbb)
        if opponent_id not in player.opponent_model:
            player.opponent_model[opponent_id] = OpponentModel()
        return player.opponent_model[opponent_id]

    @staticmethod
    def update_opponent_model_and_chips(player, point, messages, debug_file, previous_action):
        for partial_msg in reversed(messages):
            if partial_msg:
                partial_match_state = MatchState(partial_msg, PokerEnvironment.CONFIG['small_bet'], PokerEnvironment.CONFIG['big_bet'], PokerEnvironment.full_deck, PokerEnvironment.hand_strength_hole_cards)
                self_actions, opponent_actions = partial_match_state.actions_per_player()
                if partial_match_state.is_showdown():
                    if Config.USER['reinforcement_parameters']['debug_matches']:
                        debug_file.write("partial_msg: "+str(partial_msg)+", previous_action: "+str(previous_action)+"\n\n")
                    self_folded = False
                    opponent_folded = False
                    winner = partial_match_state.get_winner_of_showdown()
                    if Config.USER['reinforcement_parameters']['debug_matches'] and winner is None:
                        debug_file.write("showdown, draw\n\n")
                    else:
                        if winner == partial_match_state.position:
                            if Config.USER['reinforcement_parameters']['debug_matches']:
                                debug_file.write("showdown, I won\n\n")
                            PokerEnvironment.get_chips(player, point, True).append(+(partial_match_state.calculate_pot()))
                        else:
                            if Config.USER['reinforcement_parameters']['debug_matches']:
                                debug_file.write("showdown, I lost\n\n")
                            PokerEnvironment.get_chips(player, point, True).append(-(partial_match_state.calculate_pot()))
                else:
                    last_player = partial_match_state.last_player_to_act()
                    if last_player == partial_match_state.position:
                        if self_actions and self_actions[-1] == 'f':
                            if Config.USER['reinforcement_parameters']['debug_matches']:
                                debug_file.write("partial_msg: "+str(partial_msg)+", I folded (1)\n\n")
                            self_folded = True
                            opponent_folded = False
                            PokerEnvironment.get_chips(player, point, True).append(-(partial_match_state.calculate_pot()))
                    elif opponent_actions and opponent_actions[-1] == 'f':
                        if Config.USER['reinforcement_parameters']['debug_matches']:
                            debug_file.write("partial_msg: "+str(partial_msg)+", opponent folded (1)\n\n")
                        self_folded = False
                        opponent_folded = True
                        PokerEnvironment.get_chips(player, point, True).append(+(partial_match_state.calculate_pot()))
                    elif previous_action == 'f':
                        if Config.USER['reinforcement_parameters']['debug_matches']:
                            debug_file.write("partial_msg: "+str(partial_msg)+", I folded (2)\n\n")
                        self_folded = True
                        opponent_folded = False
                        PokerEnvironment.get_chips(player, point, True).append(-(partial_match_state.calculate_pot()))
                    else:
                        if Config.USER['reinforcement_parameters']['debug_matches']:
                            debug_file.write("partial_msg: "+str(partial_msg)+", opponent folded (2)\n\n")
                        self_folded = False
                        opponent_folded = True
                        PokerEnvironment.get_chips(player, point, True).append(+(partial_match_state.calculate_pot()))
                PokerEnvironment.get_opponent_model(player, point, True).update_agressiveness(len(partial_match_state.rounds), self_actions, opponent_actions, self_folded, opponent_folded, previous_action)
                break