import numpy
from ...config import Config

class OpponentModel():
    """
    ATTENTION: If you change the order, add or remove inputs the SBB teams that were already trained will 
    behave unexpectedly!

    All inputs are normalized, so they influence the SBB player potentially equal,

    inputs[0] = opponent last action
    inputs[1] = opponent hand agressiveness
    inputs[2] = opponent long-term agressiveness
    inputs[3] = opponent short-term agressiveness (last 10 hands)
    inputs[4] = opponent long-term volatility
    inputs[5] = opponent short-term volatility (last 10 hands)
    inputs[6] = opponent long-term tight/loose
    inputs[7] = opponent short-term tight/loose (last 10 hands)
    inputs[8] = opponent long-term passive/aggressive
    inputs[9] = opponent short-term passive/aggressive (last 10 hands)
    inputs[10] = self long-term agressiveness
    inputs[11] = self short-term agressiveness (last 10 hands)
    inputs[12] = self long-term volatility
    inputs[13] = self short-term volatility (last 10 hands)
    inputs[14] = self long-term tight/loose
    inputs[15] = self short-term tight/loose (last 10 hands)
    inputs[16] = self long-term passive/aggressive
    inputs[17] = self short-term passive/aggressive (last 10 hands)
    reference for agressiveness: "Countering Evolutionary Forgetting in No-Limit Texas Hold'em Poker Agents"

    volatility: how frequently the opponent changes its behaviors between pre-flop and post-flop
    formula: (agressiveness pos-flop)-(agressiveness pre-flop) (normalized between 0.0 and 1.0, 
        where 0.5: no volatility, 0.0: get less agressive, 1.0: get more agressive)
    question: isn't expected that most opponents will be less agressive pre-flop and more agressive post-flop? 
    (since they probably got better hands?) may this metric be usefull to identify bluffing?

    volatility hand tests:
    (tight aggressive): (1.0-0.1 + 1.0)/2.0 = 0.95
    (loose aggressive): (1.0-0.9 + 1.0)/2.0 = 0.55
    (tight passive): (0.5-0.1 + 1.0)/2.0 = 0.7
    (loose passive): (0.5-0.4 + 1.0)/2.0 = 0.55
    (dumb): (0.1-1.0 + 1.0)/2.0 = 0.05

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

    INPUTS = ['opponent last action (0)', 'opponent hand agressiveness (1)',
        'opponent long-term agressiveness (2)', 'opponent short-term agressiveness (3)',
        'opponent long-term volatility (4)', 'opponent short-term volatility (5)',
        'opponent long-term tight/loose (6)', 'opponent short-term tight/loose (7)',
        'opponent long-term passive/aggressive (8)', 'opponent short-term passive/aggressive (9)']
    #     ,
    #     'self long-term agressiveness (10)', 'self short-term agressiveness (11)', 
    #     'self long-term volatility (12)', 'self short-term volatility (13)',
    #     'self long-term tight/loose (14)', 'self short-term tight/loose (15)',
    #     'self long-term passive/aggressive (16)', 'self short-term passive/aggressive (17)',
    # ]
    SINGLE_HAND_AGRESSIVENESS_MAPPING = {'c': 0.0, 'r': 1.0}

    def __init__(self):
        self.self_agressiveness = []
        self.opponent_agressiveness = []
        self.self_agressiveness_preflop = []
        self.self_agressiveness_postflop = []
        self.opponent_agressiveness_preflop = []
        self.opponent_agressiveness_postflop = []
        self.last_opponent_action_in_last_hand = None
        self.self_tight_loose = []
        self.opponent_tight_loose = []
        self.self_passive_aggressive = []
        self.opponent_passive_aggressive = []
        self.self_bluffing = []

    def update_overall_agressiveness(self, total_rounds, self_actions, opponent_actions, point_label):
        if len(self_actions) > 0:
            agressiveness = OpponentModel.calculate_points(self_actions)
            self.self_agressiveness.append(agressiveness)
            if total_rounds == 1:
                self.self_agressiveness_preflop.append(agressiveness)
            else:
                self.self_agressiveness_postflop.append(agressiveness)
            self_passive_aggressive = OpponentModel.calculate_points_only_for_call_and_raise(self_actions)
            self.self_passive_aggressive.append(self_passive_aggressive)
            if total_rounds == 4:
                if point_label in ['20', '21', '22'] and 'f' not in self_actions:
                    self.self_bluffing.append(1.0)
                else:
                    self.self_bluffing.append(0.0)
                
        if len(opponent_actions) > 0:
            agressiveness = OpponentModel.calculate_points(opponent_actions)
            self.opponent_agressiveness.append(agressiveness)
            if total_rounds == 1:
                self.opponent_agressiveness_preflop.append(agressiveness)
            else:
                self.opponent_agressiveness_postflop.append(agressiveness)
            self.last_opponent_action_in_last_hand = OpponentModel.calculate_points([opponent_actions[-1]])
            self.opponent_passive_aggressive.append(OpponentModel.calculate_points_only_for_call_and_raise(opponent_actions))
        if total_rounds > 1:
            self.self_tight_loose.append(1.0)
            self.opponent_tight_loose.append(1.0)
        else:
            self.self_tight_loose.append(0.0)
            self.opponent_tight_loose.append(0.0)

    def inputs(self, match_state):
        inputs = [0.5] * len(OpponentModel.INPUTS)

        self_actions, opponent_actions = match_state.actions_per_player()
        if len(opponent_actions) > 0:
            inputs[0] = OpponentModel.calculate_points([opponent_actions[-1]])
        elif self.last_opponent_action_in_last_hand is not None:
            inputs[0] = self.last_opponent_action_in_last_hand
        else:
            inputs[0] = 0.5

        if len(opponent_actions) == 0:
            inputs[1] = 0.0
        else:
            actions = [OpponentModel.SINGLE_HAND_AGRESSIVENESS_MAPPING[action] for action in opponent_actions]
            inputs[1] = numpy.mean(actions)

        if len(self.opponent_agressiveness) > 0:
            inputs[2] = numpy.mean(self.opponent_agressiveness)
            inputs[3] = numpy.mean(self.opponent_agressiveness[:10])

        if len(self.opponent_agressiveness_postflop) > 0 and len(self.opponent_agressiveness_preflop) > 0:
            inputs[4] = OpponentModel.calculate_volatility(self.opponent_agressiveness_postflop, self.opponent_agressiveness_preflop)
            inputs[5] = OpponentModel.calculate_volatility(self.opponent_agressiveness_postflop[:10], self.opponent_agressiveness_preflop[:10])

        if len(self.opponent_tight_loose) > 0:
            inputs[6] = numpy.mean(self.opponent_tight_loose)
            inputs[7] = numpy.mean(self.opponent_tight_loose[:10])

        if len(self.opponent_passive_aggressive) > 0:
            inputs[8] = numpy.mean(self.opponent_passive_aggressive)
            inputs[9] = numpy.mean(self.opponent_passive_aggressive[:10])

        # if len(self.self_agressiveness) > 0:
        #     inputs[10] = numpy.mean(self.self_agressiveness)
        #     inputs[11] = numpy.mean(self.self_agressiveness[:10])

        # if len(self.self_agressiveness_postflop) > 0 and len(self.self_agressiveness_preflop) > 0:
        #     inputs[12] = OpponentModel.calculate_volatility(self.self_agressiveness_postflop, self.self_agressiveness_preflop)
        #     inputs[13] = OpponentModel.calculate_volatility(self.self_agressiveness_postflop[:10], self.self_agressiveness_preflop[:10])

        # if len(self.self_tight_loose) > 0:
        #     inputs[14] = numpy.mean(self.self_tight_loose)
        #     inputs[15] = numpy.mean(self.self_tight_loose[:10])

        # if len(self.self_passive_aggressive) > 0:
        #     inputs[16] = numpy.mean(self.self_passive_aggressive)
        #     inputs[17] = numpy.mean(self.self_passive_aggressive[:10])

        # opponent bluff: default 0

        inputs = [i*Config.RESTRICTIONS['multiply_normalization_by'] for i in inputs]
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

    @staticmethod
    def calculate_volatility(agressiveness_postflop, agressiveness_preflop):
        return OpponentModel._normalize_volatility(numpy.mean(agressiveness_postflop)-numpy.mean(agressiveness_preflop))

    @staticmethod
    def _normalize_volatility(value):
        return (value+1.0)/2.0