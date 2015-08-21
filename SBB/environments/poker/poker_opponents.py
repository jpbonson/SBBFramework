import random
import numpy
from ..default_opponent import DefaultOpponent
from ...config import Config

"""

"""

class PokerRandomOpponent(DefaultOpponent):
    def __init__(self):
        super(PokerRandomOpponent, self).__init__("random")

    def initialize(self, seed):
        self.random_generator_ = numpy.random.RandomState(seed=seed)

    def execute(self, point_id, inputs, valid_actions, is_training):
        return self.random_generator_.choice(valid_actions)

class PokerAlwaysFoldOpponent(DefaultOpponent):
    def __init__(self):
        super(PokerAlwaysFoldOpponent, self).__init__("always_fold")

    def initialize(self, seed):
        pass

    def execute(self, point_id, inputs, valid_actions, is_training):
        return 0

class PokerAlwaysCallOpponent(DefaultOpponent):
    def __init__(self):
        super(PokerAlwaysCallOpponent, self).__init__("always_call")

    def initialize(self, seed):
        pass

    def execute(self, point_id, inputs, valid_actions, is_training):
        return 1

class PokerAlwaysRaiseOpponent(DefaultOpponent):
    def __init__(self):
        super(PokerAlwaysRaiseOpponent, self).__init__("always_raise")

    def initialize(self, seed):
        pass

    def execute(self, point_id, inputs, valid_actions, is_training):
        return 2

class PokerRuleBasedOpponent(DefaultOpponent):
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
    def __init__(self):
        super(PokerLooseAgressiveOpponent, self).__init__('loose_agressive', 0.2, 0.4)

class PokerLoosePassiveOpponent(PokerRuleBasedOpponent):
    def __init__(self):
        super(PokerLoosePassiveOpponent, self).__init__('loose_passive', 0.2, 0.8)

class PokerTightAgressiveOpponent(PokerRuleBasedOpponent):
    def __init__(self):
        super(PokerTightAgressiveOpponent, self).__init__('tight_agressive', 0.8, 0.85)

class PokerTightPassiveOpponent(PokerRuleBasedOpponent):
    def __init__(self):
        super(PokerTightPassiveOpponent, self).__init__('tight_passive', 0.8, 0.95)