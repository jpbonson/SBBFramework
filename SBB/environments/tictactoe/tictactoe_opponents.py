import abc
import random

class TictactoeOpponent(object):
    def __init__(self, opponent_id):
        self.opponent_id = opponent_id

    @abc.abstractmethod
    def execute(self, inputs):
        """
        Returns an action for the given inputs.
        """

class TictactoeRandomOpponent(TictactoeOpponent):
    def __init__(self):
        super(TictactoeRandomOpponent, self).__init__("random")

    @abc.abstractmethod
    def execute(self, point_id, inputs, valid_actions, is_training):
        return random.choice(valid_actions)