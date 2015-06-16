import abc
from default_environment import DefaultEnvironment, DefaultPoint

class ReinforcementPoint(DefaultPoint):
    """
    
    """
    __metaclass__  = abc.ABCMeta

    def __init__(self, point_id, opponent):
        super(ReinforcementPoint, self).__init__(point_id)
        self.opponent = opponent

class ReinforcementEnvironment(DefaultEnvironment):
    """
    
    """
    __metaclass__  = abc.ABCMeta

    @abc.abstractmethod
    def __init__(self):
        """
        Initialize the environment variables.
        """