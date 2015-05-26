import random
from collections import Counter
import numpy
from sklearn.metrics import confusion_matrix, accuracy_score, recall_score
from default_environment import DefaultEnvironment, DefaultPoint
from ..diversity_maintenance import DiversityMaintenance
from ..pareto_dominance import ParetoDominance
from ..utils.helpers import round_array_to_decimals, flatten, is_nearly_equal_to
from ..config import CONFIG, RESTRICTIONS

class TictactoeMatch():
    """

    """

    def __init__(self):
        self.inputs_ = []
        self.result_ = -1
        pass

    def perform_action(self, current_player, action):
        """
        Perform the action for the current_player in the board, modifying 
        the attribute inputs_.
        """
        pass


    def is_valid_action(self, action):
        """
        If the chosen space (represented by the action) is empty, the 
        action is valid. If not, it is invalid.
        """
        # TODO
        return False

    def is_over(self):
        """
        Check if all spaces were used. If yes, sets the attribute result_ with the 
        number of the winner or 0 if a draw occured.
        """
        # TODO
        return False

    def result_for_player(self, current_player):
        if self.result_ == current_player:
            return 1 # win
        if self.result_ == 0:
            return 0.5 # draw
        else:
            return 0 # lose


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
        """
        Each team plays 2 matches against each point in the point population.
        One match as the player 1, another as player 2. The final score is 
        the mean of the scores in the matches (1: win, 0.5: draw, 0: lose)
        """
        results = []
        for point in population:
            outputs = []
            outputs.append(self._play_match(1, team, point, is_training))
            outputs.append(self._play_match(2, team, point, is_training))

            result = numpy.mean(outputs)
            results.append(result)
            if is_training:
                team.results_per_points_[point.point_id] = result

        score = numpy.mean(results)
        extra_metrics = {}
        
        if is_training:
            team.fitness_ = score
            team.score_trainingset_ = score
        else:
            team.score_testset_ = score
            team.extra_metrics_ = extra_metrics

    def _play_match(self, player_number, team, point, is_training):
        current_player = player_number
        if player_number == 1:
            current_opponent = 2
        else:
            current_opponent = 1

        match = TictactoeMatch()
        while not match.is_over():
            action = team.execute(point.point_id, match.inputs_, match.is_valid_action, is_training)
            match.perform_action(current_player, action)
            if match.is_over():
                return match.result_for_player(current_player)
            action = point.execute(match.inputs_, match.is_valid_action)
            match.perform_action(current_opponent, action)
            if match.is_over():
                return match.result_for_player(current_player)
        raise ValueError("The match finished executing without being over. You got a bug!")

    def metrics(self):
        msg = ""
        msg += "\n### Environment Info:"
        msg += "\ntotal inputs: "+str(self.total_inputs_)
        msg += "\ntotal actions: "+str(self.total_actions_)
        msg += "\nactions mapping: "+str(self.action_mapping_)
        return msg