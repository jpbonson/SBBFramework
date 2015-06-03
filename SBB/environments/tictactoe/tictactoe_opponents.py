import abc
import sys
import random
import numpy

class TictactoeOpponent(object):
    def __init__(self, opponent_id):
        self.opponent_id = opponent_id
        self.seed = random.randint(0, 4294967295) # 4294967295 is the maximum seed number allowed by numpy
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

class TictactoeRandomOpponent(TictactoeOpponent):
    def __init__(self):
        super(TictactoeRandomOpponent, self).__init__("random")

    def initialize(self):
        self.random_generator = numpy.random.RandomState(seed=self.seed)

    def execute(self, point_id, inputs, valid_actions, is_training):
        return self.random_generator.choice(valid_actions)