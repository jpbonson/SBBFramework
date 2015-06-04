import abc
import random
import numpy
from tictactoe_match import TictactoeMatch

class TictactoeOpponent(object):
    def __init__(self, opponent_id):
        self.opponent_id = opponent_id
        self.seed = random.randint(0, numpy.iinfo(numpy.int32).max + abs(numpy.iinfo(numpy.int32).min))
        self.random_generator = None

    @abc.abstractmethod
    def initialize(self):
        """
        Initialize attributes of the opponent before a match.
        """

    @abc.abstractmethod
    def execute(self, inputs):
        """
        Returns an action for the given inputs.
        """

    def __str__(self):
        return self.opponent_id+":"+str(self.seed)

    def __repr__(self):
        return self.opponent_id+":"+str(self.seed)

class TictactoeRandomOpponent(TictactoeOpponent):
    def __init__(self):
        super(TictactoeRandomOpponent, self).__init__("random")

    def initialize(self):
        self.random_generator = numpy.random.RandomState(seed=self.seed)

    def execute(self, point_id, inputs, valid_actions, is_training):
        return self.random_generator.choice(valid_actions)

class TictactoeSmartOpponent(TictactoeOpponent):
    def __init__(self):
        super(TictactoeSmartOpponent, self).__init__("smart")

    def initialize(self):
        self.random_generator = numpy.random.RandomState(seed=self.seed)

    def execute(self, point_id, inputs, valid_actions, is_training):
        current_player = 1
        opponent_player = 2

        # check if can win in the next move
        for action in valid_actions:
            copy = list(inputs)
            copy[action] = current_player
            winner = TictactoeMatch.get_winner(copy)
            if TictactoeMatch.get_winner(copy) == current_player:
                return action

        # check if the opponent could win on their next move, and block them
        for action in valid_actions:
            copy = list(inputs)
            copy[action] = opponent_player
            if TictactoeMatch.get_winner(copy) == opponent_player:
                return action

        # try to take one of the corners
        corners = [0, 2, 6, 8]
        valid_corners = list(set(valid_actions).intersection(corners))
        if valid_corners:
            return self.random_generator.choice(valid_corners)

        # try to take the center
        center = 4
        if center in valid_actions:
            return center

        # get anything that is valid
        return self.random_generator.choice(valid_actions)