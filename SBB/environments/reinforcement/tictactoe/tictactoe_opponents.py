import random
import numpy
from tictactoe_match import TictactoeMatch
from ..default_opponent import DefaultOpponent
from ....config import Config

class TictactoeRandomOpponent(DefaultOpponent):
    OPPONENT_ID = "random"

    def __init__(self):
        super(TictactoeRandomOpponent, self).__init__(TictactoeRandomOpponent.OPPONENT_ID)

    def initialize(self, seed):
        self.random_generator_ = numpy.random.RandomState(seed=seed)

    def execute(self, point_id_, inputs, valid_actions, is_training):
        return self.random_generator_.choice(valid_actions)

class TictactoeSmartOpponent(DefaultOpponent):
    OPPONENT_ID = "smart"

    def __init__(self):
        super(TictactoeSmartOpponent, self).__init__(TictactoeSmartOpponent.OPPONENT_ID)

    def initialize(self, seed):
        self.random_generator_ = numpy.random.RandomState(seed=seed)

    def execute(self, point_id_, inputs, valid_actions, is_training):
        current_player = 1*Config.RESTRICTIONS['multiply_normalization_by']
        opponent_player = 2*Config.RESTRICTIONS['multiply_normalization_by']

        # check if can win in the next move
        for action in valid_actions:
            copy = list(inputs)
            copy[action] = current_player
            winner = TictactoeMatch.get_winner(copy)
            if winner == current_player:
                return action

        # check if the opponent could win on their next move, and block them
        for action in valid_actions:
            copy = list(inputs)
            copy[action] = opponent_player
            winner = TictactoeMatch.get_winner(copy)
            if winner == opponent_player:
                return action

        # try to take one of the corners
        corners = [0, 2, 6, 8]
        valid_corners = list(set(valid_actions).intersection(corners))
        if valid_corners:
            action = self.random_generator_.choice(valid_corners)
            return action

        # try to take the center
        center = 4
        if center in valid_actions:
            return center

        # get anything that is valid
        action = self.random_generator_.choice(valid_actions)
        return action