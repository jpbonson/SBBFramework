import numpy
from collections import defaultdict
from tictactoe_match import TictactoeMatch
from tictactoe_opponents import TictactoeRandomOpponent
from ..default_environment import DefaultEnvironment, DefaultPoint
from ...utils.helpers import round_value
from ...config import Config

class TictactoePoint(DefaultPoint):
    """
    Encapsulates a tictactoe board configuration as a point.
    """

    def __init__(self, point_id, opponent):
        super(TictactoePoint, self).__init__(point_id)
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
        self.total_actions_ = 9 # spaces in the board
        self.total_inputs_ = 9 # spaces in the board (0, 1, 2 as the states, 0: no player, 1: player 1, 2: player 2)
        self.total_positions_ = 2
        self.point_population_ = [TictactoePoint("random0", TictactoeRandomOpponent()), TictactoePoint("random1", TictactoeRandomOpponent())]
        self.action_mapping_ = {
            '[0,0]': 0, '[0,1]': 1, '[0,2]': 2,
            '[1,0]': 3, '[1,1]': 4, '[1,2]': 5,
            '[2,0]': 6, '[2,1]': 7, '[2,2]': 8,
        }
        Config.RESTRICTIONS['total_actions'] = self.total_actions_
        Config.RESTRICTIONS['total_inputs'] = self.total_inputs_
        Config.RESTRICTIONS['action_mapping'] = self.action_mapping_
        Config.RESTRICTIONS['use_memmory'] = False # since the point population output is not predictable

    def reset_point_population(self):
        pass

    def setup_point_population(self, teams_population):
        pass

    def evaluate_point_population(self, teams_population):
        pass
                        
    def point_population(self):
        return self.point_population_

    def evaluate_team(self, team, is_training = False, total_matches = Config.USER['reinforcement_parameters']['training_matches']):
        """
        Each team plays 2 matches against each point in the point population.
        One match as the player 1, another as player 2. The final score is 
        the mean of the scores in the matches (1: win, 0.5: draw, 0: lose)
        """
        results = []
        extra_metrics = {}
        extra_metrics['opponents'] = defaultdict(list)

        for point in self.point_population_:
            outputs = []
            for match_id in range(total_matches):
                for position in range(1, self.total_positions_+1):
                    outputs.append(self._play_match(position, point, team, is_training))
            result = numpy.mean(outputs)
            results.append(result)
            if is_training:
                team.results_per_points_[point.point_id] = result
            else:
                extra_metrics['opponents'][point.opponent.opponent_id].append(result)

        score = numpy.mean(results)
        
        if is_training:
            team.fitness_ = score
            team.score_trainingset_ = score
        else:
            for key in extra_metrics['opponents']:
                extra_metrics['opponents'][key] = round_value(numpy.mean(extra_metrics['opponents'][key]))
            team.score_testset_ = score
            team.extra_metrics_ = extra_metrics

    def _play_match(self, position, point, team, is_training):
        if position == 1:
            first_player = point.opponent
            second_player = team
            sbb_player = 2
        else:
            first_player = team
            second_player = point.opponent
            sbb_player = 1

        match = TictactoeMatch()
        point.opponent.initialize()
        while True:
            player = 1
            inputs = match.inputs_from_the_point_of_view_of(player)
            action = first_player.execute(point.point_id, inputs, match.valid_actions(), is_training)
            match.perform_action(player, action)
            if match.is_over():
                return match.result_for_player(sbb_player)
            player = 2
            inputs = match.inputs_from_the_point_of_view_of(player)
            action = second_player.execute(point.point_id, inputs, match.valid_actions(), is_training)
            match.perform_action(player, action)
            if match.is_over():
                return match.result_for_player(sbb_player)

    def validate(self, current_generation, teams_population):
        for team in teams_population:
            if team.generation != current_generation: # dont evaluate tems that have just being created (to improve performance and to get training metrics)
                self.evaluate_team(team, is_training = False, total_matches = Config.USER['reinforcement_parameters']['test_matches'])
        score = [p.score_testset_ for p in teams_population]
        best_team = teams_population[score.index(max(score))]
        print("\nChampion team test score in the initial matches: "+str(best_team.score_testset_))
        self.evaluate_team(best_team, is_training = False, total_matches = Config.USER['reinforcement_parameters']['champion_matches'])
        return best_team

    def metrics(self):
        msg = ""
        msg += "\n### Environment Info:"
        msg += "\ntotal inputs: "+str(self.total_inputs_)
        msg += "\ntotal actions: "+str(self.total_actions_)
        msg += "\nactions mapping: "+str(self.action_mapping_)
        return msg