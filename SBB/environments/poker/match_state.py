import re
from poker_config import PokerConfig
from ...utils.helpers import round_value
from ...config import Config

class MatchState():

    INPUTS = ['hand strength', 'effective potential', 'pot', 'bet', 'pot odds', 'betting position', 'round', 'chips']

    def __init__(self, point, player_key):
        self.point = point
        self.position = point.players[player_key]['position']
        self.hand_strength = point.players[player_key]['hand_strength']
        self.effective_potential = point.players[player_key]['effective_potential']
        self.round_id = 0
        self.rounds = {}
        self.rounds['preflop'] = []
        self.rounds['flop'] = []
        self.rounds['turn'] = []
        self.rounds['river'] = []

    # def is_current_player_to_act(self):
    #     if len(self.rounds) == 1: # since the game uses reverse blinds
    #         if len(self.rounds[0]) % 2 == 0:
    #             current_player = 1
    #         else:
    #             current_player = 0
    #     else:
    #         if len(self.rounds[-1]) % 2 == 0:
    #             current_player = 0
    #         else:
    #             current_player = 1
    #     if int(self.position) == current_player:
    #         return True
    #     else:
    #         return False

    # def last_player_to_act(self):
    #     if len(self.rounds[-1]) == 0:
    #         last_acted_round = self.rounds[-2]
    #     else:
    #         last_acted_round = self.rounds[-1]
    #     if last_acted_round == self.rounds[0]: # since the game uses reverse blinds
    #         if len(last_acted_round) % 2 == 0:
    #             last_player = 0
    #         else:
    #             last_player = 1
    #     else: # cc/cr/rr 10/01/01
    #         if len(last_acted_round) % 2 == 0:
    #             last_player = 1
    #         else:
    #             last_player = 0
    #     return last_player

    # def is_showdown(self):
    #     if self.opponent_hole_cards:
    #         return True
    #     else:
    #         return False

    # def is_last_action_a_fold(self):
    #     actions = self.rounds[-1]
    #     if len(actions) > 0 and actions[-1] == 'f':
    #         return True
    #     else:
    #         return False

    # def actions_per_player(self):
    #     self_actions = []
    #     opponent_actions = []
    #     for round_index, actions in enumerate(self.rounds):
    #         for action_index, action in enumerate(actions):
    #             if round_index == 0:
    #                 if self.position == 0:
    #                     if action_index % 2 == 0:
    #                         opponent_actions.append(action)
    #                     else:
    #                         self_actions.append(action)
    #                 else:
    #                     if action_index % 2 == 0:
    #                         self_actions.append(action)
    #                     else:
    #                         opponent_actions.append(action)
    #             else:
    #                 if self.position == 0:
    #                     if action_index % 2 == 0:
    #                         self_actions.append(action)
    #                     else:
    #                         opponent_actions.append(action)
    #                 else:
    #                     if action_index % 2 == 0:
    #                         opponent_actions.append(action)
    #                     else:
    #                         self_actions.append(action)
    #     return self_actions, opponent_actions

    def inputs(self, pot, bet, chips):
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
        inputs = [0] * len(MatchState.INPUTS)
        inputs[0] = self.hand_strength[self.round_id]
        inputs[1] = self.effective_potential[self.round_id]
        inputs[2] = pot/float(self.maximum_winning())
        inputs[3] = bet/float(PokerConfig.CONFIG['big_bet'])
        if (pot + bet) > 0:
            inputs[4] = bet / float(pot + bet)
        else:
            inputs[4] = 0.0
        inputs[5] = float(self._betting_position())
        inputs[6] = self.round_id/3.0
        inputs[7] = chips
        inputs = [round_value(i*Config.RESTRICTIONS['multiply_normalization_by']) for i in inputs]
        return inputs

    def simplified_inputs(self, bet):
        inputs = [0] * 2
        inputs[0] = self.hand_strength[self.round_id]
        inputs[1] = bet/float(PokerConfig.CONFIG['big_bet'])
        inputs = [round_value(i*Config.RESTRICTIONS['multiply_normalization_by']) for i in inputs]
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

    def _betting_position(self):
        if self.round_id == 0: # reverse blinds
            if self.position == 0:
                return 1
            else:
                return 0
        else:
            return self.position

    # def valid_actions(self):
    #     """
        
    #     """
    #     valid = [1]
    #     # check if can fold
    #     if len(self.rounds) > 1:
    #         current_round = self.rounds[-1]
    #         if 'r' in current_round:
    #             valid.append(0)
    #     else:
    #         current_round = self.rounds[-1]
    #         if len(current_round) == 0 or 'r' in current_round:
    #             valid.append(0)

    #     # check if can raise
    #     if len(self.rounds) == 1:
    #         max_raises = 3
    #     else:
    #         max_raises = 4
    #     raises = 0
    #     for action in self.rounds[-1]:
    #         if action == 'r':
    #             raises += 1
    #     if raises < max_raises:
    #         valid.append(2)
    #     return valid

    def __str__(self):
        msg = "\n"
        msg += "position: "+str(self.position)+"\n"
        msg += "rounds: "+str(self.rounds)+"\n"
        return msg