import numpy
from ...utils.helpers import round_value
from ...config import Config

class OpponentModel():
    """
    ATTENTION: If you change the order, add or remove inputs the SBB teams that were already trained will 
    behave unexpectedly!

    All inputs are normalized, so they influence the SBB player equally.

    reference for agressiveness: "Countering Evolutionary Forgetting in No-Limit Texas Hold'em Poker Agents"

    aggressiveness hand tests:
    (tight aggressive): 0.66, ffffffffrrrrrrrrrrrrrrrr
    (loose aggressive): 0.98, ffrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrr
    (tight passive): 0.25, ffffffffcccccccc
    (loose passive): 0.47, ffcccccccccccccccccccccccccccccccc

    tight/loose hand tests:
    - higher number == more hands the team played

    passive/aggressive hand tests:
    - higher number == more raises in relation to calls

    self_bluffing:
    - only calculated for the last round
    - if the player went up to the last round and didn't fold with a weak hand, bluff = 1.0, else 0.0

    """

    INPUTS = ['opp last action', 'opp hand agressiveness', 'opp agressiveness', 'opp tight/loose', 
        'opp passive/aggressive', 'opp bluffing', 'opp short-term agressiveness', 'self short-term agressiveness']

    SINGLE_HAND_AGRESSIVENESS_MAPPING = {'c': 0.0, 'r': 1.0}

    def __init__(self):
        self.self_agressiveness = []
        self.opponent_agressiveness = []
        self.self_tight_loose = []
        self.opponent_tight_loose = []
        self.self_passive_aggressive = []
        self.opponent_passive_aggressive = []
        self.self_bluffing = []
        self.opponent_bluffing = []

    def update_overall_agressiveness(self, round_id, self_actions, opponent_actions, point_label, showdown_happened):
        if len(self_actions) > 0:
            agressiveness = OpponentModel.calculate_points(self_actions)
            self.self_agressiveness.append(agressiveness)
            self.self_passive_aggressive.append(OpponentModel.calculate_points_only_for_call_and_raise(self_actions))
            if round_id == 3:
                if point_label in [6, 7, 8] and 'f' not in self_actions:
                    self.self_bluffing.append(1.0)
                else:
                    self.self_bluffing.append(0.0)
                
        if len(opponent_actions) > 0:
            agressiveness = OpponentModel.calculate_points(opponent_actions)
            self.opponent_agressiveness.append(agressiveness)
            self.opponent_passive_aggressive.append(OpponentModel.calculate_points_only_for_call_and_raise(opponent_actions))
            if showdown_happened:
                if point_label in [2, 5, 8] and 'f' not in opponent_actions:
                    self.opponent_bluffing.append(1.0)
                else:
                    self.opponent_bluffing.append(0.0)

        if round_id > 0:
            self.self_tight_loose.append(1.0)
            self.opponent_tight_loose.append(1.0)
        else:
            if 'f' in self_actions:
                self.self_tight_loose.append(0.0)
                self.opponent_tight_loose.append(1.0)
            else:
                self.self_tight_loose.append(1.0)
                self.opponent_tight_loose.append(0.0)

    def inputs(self, self_actions, opponent_actions):
        inputs = [0.5] * len(OpponentModel.INPUTS)

        if len(opponent_actions) > 0:
            inputs[0] = OpponentModel.calculate_points([opponent_actions[-1]])

        if len(opponent_actions) > 0:
            actions = [OpponentModel.SINGLE_HAND_AGRESSIVENESS_MAPPING[action] for action in opponent_actions]
            inputs[1] = numpy.mean(actions)
        else:
            inputs[1] = 0.0

        if len(self.opponent_agressiveness) > 0:
            inputs[2] = numpy.mean(self.opponent_agressiveness)

        if len(self.opponent_tight_loose) > 0:
            inputs[3] = numpy.mean(self.opponent_tight_loose)

        if len(self.opponent_passive_aggressive) > 0:
            inputs[4] = numpy.mean(self.opponent_passive_aggressive)

        if len(self.opponent_bluffing) > 0:
            inputs[5] = numpy.mean(self.opponent_bluffing)
        else:
            inputs[5] = 0.0

        if len(self.opponent_agressiveness) > 0:
            inputs[6] = numpy.mean(self.opponent_agressiveness[:10])

        if len(self.self_agressiveness) > 0:
            inputs[7] = numpy.mean(self.self_agressiveness[:10])

        inputs = [round_value(i*Config.RESTRICTIONS['multiply_normalization_by']) for i in inputs]
        return inputs

    @staticmethod
    def calculate_points(actions):
        if len(actions) == 0:
            return 0.0
        points = 0.0
        for action in actions:
            if action == 'c':
                points += 0.5
            if action == 'r':
                points += 1.0
        return points/float(len(actions))

    @staticmethod
    def calculate_points_only_for_call_and_raise(actions):
        points = []
        for action in actions:
            if action == 'c':
                points.append(0.0) 
            if action == 'r':
                points.append(1.0)
        if len(points) == 0:
            return 0.5
        return numpy.mean(points)