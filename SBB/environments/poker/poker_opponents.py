import random
import numpy
from ..default_opponent import DefaultOpponent
from ...config import Config

"""
(Andy)
'loose' opponents: always call, always raise, always fold
Next we should have a few opponents that actually consider their starting hand strength (equity) and play a 'reasonable' range of hands.
If we build a couple of opponents that are more likely to engage in hands proportionate to starting equity, i.e., always betting with high equity 
(say >= 0.65), always calling for moderate (0.5 to < 0.65) and fold anything less (assuming a single opponent context) then this will get us a 
basic opponent that will be tough to beat initially.  In other words, we could bias the probabilities of <bet, call, fold> with starting equity 
and let it go from there.  This would cover our 'tight' sample behaviours.  
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