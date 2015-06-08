import abc
import random
import numpy
from ..config import Config

class DefaultOpponent(object):
    def __init__(self, opponent_id):
        self.opponent_id = opponent_id

    @abc.abstractmethod
    def initialize(self):
        """
        Initialize attributes of the opponent before a match.
        """

    @abc.abstractmethod
    def execute(self, point_id, inputs, valid_actions, is_training):
        """
        Returns an action for the given inputs provided by the environment.
        """

    def __str__(self):
        return self.opponent_id