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
        if 2 in valid_actions:
            return 2
        else:
            return 1

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

class PokerBayesianTesterOpponent(PokerRuleBasedOpponent):
    OPPONENT_ID = "bayesian_tester"
    def __init__(self, alfa, beta):
        super(PokerBayesianTesterOpponent, self).__init__(PokerBayesianTesterOpponent.OPPONENT_ID, alfa, beta)
        self.programs = []
        self.extra_metrics_ = {}
        self.results_per_points_for_validation_ = {}
        self.action_sequence_ = {}
        self.last_selected_program_ = None

    def reset_registers(self):
        pass

    def get_behaviors_metrics(self):
        result = {}
        result['agressiveness'] = self.extra_metrics_['agressiveness']
        result['tight_loose'] = self.extra_metrics_['tight_loose']
        result['passive_aggressive'] = self.extra_metrics_['passive_aggressive']
        result['bluffing'] = self.extra_metrics_['bluffing']
        result['normalized_result_mean'] = numpy.mean(self.results_per_points_for_validation_.values())
        result['normalized_result_std'] = numpy.std(self.results_per_points_for_validation_.values())
        return result

    def metrics(self, full_version = False):
        print "hand_played/total_hands: "+str(self.extra_metrics_['hand_played']['validation']/float(self.extra_metrics_['total_hands']['validation']))
        print "won_hands/total_hands: "+str(self.extra_metrics_['won_hands']['validation']/float(self.extra_metrics_['total_hands']['validation']))
        print "won_hands/hand_played: "+str(self.extra_metrics_['won_hands']['validation']/float(self.extra_metrics_['hand_played']['validation']))
        return ""