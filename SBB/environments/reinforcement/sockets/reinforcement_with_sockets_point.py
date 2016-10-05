from ..reinforcement_point import ReinforcementPoint

class ReinforcementWithSocketsPoint(ReinforcementPoint):
    
    def __init__(self, label):
        super(ReinforcementWithSocketsPoint, self).__init__()
        self.label_ = label