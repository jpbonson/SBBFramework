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
        # first action: (0.107, 0.185, 0.708)
        # all actions: (0.02626371649577262, 0.32829645619715775, 0.6454398273070696)

        # old (previous EHS metric, unbalanced, against always_raise):
        # (0.20253164556962025, 0.12025316455696203, 0.6772151898734177)
        # (0.06377551020408163, 0.2461734693877551, 0.6900510204081632)

class PokerLoosePassiveOpponent(PokerRuleBasedOpponent):
    def __init__(self):
        super(PokerLoosePassiveOpponent, self).__init__('loose_passive', 0.2, 0.8)
        # first action: (0.107, 0.7, 0.193)
        # all actions: (0.030004110152075627, 0.729140978216194, 0.24085491163173037)

        # old (previous EHS metric, unbalanced, against always_raise, beta = 0.9):
        # (0.20253164556962025, 0.6645569620253164, 0.13291139240506328)
        # (0.07473841554559044, 0.7309417040358744, 0.19431988041853512)

class PokerTightAgressiveOpponent(PokerRuleBasedOpponent):
    def __init__(self):
        super(PokerTightAgressiveOpponent, self).__init__('tight_agressive', 0.8, 0.82)
        # first action: (0.612, 0.234, 0.154)
        # all actions: (0.29934354485776804, 0.4700218818380744, 0.23063457330415754)

        # old (previous EHS metric, unbalanced, against always_raise, beta = 0.85):
        # (0.7974683544303798, 0.006329113924050633, 0.1962025316455696)
        # (0.5441696113074205, 0.10600706713780919, 0.3498233215547703)

class PokerTightPassiveOpponent(PokerRuleBasedOpponent):
    def __init__(self):
        super(PokerTightPassiveOpponent, self).__init__('tight_passive', 0.8, 0.95)
        # first action: (0.612, 0.365, 0.023)
        # all actions: (0.31161731207289295, 0.6337129840546697, 0.05466970387243736)
        
        # old (previous EHS metric, unbalanced, against always_raise):
        # (0.7974683544303798, 0.15822784810126583, 0.04430379746835443)
        # (0.5877862595419847, 0.2748091603053435, 0.13740458015267176)