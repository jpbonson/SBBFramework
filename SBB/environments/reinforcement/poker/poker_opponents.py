import abc
import random
import numpy
from collections import Counter
from ..default_opponent import DefaultOpponent

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

class PokerLAAntiPlayerOpponent(PokerRuleBasedOpponent):
    OPPONENT_ID = "LA_antiplayer"
    def __init__(self):
        alfa = 5.0
        beta = 5.0
        super(PokerLAAntiPlayerOpponent, self).__init__(PokerLAAntiPlayerOpponent.OPPONENT_ID, alfa, beta)

class PokerLPAntiPlayerOpponent(PokerRuleBasedOpponent):
    OPPONENT_ID = "LP_antiplayer"
    def __init__(self):
        alfa = 6.0
        beta = 6.0
        super(PokerLPAntiPlayerOpponent, self).__init__(PokerLPAntiPlayerOpponent.OPPONENT_ID, alfa, beta)

class PokerTAAntiPlayerOpponent(PokerRuleBasedOpponent):
    OPPONENT_ID = "TA_antiplayer"
    def __init__(self):
        alfa = 2.0
        beta = 2.0
        super(PokerTAAntiPlayerOpponent, self).__init__(PokerTAAntiPlayerOpponent.OPPONENT_ID, alfa, beta)

class PokerTPAntiPlayerOpponent(PokerRuleBasedOpponent):
    OPPONENT_ID = "TP_antiplayer"
    def __init__(self):
        alfa = 2.0
        beta = 2.0
        super(PokerTPAntiPlayerOpponent, self).__init__(PokerTPAntiPlayerOpponent.OPPONENT_ID, alfa, beta)

class PokerBayesianOpponent(DefaultOpponent):

    """
    1. analyse opponent's past actions
    2. determine opponent's play style
    3. perform anti-player actions
    """

    OPPONENT_ID = "bayesian_opponent"

    def __init__(self, balanced=True):
        super(PokerBayesianOpponent, self).__init__(PokerBayesianOpponent.OPPONENT_ID)
        action_prob_from_paper = {
            'tp': {
                'f': 0.87,                'c': 0.07,                'r': 0.06,
            },
            'ta': {
                'f': 0.73,                'c': 0.02,                'r': 0.25,
            },
            'lp': {
                'f': 0.6,                 'c': 0.29,                'r': 0.11,
            },
            'la': {
                'f': 0.36,                'c': 0.05,                'r': 0.59,
            }
        }
        action_prob_from_tests_with_3bets = {
            'tp': {
                'f': 0.38,                'c': 0.55,                'r': 0.07,
            },
            'ta': {
                'f': 0.4,                'c': 0.37,                'r': 0.23,
            },
            'lp': {
                'f': 0.05,                'c': 0.75,                'r': 0.2,
            },
            'la': {
                'f': 0.05,                'c': 0.46,                'r': 0.49,
            }
        }
        action_prob_from_tests_with_4bets = {
            'la': {
                'f': 0.053,                'c': 0.43,                'r': 0.517,
            },
            'lp': {
                'f': 0.047,                'c': 0.728,                'r': 0.225,
            },
            'ta': {
                'f': 0.373,                'c': 0.357,                'r': 0.270,
            },
            'tp': {
                'f': 0.355,                'c': 0.559,                'r': 0.086,
            }
        }
        self.action_prob = action_prob_from_tests_with_4bets
        self.antiplayers = {
            'tp': PokerTPAntiPlayerOpponent(balanced),
            'ta': PokerTAAntiPlayerOpponent(balanced),
            'lp': PokerLPAntiPlayerOpponent(balanced),
            'la': PokerLAAntiPlayerOpponent(balanced),
        }
        self.programs = []
        self.extra_metrics_ = {}
        self.results_per_points_for_validation_ = {}
        self.encodings_ = {}
        self.last_selected_program_ = None
        self.opponent_past_actions_history = []
        self.initial_prob = {
            'tp': 0.25,
            'ta': 0.25,
            'lp': 0.25,
            'la': 0.25,
        }

    def initialize(self, seed):
        pass

    def update_opponent_actions(self, opponent_actions):
        self.opponent_past_actions_history += opponent_actions
        for opp_action in opponent_actions:
            temp = {}
            for key in self.initial_prob.keys():
                temp[key] = self.action_prob[key][opp_action] * self.initial_prob[key]

            normalization_param = sum(temp.values())
            for key in self.initial_prob.keys():
                temp[key] /= normalization_param
                self.initial_prob[key] = temp[key]

    def execute(self, point_id, inputs, valid_actions, is_training):
        play_style = max(self.initial_prob.iterkeys(), key=(lambda key: self.initial_prob[key]))
        action = self.antiplayers[play_style].execute(point_id, inputs, valid_actions, is_training)
        return action

    def reset_registers(self):
        pass