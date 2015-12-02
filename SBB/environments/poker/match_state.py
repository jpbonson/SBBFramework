import re
import numpy
from poker_config import PokerConfig
from ...utils.helpers import round_value
from ...config import Config

class MatchState():

    INPUTS = ['hand strength', 'effective potential', 'pot', 'bet', 'pot odds', 'betting position', 'round', 'chips']

    def __init__(self, point, player_key):
        self.point = point
        self.player_key = player_key
        self.position = point.players[player_key]['position']
        self.hand_strength = point.players[player_key]['hand_strength']
        self.effective_potential = point.players[player_key]['effective_potential']
        self.hole_cards = point.players[player_key]['hole_cards']
        self.actions = []

    def inputs(self, pot, bet, chips, round_id):
        """
        inputs[0] = hand strength
        inputs[1] = effective potential
        inputs[2] = pot
        inputs[3] = bet
        inputs[4] = pot odds
        inputs[5] = betting position (0: first betting, 1: last betting)
        inputs[6] = round
        inputs[7] = chips
        """
        if self.player_key == 'team':
            inputs = [0] * len(MatchState.INPUTS)
            inputs[0] = self.hand_strength[round_id]
            inputs[1] = self.effective_potential[round_id]
            inputs[2] = pot/float(MatchState.maximum_winning())
            inputs[3] = bet/float(PokerConfig.CONFIG['big_bet'])
            if (pot + bet) > 0:
                inputs[4] = bet / float(pot + bet)
            else:
                inputs[4] = 0.0
            inputs[5] = float(self._betting_position(round_id))
            inputs[6] = round_id/3.0
            inputs[7] = self._calculate_chips_input(chips)
            normalized_inputs = [round_value(i*Config.RESTRICTIONS['multiply_normalization_by']) for i in inputs[2:]]
            return inputs[:2]+normalized_inputs
        else: # inputs for rule-based opponents
            inputs = [0] * 2
            inputs[0] = self.hand_strength[round_id]
            inputs[1] = bet/float(PokerConfig.CONFIG['big_bet'])
            inputs[1] = round_value(inputs[1]*Config.RESTRICTIONS['multiply_normalization_by'])
            return inputs

    @staticmethod
    def maximum_winning():
        max_small_bet_turn_winning = PokerConfig.CONFIG['small_bet']*4
        max_big_bet_turn_winning = PokerConfig.CONFIG['big_bet']*4
        return max_small_bet_turn_winning*2 + max_big_bet_turn_winning*2

    def _betting_position(self, round_id):
        if round_id == 0: # reverse blinds
            if self.position == 0:
                return 1
            else:
                return 0
        else:
            return self.position

    def _calculate_chips_input(self, chips):
        if len(chips) == 0:
            chips = 0.5
        else:
            chips = numpy.mean(chips)
        return chips