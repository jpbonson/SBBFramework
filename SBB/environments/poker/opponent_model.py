import numpy

class OpponentModel():
    """
    ATTENTION: If you change the order, add or remove inputs the SBB teams that were already trained will 
    behave unexpectedly!

    All inputs are normalized, so they influence the SBB player potentially equal,

    inputs[0] = self short-term agressiveness (last 10 hands)
    inputs[1] = self long-term agressiveness
    inputs[2] = opponent short-term agressiveness (last 10 hands)
    inputs[3] = opponent long-term agressiveness
    inputs[4] = self short-term volatility (last 10 hands)
    inputs[5] = self long-term volatility
    inputs[6] = opponent short-term volatility (last 10 hands)
    inputs[7] = opponent long-term volatility
    reference for agressiveness: "Countering Evolutionary Forgetting in No-Limit Texas Hold'em Poker Agents"

    volatility: how frequently the opponent changes its behaviors between pre-flop and post-flop
    formula: (agressiveness pos-flop)-(agressiveness pre-flop) (normalized between 0.0 and 1.0, 
        where 0.5: no volatility, 0.0: get less agressive, 1.0: get more agressive)
    question: isn't expected that most opponents will be less agressive pre-flop and more agressive post-flop? 
    (since they probably got better hands?) may this metric be usefull to identify bluffing?
    """

    INPUTS = ['self short-term agressiveness', 'self long-term agressiveness', 'opponent short-term agressiveness', 
        'opponent long-term agressiveness', 'self short-term volatility', 'self long-term volatility', 
        'opponent short-term volatility', 'opponent long-term volatility']

    def __init__(self):
        self.self_agressiveness = []
        self.opponent_agressiveness = []
        self.self_agressiveness_preflop = []
        self.self_agressiveness_postflop = []
        self.opponent_agressiveness_preflop = []
        self.opponent_agressiveness_postflop = []

    def update_agressiveness(self, total_rounds, self_actions, opponent_actions, self_folded, opponent_folded, previous_action):
        if self_folded:
            if self_actions:
                if self_actions[-1] != 'f':
                    self_actions.append('f')
            else:
                self_actions.append('f')
        if opponent_folded:
            if opponent_actions:
                if opponent_actions[-1] != 'f':
                    opponent_actions.append('f')
            else:
                opponent_actions.append('f')
            if previous_action:
                self_actions.append(previous_action)
        if len(self_actions) > 0:
            agressiveness = self._calculate_points(self_actions)/float(len(self_actions))
            self.self_agressiveness.append(agressiveness)
            if total_rounds == 1:
                self.self_agressiveness_preflop.append(agressiveness)
            else:
                self.self_agressiveness_postflop.append(agressiveness)
        if len(opponent_actions) > 0:
            agressiveness = self._calculate_points(opponent_actions)/float(len(opponent_actions))
            self.opponent_agressiveness.append(agressiveness)
            if total_rounds == 1:
                self.opponent_agressiveness_preflop.append(agressiveness)
            else:
                self.opponent_agressiveness_postflop.append(agressiveness)

    def _calculate_points(self, actions):
        points = 0.0
        for action in actions:
            if action == 'c':
                points += 0.5
            if action == 'r':
                points += 1.0
        return points

    def inputs(self):
        inputs = [0] * len(OpponentModel.INPUTS)
        inputs[4] = 0.5
        inputs[5] = 0.5
        inputs[6] = 0.5
        inputs[7] = 0.5
        if len(self.self_agressiveness) > 0:
            inputs[0] = numpy.mean(self.self_agressiveness[:10])
            inputs[1] = numpy.mean(self.self_agressiveness)
        if len(self.opponent_agressiveness) > 0:
            inputs[2] = numpy.mean(self.opponent_agressiveness[:10])
            inputs[3] = numpy.mean(self.opponent_agressiveness)
        if len(self.self_agressiveness_postflop) > 0 and len(self.self_agressiveness_preflop) > 0:
            inputs[4] = OpponentModel.calculate_volatility(self.self_agressiveness_postflop[:10], self.self_agressiveness_preflop[:10])
            inputs[5] = OpponentModel.calculate_volatility(self.self_agressiveness_postflop, self.self_agressiveness_preflop)
        if len(self.opponent_agressiveness_postflop) > 0 and len(self.opponent_agressiveness_preflop) > 0:
            inputs[6] = OpponentModel.calculate_volatility(self.opponent_agressiveness_postflop[:10], self.opponent_agressiveness_preflop[:10])
            inputs[7] = OpponentModel.calculate_volatility(self.opponent_agressiveness_postflop, self.opponent_agressiveness_preflop)
        return inputs

    @staticmethod
    def calculate_volatility(agressiveness_postflop, agressiveness_preflop):
        return OpponentModel._normalize_volatility(numpy.mean(agressiveness_postflop)-numpy.mean(agressiveness_preflop))

    @staticmethod
    def _normalize_volatility(value):
        return (value+1.0)/2.0