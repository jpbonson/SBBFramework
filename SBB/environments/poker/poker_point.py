from poker_config import PokerConfig
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
        self.position_ = info['pos']
        self.board_cards_ = info['bc']
        self.point_id_ = str(self.seed_)+"-"+str(self.position_)
        self.hand_strength_ = info['p']['str']
        self.ep_ = info['p']['ep']
        self.hole_cards_ = info['p']['hc']
        self.opp_hand_strength_ = info['o']['str']
        self.opp_ep_ = info['o']['ep']
        self.opp_hole_cards_ = info['o']['hc']

        if self.hand_strength_[3] > self.opp_hand_strength_[3]:
            self.sbb_sd_label_ = 0
        elif self.hand_strength_[3] < self.opp_hand_strength_[3]:
            self.sbb_sd_label_ = 2
        else:
            self.sbb_sd_label_ = 1

        self.last_validation_opponent_id_ = None
        self.teams_results_ = []

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

    def __repr__(self):
        return "("+str(self.point_id_)+":"+str(self.label_)+")"

    def __str__(self):
        return "("+str(self.point_id_)+":"+str(self.label_)+")"
