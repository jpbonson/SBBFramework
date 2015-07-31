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
        point_id = "("+str(opponent)+","+str(self.position_)+","+str(self.seed_)+")"
        super(PokerPoint, self).__init__(point_id, opponent)
        self.sbb_hole_cards = None
        self.opponent_hole_cards = None
        self.sbb_2card_strength = None
        self.opponent_2card_strength = None
        self.teams_results = []

    def update_metrics(self):
        if self.sbb_hole_cards:
            self.sbb_2card_strength = STRENGTH_TABLE_FOR_2_CARDS[frozenset(self.sbb_hole_cards)]
        if self.opponent_hole_cards:
            self.opponent_2card_strength = STRENGTH_TABLE_FOR_2_CARDS[frozenset(self.opponent_hole_cards)]

    def __str__(self):
        msg = str(self.opponent)+","+str(self.position_)+","+str(self.seed_)
        cards = str(self.sbb_hole_cards)+","+str(self.opponent_hole_cards)
        metrics = str(self.sbb_2card_strength)+","+str(self.opponent_2card_strength)
        return "(id = ["+msg+"], cards = ["+cards+"], metrics = ["+metrics+"])"

    def __repr__(self):
        return "("+str(self.opponent)+","+str(self.position_)+","+str(self.seed_)+")"

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
        'hands_against_sbb_opponents': Config.USER['training_parameters']['populations']['points']/10
    }

    def __init__(self):
        total_actions = 3 # fold, call, raise
        total_inputs = len(PokerEnvironment.INPUTS)
        coded_opponents_for_training = [PokerAlwaysCallOpponent, PokerAlwaysRaiseOpponent] # PokerAlwaysFoldOpponent
        coded_opponents_for_validation = [PokerAlwaysCallOpponent, PokerAlwaysRaiseOpponent] # PokerAlwaysFoldOpponent
        super(PokerEnvironment, self).__init__(total_actions, total_inputs, coded_opponents_for_training, coded_opponents_for_validation)
        port1, port2 = avaliable_ports()
        PokerEnvironment.CONFIG['available_ports'] = [port1, port2]
        self.population_size_for_hall_of_fame = self.population_size_/5 # it is lower, since more hands are played
        if self.population_size_for_hall_of_fame == 0:
            self.population_size_for_hall_of_fame = 1
        if PokerEnvironment.CONFIG['hands_against_sbb_opponents'] == 0:
            PokerEnvironment.CONFIG['hands_against_sbb_opponents'] = 1

    def _instantiate_point_for_coded_opponent_class(self, opponent_class):
        instance = opponent_class()
        return PokerPoint(str(instance), instance)

    def _instantiate_point_for_sbb_opponent(self, team, opponent_id):
        point = PokerPoint(team.__repr__(), team)
        point.opponent.opponent_id = opponent_id
        return point

    def _play_match(self, team, point, mode):
        """
        If the opponent is not a SBB player, play just 1 hand per point (since there will be 
        more points for that opponent type). If it is a SBB player, then it is necessary to 
        play more hands in order for it to be able to use effectively all the its inputs.
        """
        is_sbb_opponent = point.opponent.opponent_id == "hall_of_fame" or point.opponent.opponent_id == "sbb"
        if not is_sbb_opponent:
            result = self._play_hand(team, point, mode, point.position_, point.seed_)
        else:
            # play more hands for sbb opponents (also change de size of the point population for SBB opponents)
            # because otherwise they wont be able to use the opponent model themselves
            random_generator = numpy.random.RandomState(seed=point.seed_)
            results = []
            point.position_ = []
            for index in range(PokerEnvironment.CONFIG['hands_against_sbb_opponents']):
                position = index % 2
                point.position_.append(position)
                seed = random_generator.randint(0, Config.RESTRICTIONS['max_seed'])
                results.append(self._play_hand(team, point, mode, position, seed))
            result = numpy.mean(results)
            # cleaning memmory
            point.opponent.opponent_model = {}
            point.opponent.chips = {}
        return result

    def _play_hand(self, team, point, mode, position, seed):
        """

        """
        if mode == Config.RESTRICTIONS['mode']['training']:
            is_training = True
        else:
            is_training = False

        if Config.USER['reinforcement_parameters']['debug_matches'] and not os.path.exists(PokerEnvironment.CONFIG['acpc_path']+"outputs/"):
            os.makedirs(PokerEnvironment.CONFIG['acpc_path']+"outputs/")

        if mode == Config.RESTRICTIONS['mode']['champion'] or (is_training and self.current_population_ and self.current_population_ == 'sbb'):
            # because it wastes too much memmory to save the values for the champion
            # and it is usless to save it for the 'sbb' points, since they change every generation
            memories = ({}, {}, {})
            use_memmory = False
        else:
            use_memmory = True
            if Config.USER['reinforcement_parameters']['balanced_opponent_populations']:
                memories = (PokerEnvironment.HAND_STRENGHT_MEMORY[point.point_id], 
                    PokerEnvironment.HAND_PPOTENTIAL_MEMORY[point.point_id], 
                    PokerEnvironment.HAND_NPOTENTIAL_MEMORY[point.point_id])
            else:
                if is_training:
                    memories = (PokerEnvironment.HAND_STRENGHT_MEMORY[self.current_population_][point.point_id], 
                        PokerEnvironment.HAND_PPOTENTIAL_MEMORY[self.current_population_][point.point_id], 
                        PokerEnvironment.HAND_NPOTENTIAL_MEMORY[self.current_population_][point.point_id])
                else:
                    memories = (PokerEnvironment.HAND_STRENGHT_MEMORY['validation'][point.point_id], 
                        PokerEnvironment.HAND_PPOTENTIAL_MEMORY['validation'][point.point_id], 
                        PokerEnvironment.HAND_NPOTENTIAL_MEMORY['validation'][point.point_id])

        if position == 0:
            sbb_port = PokerEnvironment.CONFIG['available_ports'][0]
            opponent_port = PokerEnvironment.CONFIG['available_ports'][1]
            player1 = 'sbb'
            player2 = 'opponent'
        else:
            sbb_port = PokerEnvironment.CONFIG['available_ports'][1]
            opponent_port = PokerEnvironment.CONFIG['available_ports'][0]
            player1 = 'opponent'
            player2 = 'sbb'

        opponent_use_inputs = False
        one_hand_per_point = True
        is_sbb_opponent = False
        if point.opponent.opponent_id == "hall_of_fame" or point.opponent.opponent_id == "sbb":
            opponent_use_inputs = True
            one_hand_per_point = False
            is_sbb_opponent = True

        t1 = threading.Thread(target=PokerEnvironment.execute_player, args=[team, sbb_port, point, team, is_training, True, True, one_hand_per_point, memories, use_memmory])
        t2 = threading.Thread(target=PokerEnvironment.execute_player, args=[point.opponent, opponent_port, point, team, False, False, opponent_use_inputs, one_hand_per_point, memories, use_memmory])
        args = [PokerEnvironment.CONFIG['acpc_path']+'dealer', 
                PokerEnvironment.CONFIG['acpc_path']+'outputs/match_output', 
                PokerEnvironment.CONFIG['acpc_path']+'holdem.limit.2p.reverse_blinds.game', 
                "1", # total hands 
                str(seed),
                player1, player2, 
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
        if players[0] == 'sbb':
            sbb_position = 0
        else:
            sbb_position = 1
        normalized_value = PokerEnvironment.normalize_winning(float(scores[sbb_position]))
        if not is_training and not is_sbb_opponent:
            if mode == Config.RESTRICTIONS['mode']['validation']:
                team.extra_metrics_['total_hands_validation'] += 1
                team.extra_metrics_['total_hands_validation_per_point_type'][str(position)] += 1
            else:
                team.extra_metrics_['total_hands_champion'] += 1
                team.extra_metrics_['total_hands_champion_per_point_type'][str(position)] += 1
            if team.extra_metrics_['played_last_hand']:
                if mode == Config.RESTRICTIONS['mode']['validation']:
                    team.extra_metrics_['hand_played_validation'] += 1
                    team.extra_metrics_['hand_played_validation_per_point_type'][str(position)] += 1
                else:
                    team.extra_metrics_['hand_played_champion'] += 1
                    team.extra_metrics_['hand_played_champion_per_point_type'][str(position)] += 1
            if team.extra_metrics_['played_last_hand'] and normalized_value > 0.5:
                if mode == Config.RESTRICTIONS['mode']['validation']:
                    team.extra_metrics_['won_hands_validation'] += 1
                    team.extra_metrics_['won_hands_validation_per_point_type'][str(position)] += 1
                else:
                    team.extra_metrics_['won_hands_champion'] += 1
                    team.extra_metrics_['won_hands_champion_per_point_type'][str(position)] += 1

        if Config.USER['reinforcement_parameters']['debug_matches']:
            print "scores: "+str(scores)
            print "players: "+str(players)
            print "normalized_value: "+str(normalized_value)

        point.teams_results.append(normalized_value)

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
        PokerEnvironment.hole_cards_based_on_equity = self._initialize_hole_cards_based_on_equity()
        gc.collect()
        yappi.clear_stats()

    def setup(self, teams_population):
        super(PokerEnvironment, self).setup(teams_population)
        if Config.USER['reinforcement_parameters']['hall_of_fame']['enabled']:
            for point in self.point_population_per_opponent_['hall_of_fame']:
                point.opponent.opponent_model = {}
                point.opponent.chips = {}
        for point in self.point_population():
            point.teams_results = []
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

                for position in range(PokerEnvironment.CONFIG['positions']):
                    team.extra_metrics_['total_hands_validation_per_point_type'] = defaultdict(int)
                    team.extra_metrics_['total_hands_champion_per_point_type'] = defaultdict(int)
                    team.extra_metrics_['hand_played_validation_per_point_type'] = defaultdict(int)
                    team.extra_metrics_['hand_played_champion_per_point_type'] = defaultdict(int)
                    team.extra_metrics_['won_hands_validation_per_point_type'] = defaultdict(int)
                    team.extra_metrics_['won_hands_champion_per_point_type'] = defaultdict(int)

        if Config.USER['reinforcement_parameters']['hall_of_fame']['enabled']: # initializing
            for point in self.point_population_per_opponent_['hall_of_fame']:
                point.opponent.opponent_model = {}
                point.opponent.chips = {}

        for point in self.validation_population():
            point.teams_results = []

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
        msg += "\nmatches per opponents (not in hall of fame): "+str(self.population_size_)
        msg += "\ntraining opponents: "+str([c.__name__ for c in self.coded_opponents_for_training_])
        msg += "\nvalidation opponents: "+str([c.__name__ for c in self.coded_opponents_for_validation_])
        if Config.USER['reinforcement_parameters']['hall_of_fame']['enabled']:
            msg += "\nhall of fame size: "+str(self.population_size_for_hall_of_fame)
            msg += "\nmatches per opponents (in hall of fame): "+str(PokerEnvironment.CONFIG['hands_against_sbb_opponents'])
        return msg

    def _initialize_deck(self):
        deck = []
        for rank in PokerEnvironment.RANKS:
            for suit in PokerEnvironment.SUITS:
                deck.append(rank+suit)
        return deck

    def _initialize_hole_cards_based_on_equity(self):
        deck = self._initialize_deck()
        hole_cards = list(itertools.combinations(deck, 2))
        equities = []
        for card1, card2 in hole_cards:
            equities.append(MatchState.calculate_equity([card1, card2]))
        total_equities = sum(equities)
        probabilities = [e/float(total_equities) for e in equities]
        hole_cards_indices = numpy.random.choice(range(len(hole_cards)), size = int(len(hole_cards)*0.3), replace = False, p = probabilities)
        final_cards = []
        for index in hole_cards_indices:
            final_cards.append(hole_cards[index])
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
    def execute_player(player, port, point, team, is_training, is_sbb, use_inputs, one_hand_per_point, memories, use_memmory):
        if is_sbb and not is_training:
            player.extra_metrics_['played_last_hand'] = True

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
            print player.__repr__()+": started"
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
            match_state = MatchState(last_message, PokerEnvironment.CONFIG['small_bet'], PokerEnvironment.CONFIG['big_bet'], PokerEnvironment.full_deck, PokerEnvironment.hole_cards_based_on_equity)
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
                        chips = PokerEnvironment.get_chips(player, point, team, is_sbb)
                        if len(chips) == 0:
                            chips = 0.5
                        else:
                            chips = PokerEnvironment.normalize_winning(numpy.mean(chips))
                        inputs = match_state.inputs(memories, use_memmory) + [chips] + PokerEnvironment.get_opponent_model(player, point, team, is_sbb).inputs()
                    else:
                        inputs = []
                    action = player.execute(point.point_id, inputs, match_state.valid_actions(), is_training)
                    if action is None:
                        action = 1
                    if is_sbb and is_training:
                        player.action_sequence_.append(str(action))
                    if is_sbb and not is_training:
                        if len(match_state.rounds) == 1 and len(match_state.rounds[0]) < 2 and action == 0: # first action of first round is a fold
                            player.extra_metrics_['played_last_hand'] = False
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
            PokerEnvironment.update_opponent_model_and_chips(player, point, team, previous_messages+partial_messages, debug_file, previous_action, is_sbb)

        if one_hand_per_point:
            updated = False
            if is_sbb and not point.sbb_hole_cards:
                point.sbb_hole_cards = match_state.current_hole_cards
                updated = True
            if not is_sbb and not point.opponent_hole_cards:
                point.opponent_hole_cards = match_state.current_hole_cards
                updated = True
            if updated:
                point.update_metrics()

        if Config.USER['reinforcement_parameters']['debug_matches']:
            debug_file.write("The end.\n\n")
            print player.__repr__()+": The end.\n"
            debug_file.close()

    @staticmethod
    def get_chips(player, point, team, is_sbb):
        opponent_id = PokerEnvironment.get_opponent_id(player, point, team, is_sbb)
        if opponent_id not in player.chips:
            player.chips[opponent_id] = []
        return player.chips[opponent_id]

    @staticmethod
    def get_opponent_id(player, point, team, is_sbb):
        if is_sbb:
            if point.opponent.opponent_id == "hall_of_fame" or point.opponent.opponent_id == "sbb":
                opponent_id = point.opponent.team_id_
            else:
                opponent_id = point.opponent.opponent_id
        else:
            opponent_id = team.team_id_
        return opponent_id

    @staticmethod
    def get_opponent_model(player, point, team, is_sbb):
        opponent_id = PokerEnvironment.get_opponent_id(player, point, team, is_sbb)
        if opponent_id not in player.opponent_model:
            player.opponent_model[opponent_id] = OpponentModel()
        return player.opponent_model[opponent_id]

    @staticmethod
    def update_opponent_model_and_chips(player, point, team, messages, debug_file, previous_action, is_sbb):
        for partial_msg in reversed(messages):
            if partial_msg:
                partial_match_state = MatchState(partial_msg, PokerEnvironment.CONFIG['small_bet'], PokerEnvironment.CONFIG['big_bet'], PokerEnvironment.full_deck, PokerEnvironment.hole_cards_based_on_equity)
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
                            PokerEnvironment.get_chips(player, point, team, is_sbb).append(+(partial_match_state.calculate_pot()))
                        else:
                            if Config.USER['reinforcement_parameters']['debug_matches']:
                                debug_file.write("showdown, I lost\n\n")
                                print player.__repr__()+": showdown, I lost\n"
                            PokerEnvironment.get_chips(player, point, team, is_sbb).append(-(partial_match_state.calculate_pot()))
                else:
                    last_player = partial_match_state.last_player_to_act()
                    if last_player == partial_match_state.position:
                        if self_actions and self_actions[-1] == 'f':
                            if Config.USER['reinforcement_parameters']['debug_matches']:
                                debug_file.write("partial_msg: "+str(partial_msg)+", I folded (1)\n\n")
                                print player.__repr__()+": partial_msg: "+str(partial_msg)+", I folded (1)\n"
                            self_folded = True
                            opponent_folded = False
                            PokerEnvironment.get_chips(player, point, team, is_sbb).append(-(partial_match_state.calculate_pot()))
                    elif opponent_actions and opponent_actions[-1] == 'f':
                        if Config.USER['reinforcement_parameters']['debug_matches']:
                            debug_file.write("partial_msg: "+str(partial_msg)+", opponent folded (1)\n\n")
                            print player.__repr__()+": partial_msg: "+str(partial_msg)+", opponent folded (1)\n"
                        self_folded = False
                        opponent_folded = True
                        PokerEnvironment.get_chips(player, point, team, is_sbb).append(+(partial_match_state.calculate_pot()))
                    elif previous_action == 'f':
                        if Config.USER['reinforcement_parameters']['debug_matches']:
                            debug_file.write("partial_msg: "+str(partial_msg)+", I folded (2)\n\n")
                            print player.__repr__()+": partial_msg: "+str(partial_msg)+", I folded (2)\n"
                        self_folded = True
                        opponent_folded = False
                        PokerEnvironment.get_chips(player, point, team, is_sbb).append(-(partial_match_state.calculate_pot()))
                    else:
                        if Config.USER['reinforcement_parameters']['debug_matches']:
                            debug_file.write("partial_msg: "+str(partial_msg)+", opponent folded (2)\n\n")
                            print player.__repr__()+": partial_msg: "+str(partial_msg)+", opponent folded (2)\n"
                        self_folded = False
                        opponent_folded = True
                        PokerEnvironment.get_chips(player, point, team, is_sbb).append(+(partial_match_state.calculate_pot()))
                PokerEnvironment.get_opponent_model(player, point, team, is_sbb).update_agressiveness(len(partial_match_state.rounds), self_actions, opponent_actions, self_folded, opponent_folded, previous_action)
                break