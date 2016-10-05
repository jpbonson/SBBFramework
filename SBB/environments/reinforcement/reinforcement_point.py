import random
from ..default_point import DefaultPoint
from ...config import Config

class ReinforcementPoint(DefaultPoint):

    def __init__(self):
        super(ReinforcementPoint, self).__init__()
        self.seed_ = random.randint(0, Config.RESTRICTIONS['max_seed'])
        self.label_ = 0