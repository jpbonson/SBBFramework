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
    def execute(self, point_id, inputs, is_valid_action, is_training):
        while True:
            action = random.randint(0, len(inputs)-1)
            if is_valid_action(action):
                return action