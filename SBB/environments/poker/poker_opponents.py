import abc
import random
import numpy
from ..default_opponent import DefaultOpponent

"""

"""

class PokerRandomOpponent(DefaultOpponent):
    OPPONENT_ID = "random"

    def __init__(self):
        super(PokerRandomOpponent, self).__init__(PokerRandomOpponent.OPPONENT_ID)

    def initialize(self, seed):
        self.random_generator_ = numpy.random.RandomState(seed=seed)

    def execute(self, point_id, inputs, valid_actions, is_training):
        return self.random_generator_.choice(valid_actions)

class PokerAlwaysFoldOpponent(DefaultOpponent):
    OPPONENT_ID = "always_fold"

    def __init__(self):
        super(PokerAlwaysFoldOpponent, self).__init__(PokerAlwaysFoldOpponent.OPPONENT_ID)

    def initialize(self, seed):
        pass

    def execute(self, point_id, inputs, valid_actions, is_training):
        return 0

class PokerAlwaysCallOpponent(DefaultOpponent):
    OPPONENT_ID = "always_call"

    def __init__(self):
        super(PokerAlwaysCallOpponent, self).__init__(PokerAlwaysCallOpponent.OPPONENT_ID)

    def initialize(self, seed):
        pass

    def execute(self, point_id, inputs, valid_actions, is_training):
        return 1

class PokerAlwaysRaiseOpponent(DefaultOpponent):
    OPPONENT_ID = "always_raise"

    def __init__(self):
        super(PokerAlwaysRaiseOpponent, self).__init__(PokerAlwaysRaiseOpponent.OPPONENT_ID)

    def initialize(self, seed):
        pass

    def execute(self, point_id, inputs, valid_actions, is_training):
        return 2

class PokerRuleBasedOpponent(DefaultOpponent):

    __metaclass__  = abc.ABCMeta

    def __init__(self, opponent_id, alfa, beta):
        super(PokerRuleBasedOpponent, self).__init__(opponent_id)
        self.alfa_ = alfa
        self.beta_ = beta

    def initialize(self, seed):
        pass

    def execute(self, point_id, inputs, valid_actions, is_training):
        action = 1
        winning_probability = inputs[0]
        if winning_probability >= self.alfa_:
            if winning_probability >= self.beta_:
                action = 2
            else:
                action = 1
        else:
            if inputs[1] > 0.0:
                action = 0
            else:
                action = 1
        if action not in valid_actions:
            action = 1
        return action

class PokerLooseAgressiveOpponent(PokerRuleBasedOpponent):
    OPPONENT_ID = "loose_agressive"
    def __init__(self):
        super(PokerLooseAgressiveOpponent, self).__init__(PokerLooseAgressiveOpponent.OPPONENT_ID, 2.0, 4.0)

class PokerLoosePassiveOpponent(PokerRuleBasedOpponent):
    OPPONENT_ID = "loose_passive"
    def __init__(self):
        super(PokerLoosePassiveOpponent, self).__init__(PokerLoosePassiveOpponent.OPPONENT_ID, 2.0, 8.0)

class PokerTightAgressiveOpponent(PokerRuleBasedOpponent):
    OPPONENT_ID = "tight_agressive"
    def __init__(self):
        super(PokerTightAgressiveOpponent, self).__init__(PokerTightAgressiveOpponent.OPPONENT_ID, 8.0, 8.5)

class PokerTightPassiveOpponent(PokerRuleBasedOpponent):
    OPPONENT_ID = "tight_passive"
    def __init__(self):
        super(PokerTightPassiveOpponent, self).__init__(PokerTightPassiveOpponent.OPPONENT_ID, 8.0, 9.5)