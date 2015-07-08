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
from match_state import MatchState
from tables.equity_table import UNIQUE_EQUITY_TABLE
from tables.strenght_table_for_2cards import STRENGTH_TABLE_FOR_2_CARDS
from poker_opponents import PokerRandomOpponent, PokerAlwaysFoldOpponent, PokerAlwaysCallOpponent, PokerAlwaysRaiseOpponent
from ..reinforcement_environment import ReinforcementEnvironment, ReinforcementPoint
from ...config import Config

class OpponentModel():
    """
    ATTENTION: If you change the order, add or remove inputs the SBB teams that were already trained will 
    behave unexpectedly!

    All inputs are normalized, so they influence the SBB player potentially equal,

    inputs[0] = self short-term agressiveness (last 10 hands)
    inputs[1] = self long-term agressiveness
    inputs[2] = opponent short-term agressiveness (last 10 hands)
    inputs[3] = opponent long-term agressiveness
    inputs[4] = self short-term volatility (last 10 hands)
    inputs[5] = self long-term volatility
    inputs[6] = opponent short-term volatility (last 10 hands)
    inputs[7] = opponent long-term volatility
    reference for agressiveness: "Countering Evolutionary Forgetting in No-Limit Texas Hold'em Poker Agents"

    volatility: how frequently the opponent changes its behaviors between pre-flop and post-flop
    formula: (agressiveness pos-flop)-(agressiveness pre-flop) (normalized between 0.0 and 1.0, 
        where 0.5: no volatility, 0.0: get less agressive, 1.0: get more agressive)
    question: isn't expected that most opponents will be less agressive pre-flop and more agressive post-flop? 
    (since they probably got better hands?) may this metric be usefull to identify bluffing?
    """

    INPUTS = ['self short-term agressiveness', 'self long-term agressiveness', 'opponent short-term agressiveness', 
        'opponent long-term agressiveness', 'self short-term volatility', 'self long-term volatility', 
        'opponent short-term volatility', 'opponent long-term volatility']

    def __init__(self):
        self.self_agressiveness = []
        self.opponent_agressiveness = []
        self.self_agressiveness_preflop = []
        self.self_agressiveness_postflop = []
        self.opponent_agressiveness_preflop = []
        self.opponent_agressiveness_postflop = []

    def update_agressiveness(self, total_rounds, self_actions, opponent_actions, self_folded, opponent_folded, previous_action):
        if self_folded:
            if self_actions:
                if self_actions[-1] != 'f':
                    self_actions.append('f')
            else:
                self_actions.append('f')
        if opponent_folded:
            if opponent_actions:
                if opponent_actions[-1] != 'f':
                    opponent_actions.append('f')
            else:
                opponent_actions.append('f')
            if previous_action:
                self_actions.append(previous_action)
        if len(self_actions) > 0:
            agressiveness = self._calculate_points(self_actions)/float(len(self_actions))
            self.self_agressiveness.append(agressiveness)
            if total_rounds == 1:
                self.self_agressiveness_preflop.append(agressiveness)
            else:
                self.self_agressiveness_postflop.append(agressiveness)
        if len(opponent_actions) > 0:
            agressiveness = self._calculate_points(opponent_actions)/float(len(opponent_actions))
            self.opponent_agressiveness.append(agressiveness)
            if total_rounds == 1:
                self.opponent_agressiveness_preflop.append(agressiveness)
            else:
                self.opponent_agressiveness_postflop.append(agressiveness)

    def _calculate_points(self, actions):
        points = 0.0
        for action in actions:
            if action == 'c':
                points += 0.5
            if action == 'r':
                points += 1.0
        return points

    def inputs(self):
        inputs = [0] * len(OpponentModel.INPUTS)
        inputs[4] = 0.5
        inputs[5] = 0.5
        inputs[6] = 0.5
        inputs[7] = 0.5
        if len(self.self_agressiveness) > 0:
            inputs[0] = numpy.mean(self.self_agressiveness[:10])
            inputs[1] = numpy.mean(self.self_agressiveness)
        if len(self.opponent_agressiveness) > 0:
            inputs[2] = numpy.mean(self.opponent_agressiveness[:10])
            inputs[3] = numpy.mean(self.opponent_agressiveness)
        if len(self.self_agressiveness_postflop) > 0 and len(self.self_agressiveness_preflop) > 0:
            inputs[4] = self.normalize_volatility(numpy.mean(self.self_agressiveness_postflop[:10])-numpy.mean(self.self_agressiveness_preflop[:10]))
            inputs[5] = self.normalize_volatility(numpy.mean(self.self_agressiveness_postflop)-numpy.mean(self.self_agressiveness_preflop))
        if len(self.opponent_agressiveness_postflop) > 0 and len(self.opponent_agressiveness_preflop) > 0:
            inputs[6] = self.normalize_volatility(numpy.mean(self.opponent_agressiveness_postflop[:10])-numpy.mean(self.opponent_agressiveness_preflop[:10]))
            inputs[7] = self.normalize_volatility(numpy.mean(self.opponent_agressiveness_postflop)-numpy.mean(self.opponent_agressiveness_preflop))
        return inputs

    def normalize_volatility(self, value):
        return (value+1.0)/2.0

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
    HAND_STRENGHT_MEMORY = defaultdict(dict)
    HAND_PPOTENTIAL_MEMORY = defaultdict(dict)
    HAND_NPOTENTIAL_MEMORY = defaultdict(dict)

    def __init__(self):
        total_actions = 3 # fold, call, raise
        total_inputs = len(PokerEnvironment.INPUTS)
        coded_opponents = [PokerAlwaysFoldOpponent, PokerAlwaysCallOpponent, PokerAlwaysRaiseOpponent]
        super(PokerEnvironment, self).__init__(total_actions, total_inputs, coded_opponents)
        self.total_positions_ = 2

    def instantiate_point_for_coded_opponent_class(self, opponent_class):
        instance = opponent_class()
        return PokerPoint(str(instance), instance)

    def instantiate_point_for_sbb_opponent(self, team):
        return PokerPoint(team.__repr__(), team)

    def play_match(self, team, point, is_training):
        """

        """
        if Config.USER['reinforcement_parameters']['debug_matches'] and not os.path.exists(Config.RESTRICTIONS['poker']['acpc_path']+"outputs/"):
            os.makedirs(Config.RESTRICTIONS['poker']['acpc_path']+"outputs/")

        t1 = threading.Thread(target=PokerEnvironment.execute_player, args=[team, Config.RESTRICTIONS['poker']['available_ports'][0], point.point_id, is_training, point])
        t2 = threading.Thread(target=PokerEnvironment.execute_player, args=[point.opponent, Config.RESTRICTIONS['poker']['available_ports'][1], point.point_id, False, point])
        args = [Config.RESTRICTIONS['poker']['acpc_path']+'dealer', 
                Config.RESTRICTIONS['poker']['acpc_path']+'outputs/match_output', 
                Config.RESTRICTIONS['poker']['acpc_path']+'holdem.limit.2p.reverse_blinds.game', 
                str(Config.USER['reinforcement_parameters']['poker']['total_hands']), 
                str(point.seed_),
                'sbb', 'opponent', 
                '-p', str(Config.RESTRICTIONS['poker']['available_ports'][0])+","+str(Config.RESTRICTIONS['poker']['available_ports'][1])]
        if not Config.USER['reinforcement_parameters']['debug_matches']:
            args.append('-l')
        p = subprocess.Popen(args, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        t1.start()
        t2.start()
        out, err = p.communicate()
        t1.join()
        t2.join()

        if Config.USER['reinforcement_parameters']['debug_matches']:
            with open(Config.RESTRICTIONS['poker']['acpc_path']+"outputs/match.log", "w") as text_file:
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
        normalized_value = MatchState.normalize_winning(avg_score)
        if Config.USER['reinforcement_parameters']['debug_matches']:
            print "scores: "+str(scores)
            print "players: "+str(players)
            print "avg score: "+str(avg_score)
            print "normalized_value: "+str(normalized_value)
        return normalized_value

    def reset(self):
        for point in self.point_population():
            del PokerEnvironment.HAND_STRENGHT_MEMORY[point.point_id]
            del PokerEnvironment.HAND_PPOTENTIAL_MEMORY[point.point_id]
            del PokerEnvironment.HAND_NPOTENTIAL_MEMORY[point.point_id]
        super(PokerEnvironment, self).reset()
        PokerEnvironment.full_deck = self._initialize_deck()
        PokerEnvironment.equity_hole_cards = self._initialize_hole_cards_based_on_equity()
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

    def _initialize_hole_cards_based_on_equity(self):
        hole_cards = UNIQUE_EQUITY_TABLE.keys()
        equities = [x[0] for x in UNIQUE_EQUITY_TABLE.values()]
        total_equities = sum(equities)
        probabilities = [e/total_equities for e in equities]
        hole_cards = numpy.random.choice(hole_cards, size = len(hole_cards)*17/18, replace = False, p = probabilities)
        unpacked_hole_cards = []
        suites_permutations = list(itertools.permutations(PokerEnvironment.SUITS, 2))
        for cards in hole_cards:
            card1 = cards[0]
            card2 = cards[1]
            if cards[2] == 's':
                suites = random.sample(PokerEnvironment.SUITS, 2)
                for suit in suites:
                    unpacked_hole_cards.append((card1 + suit, card2 + suit))
            else:
                suites = random.sample(suites_permutations, len(suites_permutations)/2)
                for suit1, suit2 in suites:
                    unpacked_hole_cards.append((card1 + suit1, card2 + suit2))
        return unpacked_hole_cards

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
        for point in points_to_remove:
            del PokerEnvironment.HAND_STRENGHT_MEMORY[point.point_id]
            del PokerEnvironment.HAND_PPOTENTIAL_MEMORY[point.point_id]
            del PokerEnvironment.HAND_NPOTENTIAL_MEMORY[point.point_id]

    @staticmethod
    def execute_player(player, port, point_id, is_training, point):
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
            debug_file = open(Config.RESTRICTIONS['poker']['acpc_path']+'outputs/player'+str(port)+'.log','w')
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
            match_state = MatchState(last_message, PokerEnvironment.full_deck, PokerEnvironment.equity_hole_cards, PokerEnvironment.hand_strength_hole_cards)
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
                        chips = MatchState.normalize_winning(total_chips/float(match_state.hand_id))
                    inputs = [chips] + match_state.inputs(PokerEnvironment.HAND_STRENGHT_MEMORY[point_id], PokerEnvironment.HAND_PPOTENTIAL_MEMORY[point_id], PokerEnvironment.HAND_NPOTENTIAL_MEMORY[point_id]) + opponent_model.inputs()
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
                partial_match_state = MatchState(partial_msg, PokerEnvironment.full_deck, PokerEnvironment.equity_hole_cards, PokerEnvironment.hand_strength_hole_cards)
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