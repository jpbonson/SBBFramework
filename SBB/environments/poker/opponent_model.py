import numpy
from ...config import Config

class OpponentModel():
    """
    ATTENTION: If you change the order, add or remove inputs the SBB teams that were already trained will 
    behave unexpectedly!

    All inputs are normalized, so they influence the SBB player potentially equal,

    inputs[0] = opponent long-term agressiveness
    inputs[1] = opponent short-term agressiveness (last 10 hands)
    inputs[2] = opponent hand agressiveness
    # inputs[3] = opponent last action
    # inputs[4] = self long-term agressiveness
    # inputs[5] = self short-term agressiveness (last 10 hands)
    # inputs[6] = self short-term volatility (last 10 hands)
    # inputs[7] = self long-term volatility
    # inputs[8] = opponent short-term volatility (last 10 hands)
    # inputs[9] = opponent long-term volatility
    reference for agressiveness: "Countering Evolutionary Forgetting in No-Limit Texas Hold'em Poker Agents"

    volatility: how frequently the opponent changes its behaviors between pre-flop and post-flop
    formula: (agressiveness pos-flop)-(agressiveness pre-flop) (normalized between 0.0 and 1.0, 
        where 0.5: no volatility, 0.0: get less agressive, 1.0: get more agressive)
    question: isn't expected that most opponents will be less agressive pre-flop and more agressive post-flop? 
    (since they probably got better hands?) may this metric be usefull to identify bluffing?
    """

    # INPUTS = ['opponent long-term agressiveness', 'opponent short-term agressiveness', 
    #     'opponent hand agressiveness', 'opponent last action', 'self long-term agressiveness',
    #     'self short-term agressiveness', 'self short-term volatility', 'self long-term volatility', 
    #     'opponent short-term volatility', 'opponent long-term volatility']
    INPUTS = ['opponent long-term agressiveness', 'opponent short-term agressiveness', 
        'opponent hand agressiveness']
    SINGLE_HAND_AGRESSIVENESS_MAPPING = {'c': 0.0, 'r': 1.0}

    def __init__(self):
        self.self_agressiveness = []
        self.opponent_agressiveness = []
        self.self_agressiveness_preflop = []
        self.self_agressiveness_postflop = []
        self.opponent_agressiveness_preflop = []
        self.opponent_agressiveness_postflop = []
        self.last_opponent_action_in_last_hand = None

    def update_overall_agressiveness(self, total_rounds, self_actions, opponent_actions):
        if len(self_actions) > 0:
            agressiveness = OpponentModel.calculate_points(self_actions)
            self.self_agressiveness.append(agressiveness)
            if total_rounds == 1:
                self.self_agressiveness_preflop.append(agressiveness)
            else:
                self.self_agressiveness_postflop.append(agressiveness)
        if len(opponent_actions) > 0:
            agressiveness = OpponentModel.calculate_points(opponent_actions)
            self.opponent_agressiveness.append(agressiveness)
            if total_rounds == 1:
                self.opponent_agressiveness_preflop.append(agressiveness)
            else:
                self.opponent_agressiveness_postflop.append(agressiveness)
            self.last_opponent_action_in_last_hand = OpponentModel.calculate_points([opponent_actions[-1]])

    def inputs(self, match_state):
        inputs = [0.5] * len(OpponentModel.INPUTS)
        if len(self.opponent_agressiveness) > 0:
            inputs[0] = numpy.mean(self.opponent_agressiveness)
            inputs[1] = numpy.mean(self.opponent_agressiveness[:10])

        self_actions, opponent_actions = match_state.actions_per_player()
        if len(opponent_actions) == 0:
            inputs[2] = 0.0
        else:
            actions = [OpponentModel.SINGLE_HAND_AGRESSIVENESS_MAPPING[action] for action in opponent_actions]
            inputs[2] = numpy.mean(actions)

        # if len(opponent_actions) > 0:
        #     inputs[3] = OpponentModel.calculate_points([opponent_actions[-1]])
        # elif self.last_opponent_action_in_last_hand is not None:
        #     inputs[3] = self.last_opponent_action_in_last_hand
        # else:
        #     inputs[3] = 0.5

        # if len(self.self_agressiveness) > 0:
        #     inputs[4] = numpy.mean(self.self_agressiveness)
        #     inputs[5] = numpy.mean(self.self_agressiveness[:10])

        # if len(self.self_agressiveness_postflop) > 0 and len(self.self_agressiveness_preflop) > 0:
        #     inputs[6] = OpponentModel.calculate_volatility(self.self_agressiveness_postflop[:10], self.self_agressiveness_preflop[:10])
        #     inputs[7] = OpponentModel.calculate_volatility(self.self_agressiveness_postflop, self.self_agressiveness_preflop)
        # if len(self.opponent_agressiveness_postflop) > 0 and len(self.opponent_agressiveness_preflop) > 0:
        #     inputs[8] = OpponentModel.calculate_volatility(self.opponent_agressiveness_postflop[:10], self.opponent_agressiveness_preflop[:10])
        #     inputs[9] = OpponentModel.calculate_volatility(self.opponent_agressiveness_postflop, self.opponent_agressiveness_preflop)
        
        inputs = [i*Config.RESTRICTIONS['multiply_normalization_by'] for i in inputs]
        return inputs

    @staticmethod
    def calculate_points(actions):
        points = 0.0
        for action in actions:
            if action == 'c':
                points += 0.5
            if action == 'r':
                points += 1.0
        if float(len(actions)) > 0:
            return points/float(len(actions))
        else:
            return 0.0

    @staticmethod
    def calculate_volatility(agressiveness_postflop, agressiveness_preflop):
        return OpponentModel._normalize_volatility(numpy.mean(agressiveness_postflop)-numpy.mean(agressiveness_preflop))

    @staticmethod
    def _normalize_volatility(value):
        return (value+1.0)/2.0