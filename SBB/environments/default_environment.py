import abc
from ..config import Config

class DefaultPoint(object):
    """
    Encapsulates a value from the environment as a point.
    """

    def __init__(self, point_id):
        self.point_id = point_id

    def __repr__(self): 
        return "("+str(self.point_id)+")"

    def __str__(self): 
        return "("+str(self.point_id)+")"

class DefaultEnvironment(object):
    """
    Abstract class for environments. All environments must implement these 
    methods to be able to work with SBB.
    """
    __metaclass__  = abc.ABCMeta

    MODE = {
        'training': 0,
        'validation': 1,
        'champion': 2,
    }

    @abc.abstractmethod
    def __init__(self):
        """
        Initialize the environment variables.
        """
        self.point_population_ = None

    @abc.abstractmethod
    def reset_point_population(self):
         """
         Method that is called at the beginning of each run by SBB, to reset the 
         variables that will be used by the generations.
         """

    @abc.abstractmethod
    def setup_point_population(self, teams_population):
         """
         Method that is called at the beginning of each generation by SBB, to set the 
         variables that will be used by the generationand remove the ones that are no 
         longer being used.
         """

    @abc.abstractmethod
    def evaluate_point_population(self, teams_population):
        """
        Evaluate the fitness of the point population, to define which points will be removed 
        or added in the next generation, when setup_point_population() is executed.
        """

    @abc.abstractmethod
    def evaluate_team(self, team, mode):
        """
        Evaluate the team using the environment inputs. May be executed in the training
        or the test mode.
        This method must set the attribute results_per_points of the team, if you intend to 
        use pareto.
        """

    @abc.abstractmethod
    def validate(self, current_generation, teams_population):
        """
        Return the best team for the teams_population using the validation set. It must 
        also set the team.score_testset_ and, if necessary, team.extra_metrics_
        """

    @abc.abstractmethod
    def metrics(self):
        """
        Generate a string with the metrics for the environment. It is printed at the 
        start and at the end of the execution, and it is also saved in the output file.
        """

    def _check_for_bugs(self):
        if len(self.point_population_) != Config.USER['training_parameters']['populations']['points']:
            raise ValueError("The size of the points population changed during selection! You got a bug! (it is: "+str(len(self.point_population_))+", should be: "+str(Config.USER['training_parameters']['populations']['points'])+")")