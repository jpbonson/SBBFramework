import os
import re
import random
import itertools
import numpy
if os.name == 'posix':
    from pokereval import PokerEval
from tables.normalized_equity_table import NORMALIZED_HAND_EQUITY
from tables.strenght_table_for_2cards import STRENGTH_TABLE_FOR_2_CARDS
from ...utils.helpers import round_value

class MatchState():

    INPUTS = ['pot', 'bet', 'pot odds', 'betting position', 'round', 'equity', 'hand strength', 'EHS']

    def __init__(self, message, small_bet, big_bet):
        self.message = message
        self.small_bet = small_bet
        self.big_bet = big_bet
        self.position = None
        self.opponent_position = None
        self.hand_id = None
        self.rounds = None
        self.current_hole_cards = None
        self.opponent_hole_cards = None
        self.board_cards = None
        self._decode_message(message)
        self.pokereval = PokerEval()

    def _decode_message(self, message):
        splitted = message.split(":")
        self.position = int(splitted[1])
        if self.position == 0:
            self.opponent_position = 1
        else:
            self.opponent_position = 0
        self.hand_id = int(splitted[2])
        self.rounds = splitted[3].split("/")
        cards = splitted[4].split("/")
        hole_cards = cards[0].split("|")
        if self.position == 0:
            self.current_hole_cards = re.findall('..', hole_cards[0])
            self.opponent_hole_cards = re.findall('..', hole_cards[1])
        else:
            self.current_hole_cards = re.findall('..', hole_cards[1])
            self.opponent_hole_cards = re.findall('..', hole_cards[0])
        self.board_cards = []
        for turn in cards[1:]:
            self.board_cards += re.findall('..', turn)

    def is_current_player_to_act(self):
        if len(self.rounds) == 1: # since the game uses reverse blinds
            if len(self.rounds[0]) % 2 == 0:
                current_player = 1
            else:
                current_player = 0
        else:
            if len(self.rounds[-1]) % 2 == 0:
                current_player = 0
            else:
                current_player = 1
        if int(self.position) == current_player:
            return True
        else:
            return False

    def last_player_to_act(self):
        if len(self.rounds[-1]) == 0:
            acted_round = self.rounds[-2]
        else:
            acted_round = self.rounds[-1]
        if acted_round == self.rounds[0]: # since the game uses reverse blinds
            if len(acted_round) % 2 == 0:
                last_player = 0
            else:
                last_player = 1
        else: # cc/cr/rr 10/01/01
            if len(acted_round) % 2 == 0:
                last_player = 1
            else:
                last_player = 0
        return last_player

    def is_showdown(self):
        if self.opponent_hole_cards:
            return True
        else:
            return False

    def get_winner_of_showdown(self):
        our_rank = self.pokereval.evaln(self.current_hole_cards + self.board_cards)
        opponent_rank = self.pokereval.evaln(self.opponent_hole_cards + self.board_cards)
        if our_rank > opponent_rank:
            return self.position
        if our_rank < opponent_rank:
            return self.opponent_position
        return None # draw

    def is_last_action_a_fold(self):
        actions = self.rounds[-1]
        if len(actions) > 0 and actions[-1] == 'f':
            return True
        else:
            return False

    def actions_per_player(self):
        # check the other cases
        self_actions = []
        opponent_actions = []
        for round_index, actions in enumerate(self.rounds):
            if round_index == 0 or round_index == 1:
                bet = self.small_bet
            else:
                bet = self.big_bet
            for action_index, action in enumerate(actions):
                if round_index == 0:
                    if self.position == 0:
                        if action_index % 2 == 0:
                            opponent_actions.append(action)
                        else:
                            self_actions.append(action)
                    else:
                        if action_index % 2 == 0:
                            self_actions.append(action)
                        else:
                            opponent_actions.append(action)
                else:
                    if self.position == 0:
                        if action_index % 2 == 0:
                            self_actions.append(action)
                        else:
                            opponent_actions.append(action)
                    else:
                        if action_index % 2 == 0:
                            opponent_actions.append(action)
                        else:
                            self_actions.append(action)
        return self_actions, opponent_actions

    def inputs(self, memories):
        """
        ATTENTION: If you change the order, add or remove inputs the SBB teams that were already trained will 
        behave unexpectedly!

        All inputs are normalized, so they influence the SBB player potentially equal.

        inputs[0] = pot
        inputs[1] = bet
        inputs[2] = pot odds
        inputs[3] = betting position (0: first betting, 1: last betting)
        inputs[4] = round 
        inputs[5] = equity
        inputs[6] = hand_strength
        inputs[7] = EHS # modified from the original
        """
        hand_strength_memory, hand_ppotential_memory = memories
        inputs = [0] * len(MatchState.INPUTS)
        inputs[0] = self.calculate_pot()/float(self.maximum_winning())
        inputs[1] = self._calculate_bet()
        if inputs[0] + inputs[1] > 0:
            inputs[2] = inputs[1] / float(inputs[0] + inputs[1])
        else:
            inputs[2] = 0.0
        inputs[3] = float(self._betting_position())
        inputs[4] = (len(self.rounds)-1)/3.0
        inputs[5] = NORMALIZED_HAND_EQUITY[frozenset(self.current_hole_cards)]
        inputs[6] = MatchState.calculate_hand_strength(self.current_hole_cards, self.board_cards, self.full_deck, hand_strength_memory)
        inputs[7] = self._calculate_ehs(inputs[6], inputs[5], hand_ppotential_memory, len(self.rounds))
        return inputs

    def inputs_for_rule_based_opponents(self, memories):
        """
        """
        inputs = {}
        inputs['bet'] = self._calculate_bet()
        inputs['round'] = len(self.rounds)
        inputs['equity'] = NORMALIZED_HAND_EQUITY[frozenset(self.current_hole_cards)]
        hand_strength_memory, hand_ppotential_memory = memories
        hand_strength = MatchState.calculate_hand_strength(self.current_hole_cards, self.board_cards, self.full_deck, hand_strength_memory)
        inputs['EHS'] = self._calculate_ehs(hand_strength, inputs['equity'], hand_ppotential_memory, len(self.rounds))
        return inputs

    def calculate_pot(self):
        # check if is the small blind
        if len(self.rounds) == 1:
            if len(self.rounds[0]) == 0 or (len(self.rounds[0]) == 1 and self.rounds[0][0] == 'f'):
                return self.small_bet/2.0

        # check if someone raised
        pot = self.small_bet
        for i, r in enumerate(self.rounds):
            if i == 0 or i == 1:
                bet = self.small_bet
            else:
                bet = self.big_bet
            for action in r:
                if action == 'r':
                    pot += bet
        return pot

    def maximum_winning(self):
        max_small_bet_turn_winning = self.small_bet*4
        max_big_bet_turn_winning = self.big_bet*4
        return max_small_bet_turn_winning*2 + max_big_bet_turn_winning*2

    def _calculate_bet(self):
        # check if is the small blind
        if len(self.rounds) == 1 and len(self.rounds[0]) == 0:
            return 0.5
        
        # check if the opponent raised
        bet = 0.0
        current_round = self.rounds[-1]
        if current_round: # if there is previous actions
            last_action = current_round[-1]
            if last_action == 'r':
                bet = 1.0 # since the value is normalized and the poker is limited, 1 means the maximum bet
        return bet

    def _betting_position(self):
        if len(self.rounds) == 1: # reverse blinds
            if self.position == 0:
                return 1
            else:
                return 0
        else:
            return self.position

    def valid_actions(self):
        """
        
        """
        valid = [1]
        # check if can fold
        if len(self.rounds) > 1:
            current_round = self.rounds[-1]
            if 'r' in current_round:
                valid.append(0)
        else:
            current_round = self.rounds[-1]
            if len(current_round) == 0 or 'r' in current_round:
                valid.append(0)

        # check if can raise
        if len(self.rounds) == 1:
            max_raises = 3
        else:
            max_raises = 4
        raises = 0
        for action in self.rounds[-1]:
            if action == 'r':
                raises += 1
        if raises < max_raises:
            valid.append(2)
        return valid

    def __str__(self):
        msg = "\n"
        msg += "position: "+str(self.position)+"\n"
        msg += "opponent_position: "+str(self.opponent_position)+"\n"
        msg += "hand_id: "+str(self.hand_id)+"\n"
        msg += "rounds: "+str(self.rounds)+"\n"
        msg += "current_hole_cards: "+str(self.current_hole_cards)+"\n"
        msg += "opponent_hole_cards: "+str(self.opponent_hole_cards)+"\n"
        msg += "board_cards: "+str(self.board_cards)+"\n"
        return msg