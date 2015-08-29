from ..reinforcement_environment import ReinforcementPoint
from ...config import Config

class PokerPoint(ReinforcementPoint):
    """
    Encapsulates a poker opponent, seeded hand, and position as a point.
    """

    INPUTS = ['hand strength', 'effective potential']

    def __init__(self, label, info):
        super(PokerPoint, self).__init__()
        self.label_ = label
        self.seed_ = info['id']
        self.position_ = info['p']
        self.showdown_result_ = info['r']
        self.hand_strength_ = info['str']
        self.ep_ = info['ep']

        self.opp_hand_strength_ = info['ostr']
        self.opp_ep_ = info['oep']
        if Config.USER['reinforcement_parameters']['poker']['balance_based_on'] == 'hole_cards_strength':
            self.opp_label_ = self._label(info['str'][0])
            self.opp_extra_label_ = self._label(info['str'][3])
        else:
            self.opp_label_ = self._label(info['str'][3])
            self.opp_extra_label_ = self._label(info['str'][0])

        if Config.USER['reinforcement_parameters']['poker']['balance_based_on'] == 'hole_cards_strength':
            self.sbb_extra_label_ = self._label(info['str'][3])
        else:
            self.sbb_extra_label_ = self._label(info['str'][0])

        if info['r'] == 0.0:
            self.sbb_sd_label_ = 0
        elif info['r'] == 0.5:
            self.sbb_sd_label_ = 1
        elif info['r'] == 1.0:
            self.sbb_sd_label_ = 2

        self.last_validation_opponent_id_ = None
        self.teams_results_ = []

    def _label(self, value): # TODO: refactor
        if value >= 0.9:
            return 0
        if value >= 0.7:
            return 1
        if value >= 0.4:
            return 2
        return 3

    def inputs(self, round_id):
        """
        inputs[0] = hand_strength
        inputs[1] = effective potential
        """
        inputs = [0] * len(PokerPoint.INPUTS)
        inputs[0] = self.hand_strength_[round_id-1]
        inputs[1] = self.ep_[round_id-1]
        return inputs

    def inputs_for_opponent(self, round_id):
        """
        inputs[0] = hand_strength
        inputs[1] = effective potential
        """
        inputs = [0] * len(PokerPoint.INPUTS)
        inputs[0] = self.opp_hand_strength_[round_id-1]
        inputs[1] = self.opp_ep_[round_id-1]
        return inputs

    def winner_of_showdown(self):
        if self.showdown_result_ == 0.5:
            return None # draw
        if self.showdown_result_ == 0.0:
            if self.position_ == 0:
                return 1
            else:
                return 0
        if self.showdown_result_ == 1.0:
            return self.position_
        raise ValueError("Bug! The code should have finished in the lines above!")        

    def __str__(self):
        return "("+str(self.point_id_)+","+str(self.seed_)+","+str(self.position_)+","+str(self.label_)+")"
