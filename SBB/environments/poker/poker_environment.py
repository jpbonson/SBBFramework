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
    Encapsulates a poker opponent as a point.
    """

    def __init__(self, point_id, opponent):
        self.seed_ = random.randint(0, Config.RESTRICTIONS['max_seed'])
        point_id = "("+str(point_id)+","+str(self.seed_)+")"
        super(PokerPoint, self).__init__(point_id, opponent)

class PokerEnvironment(ReinforcementEnvironment):
    """
    This environment encapsulates all methods to deal with a reinforcement learning task for TicTacToe.
    """

    ACTION_MAPPING = {0: 'f', 1: 'c', 2: 'r'}
    INPUTS = ['chips']+MatchState.INPUTS+OpponentModel.INPUTS
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
    }

    def __init__(self):
        total_actions = 3 # fold, call, raise
        total_inputs = len(PokerEnvironment.INPUTS)
        coded_opponents = [PokerAlwaysFoldOpponent, PokerAlwaysCallOpponent, PokerAlwaysRaiseOpponent]
        super(PokerEnvironment, self).__init__(total_actions, total_inputs, coded_opponents)
        self.total_positions_ = 2
        port1, port2 = avaliable_ports()
        PokerEnvironment.CONFIG['available_ports'] = [port1, port2]

    def _instantiate_point_for_coded_opponent_class(self, opponent_class):
        instance = opponent_class()
        return PokerPoint(str(instance), instance)

    def _instantiate_point_for_sbb_opponent(self, team):
        return PokerPoint(team.__repr__(), team)

    def _play_match(self, team, point, is_training):
        """

        """
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
        t1 = threading.Thread(target=PokerEnvironment.execute_player, args=[team, PokerEnvironment.CONFIG['available_ports'][0], point.point_id, is_training, memories])
        t2 = threading.Thread(target=PokerEnvironment.execute_player, args=[point.opponent, PokerEnvironment.CONFIG['available_ports'][1], point.point_id, False, memories])
        args = [PokerEnvironment.CONFIG['acpc_path']+'dealer', 
                PokerEnvironment.CONFIG['acpc_path']+'outputs/match_output', 
                PokerEnvironment.CONFIG['acpc_path']+'holdem.limit.2p.reverse_blinds.game', 
                str(Config.USER['reinforcement_parameters']['poker']['total_hands']), 
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
        avg_score = float(scores[0])/float(Config.USER['reinforcement_parameters']['poker']['total_hands'])
        normalized_value = PokerEnvironment.normalize_winning(avg_score)
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

    def metrics(self):
        msg = ""
        msg += "\n### Environment Info:"
        msg += "\nports: "+str(PokerEnvironment.CONFIG['available_ports'])
        msg += "\ntotal inputs: "+str(self.total_inputs_)
        msg += "\ninputs: "+str(PokerEnvironment.INPUTS)
        msg += "\ntotal actions: "+str(self.total_actions_)
        msg += "\nactions mapping: "+str(PokerEnvironment.ACTION_MAPPING)
        msg += "\npositions: "+str(self.total_positions_)
        msg += "\nmatches per opponents (for each position): "+str(self.population_size_)
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
    def execute_player(player, port, point_id, is_training, memories):
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
        last_hand_id = -1
        opponent_model = OpponentModel()
        previous_messages = None
        previous_action = None
        total_chips = 0.0 # Chips (the stacks are infinite, but it may be useful to play more conservative if it is losing a lot)
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
            partial_messages = message.split("MATCHSTATE")
            last_message = partial_messages[-1] # only cares about the last message sent (ie. the one where this player should act)
            match_state = MatchState(last_message, PokerEnvironment.CONFIG['small_bet'], PokerEnvironment.CONFIG['big_bet'], PokerEnvironment.full_deck, PokerEnvironment.hand_strength_hole_cards)
            if match_state.hand_id != last_hand_id:
                player.initialize() # so a probabilistic opponent will always play equal for the same hands and actions
                if last_hand_id != -1:
                    messages = previous_messages + partial_messages
                    total_chips = PokerEnvironment.update_opponent_model_and_chips(opponent_model, messages, total_chips, match_state.hand_id-1, debug_file, previous_action)
                last_hand_id = match_state.hand_id
            previous_messages = partial_messages
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
                    if match_state.hand_id == 0:
                        chips = 0.5
                    else:
                        chips = PokerEnvironment.normalize_winning(total_chips/float(match_state.hand_id))
                    inputs = [chips] + match_state.inputs(memories) + opponent_model.inputs()
                    action = player.execute(point_id, inputs, match_state.valid_actions(), is_training)
                    if action is None:
                        action = "c"
                    else:
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

    @staticmethod
    def update_opponent_model_and_chips(opponent_model, messages, total_chips, last_hand_id, debug_file, previous_action):
        for partial_msg in reversed(messages):
            if partial_msg:
                partial_match_state = MatchState(partial_msg, PokerEnvironment.CONFIG['small_bet'], PokerEnvironment.CONFIG['big_bet'], PokerEnvironment.full_deck, PokerEnvironment.hand_strength_hole_cards)
                if partial_match_state.hand_id == last_hand_id: # get the last message of the last hand
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
                                total_chips = total_chips + partial_match_state.calculate_pot()
                            else:
                                if Config.USER['reinforcement_parameters']['debug_matches']:
                                    debug_file.write("showdown, I lost\n\n")
                                total_chips = total_chips - partial_match_state.calculate_pot()
                    else:
                        last_player = partial_match_state.last_player_to_act()
                        if last_player == partial_match_state.position:
                            if self_actions and self_actions[-1] == 'f':
                                if Config.USER['reinforcement_parameters']['debug_matches']:
                                    debug_file.write("partial_msg: "+str(partial_msg)+", I folded (1)\n\n")
                                self_folded = True
                                opponent_folded = False
                                total_chips = total_chips - partial_match_state.calculate_pot()
                        elif opponent_actions and opponent_actions[-1] == 'f':
                            if Config.USER['reinforcement_parameters']['debug_matches']:
                                debug_file.write("partial_msg: "+str(partial_msg)+", opponent folded (1)\n\n")
                            self_folded = False
                            opponent_folded = True
                            total_chips = total_chips + partial_match_state.calculate_pot()
                        elif previous_action == 'f':
                            if Config.USER['reinforcement_parameters']['debug_matches']:
                                debug_file.write("partial_msg: "+str(partial_msg)+", I folded (2)\n\n")
                            self_folded = True
                            opponent_folded = False
                            total_chips = total_chips - partial_match_state.calculate_pot()
                        else:
                            if Config.USER['reinforcement_parameters']['debug_matches']:
                                debug_file.write("partial_msg: "+str(partial_msg)+", opponent folded (2)\n\n")
                            self_folded = False
                            opponent_folded = True
                            total_chips = total_chips + partial_match_state.calculate_pot()
                    opponent_model.update_agressiveness(len(partial_match_state.rounds), self_actions, opponent_actions, self_folded, opponent_folded, previous_action)
                    break
        return total_chips