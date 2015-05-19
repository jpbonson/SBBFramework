import abc

class DefaultEnvironment():
    __metaclass__  = abc.ABCMeta

    @abc.abstractmethod
    def __init__(self):
        """
        Initialize the environment variables.
        """

    @abc.abstractmethod
    def reset(self):
         """
         Method that is called at the beginning of each run by SBB, to reset the 
         variables that will be used by the generations.
         """

    @abc.abstractmethod
    def setup(self):
         """
         Method that is called at the beginning of each generation by SBB, to set the 
         variables that will be used by the generation.
         """

    @abc.abstractmethod
    def evaluate(self, team, training=False):
        """
        Evaluate the team using the environment inputs. May be executed in the training
        or the test mode.
        """

    @abc.abstractmethod
    def metrics(self):
        """
        Generate a string with the metrics for the environment. It is printed at the 
        start and at the end of the execution, and it is also saved in the output file.
        """