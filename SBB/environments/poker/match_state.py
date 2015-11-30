import re
from poker_config import PokerConfig
from ...utils.helpers import round_value
from ...config import Config

class MatchState():

    INPUTS = ['hand strength', 'effective potential', 'pot', 'bet', 'pot odds', 'betting position', 'round']

    def __init__(self, point, player_key):
        self.point = point
        self.player_key = player_key
        self.position = point.players[player_key]['position']
        self.hand_strength = point.players[player_key]['hand_strength']
        self.effective_potential = point.players[player_key]['effective_potential']
        self.actions = []

    def inputs(self, pot, bet, round_id):
        """
        inputs[0] = hand strength
        inputs[1] = effective potential
        inputs[2] = pot
        inputs[3] = bet
        inputs[4] = pot odds
        inputs[5] = betting position (0: first betting, 1: last betting)
        inputs[6] = round
        """
        if self.player_key == 'team':
            inputs = [0] * len(MatchState.INPUTS)
            inputs[0] = self.hand_strength[round_id]
            inputs[1] = self.effective_potential[round_id]
            inputs[2] = pot/float(self.maximum_winning())
            inputs[3] = bet/float(PokerConfig.CONFIG['big_bet'])
            if (pot + bet) > 0:
                inputs[4] = bet / float(pot + bet)
            else:
                inputs[4] = 0.0
            inputs[5] = float(self._betting_position(round_id))
            inputs[6] = round_id/3.0
            normalized_inputs = [round_value(i*Config.RESTRICTIONS['multiply_normalization_by']) for i in inputs[2:]]
            return inputs[:2]+normalized_inputs
        else: # inputs for rule-based opponents
            inputs = [0] * 2
            inputs[0] = self.hand_strength[round_id]
            inputs[1] = bet/float(PokerConfig.CONFIG['big_bet'])
            inputs[1] = round_value(inputs[1]*Config.RESTRICTIONS['multiply_normalization_by'])
            return inputs

    # def calculate_pot(self):
    #     # check if is the small blind
    #     if self.round_id == 0:
    #         if len(self.rounds['preflop']) == 0 or (len(self.rounds['preflop']) == 1 and self.rounds['preflop'][0] == 'f'):
    #             return PokerConfig.CONFIG['small_bet']/2.0

    #     # check if someone raised
    #     pot = PokerConfig.CONFIG['small_bet']
    #     for i, r in enumerate(self.rounds):
    #         if i == 0 or i == 1:
    #             bet = PokerConfig.CONFIG['small_bet']
    #         else:
    #             bet = PokerConfig.CONFIG['big_bet']
    #         for action in r:
    #             if action == 'r':
    #                 pot += bet
    #     return pot

    def maximum_winning(self):
        max_small_bet_turn_winning = PokerConfig.CONFIG['small_bet']*4
        max_big_bet_turn_winning = PokerConfig.CONFIG['big_bet']*4
        return max_small_bet_turn_winning*2 + max_big_bet_turn_winning*2

    # def calculate_bet(self):
    #     # check if is the small blind
    #     if len(self.rounds) == 1 and len(self.rounds[0]) == 0:
    #         return 0.5
        
    #     # check if the opponent raised
    #     bet = 0.0
    #     current_round = self.rounds[-1]
    #     if current_round: # if there is previous actions
    #         last_action = current_round[-1]
    #         if last_action == 'r':
    #             bet = 1.0 # since the value is normalized and the poker is limited, 1 means the maximum bet
    #     return bet

    def _betting_position(self, round_id):
        if round_id == 0: # reverse blinds
            if self.position == 0:
                return 1
            else:
                return 0
        else:
            return self.position

    def __str__(self):
        msg = "\n"
        msg += "position: "+str(self.position)+"\n"
        return msg