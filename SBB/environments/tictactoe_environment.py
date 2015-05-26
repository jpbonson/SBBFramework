import random
from collections import Counter
import numpy
from sklearn.metrics import confusion_matrix, accuracy_score, recall_score
from default_environment import DefaultEnvironment, DefaultPoint
from ..diversity_maintenance import DiversityMaintenance
from ..pareto_dominance import ParetoDominance
from ..utils.helpers import round_array_to_decimals, flatten, is_nearly_equal_to
from ..config import CONFIG, RESTRICTIONS

class TictactoePoint(DefaultPoint):
    """
    Encapsulates a tictactoe game configuration as a point.
    """

    def __init__(self, point_id):
        super(TictactoePoint, self).__init__(point_id)

    def execute(self, inputs):
        # TODO
        pass

class TictactoeEnvironment(DefaultEnvironment):
    """
    This environment encapsulates all methods to deal with a reinforcement learning task for TicTacToe.
    This is a dummy environment, where the only point in the population is a random player.
    """

    def __init__(self):
        self.total_actions_ = 9 # positions in the board
        self.total_inputs_ = 9 # positions in the board (0, 1, 2 as the states, 0: no player, 1: player 1, 2: player 2)
        self.point_population_ = TictactoePoint("random")
        RESTRICTIONS['total_actions'] = self.total_actions_
        RESTRICTIONS['total_inputs'] = self.total_inputs_
        RESTRICTIONS['action_mapping'] = {
            '[0,0]': 0, '[0,1]': 1, '[0,2]': 2,
            '[1,0]': 3, '[1,1]': 4, '[1,2]': 5,
            '[2,0]': 6, '[2,1]': 7, '[2,2]': 8,
        }
        RESTRICTIONS['use_memmory'] = False # since the point population output is not predictable

    def reset_point_population(self):
        pass

    def setup_point_population(self, teams_population):
        pass

    def evaluate_point_population(self, teams_population):
        pass
                        
    def point_population(self):
        return self.point_population_

    def evaluate_team(self, team, is_training=False):
        outputs = []
        for point in population:
            output = team.execute(self, point.point_id, point.inputs, is_training)
            outputs.append(output)
            if is_training:
                if output == point.output:
                    result = 1 # correct
                else:
                    result = 0 # incorrect
                team.results_per_points_[point.point_id] = result

        score = -1 # TODO
        extra_metrics = {}
        
        if is_training:
            team.fitness_ = score
            team.score_trainingset_ = score
        else:
            team.score_testset_ = score
            team.extra_metrics_ = extra_metrics

    def is_valid_action(self, inputs, action):
        # TODO
        pass

    def metrics(self):
        msg = ""
        msg += "\n### Environment Info:"
        msg += "\ntotal inputs: "+str(self.total_inputs_)
        msg += "\ntotal actions: "+str(self.total_actions_)
        msg += "\nactions mapping: "+str(self.action_mapping_)
        return msg