import numpy
from ..default_environment import DefaultEnvironment, DefaultPoint
from ...config import CONFIG, RESTRICTIONS
from tictactoe_match import TictactoeMatch
from tictactoe_opponents import TictactoeRandomOpponent

class TictactoePoint(DefaultPoint):
    """
    Encapsulates a tictactoe board configuration as a point.
    """

    def __init__(self, point_id, player_position, opponent):
        super(TictactoePoint, self).__init__(point_id)
        self.player_position = player_position
        self.opponent = opponent

class TictactoeEnvironment(DefaultEnvironment):
    """
    This environment encapsulates all methods to deal with a reinforcement learning task for TicTacToe.
    This is a dummy environment, where the only point in the population is a random player.

    Observations:
    - Uses the same point population for training and testing.
    - The point population is fixed.
    """

    def __init__(self):
        self.total_actions_ = 9 # positions in the board
        self.total_inputs_ = 9 # positions in the board (0, 1, 2 as the states, 0: no player, 1: player 1, 2: player 2)
        self.point_population_ = [TictactoePoint("random0", 0, TictactoeRandomOpponent()), TictactoePoint("random1", 1, TictactoeRandomOpponent())]
        self.action_mapping_ = {
            '[0,0]': 0, '[0,1]': 1, '[0,2]': 2,
            '[1,0]': 3, '[1,1]': 4, '[1,2]': 5,
            '[2,0]': 6, '[2,1]': 7, '[2,2]': 8,
        }
        RESTRICTIONS['total_actions'] = self.total_actions_
        RESTRICTIONS['total_inputs'] = self.total_inputs_
        RESTRICTIONS['action_mapping'] = self.action_mapping_
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
        for point in self.point_population_:
            outputs = []
            for match_id in range(CONFIG['reinforcement_parameters']['total_matches']):
                outputs.append(self._play_match(point, team, is_training))
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

    def _play_match(self, point, team, is_training):
        if point.player_position == 1:
            first_player = team
            first_player_id = 1
            second_player = point.opponent
            second_player_id = 2
        else:
            first_player = point.opponent
            first_player_id = 2
            second_player = team
            second_player_id = 1

        match = TictactoeMatch()
        while not match.is_over():
            action = first_player.execute(point.point_id, match.inputs_, match.is_valid_action, is_training)
            match.perform_action(first_player_id, action)
            if match.is_over():
                return match.result_for_player(point.player_position)
            action = second_player.execute(point.point_id, match.inputs_, match.is_valid_action, is_training)
            match.perform_action(second_player_id, action)
            if match.is_over():
                return match.result_for_player(point.player_position)
        raise ValueError("The match finished executing without being over. You got a bug!")

    def metrics(self):
        msg = ""
        msg += "\n### Environment Info:"
        msg += "\ntotal inputs: "+str(self.total_inputs_)
        msg += "\ntotal actions: "+str(self.total_actions_)
        msg += "\nactions mapping: "+str(self.action_mapping_)
        return msg