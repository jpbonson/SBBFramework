import random
import numpy
from tictactoe_match import TictactoeMatch
from tictactoe_opponents import TictactoeRandomOpponent, TictactoeSmartOpponent
from ..reinforcement_environment import ReinforcementEnvironment, ReinforcementPoint

class TictactoePoint(ReinforcementPoint):
    """
    Encapsulates a tictactoe opponent as a point.
    """

    def __init__(self, point_id, opponent):
        super(TictactoePoint, self).__init__(point_id, opponent)

class TictactoeEnvironment(ReinforcementEnvironment):
    """
    This environment encapsulates all methods to deal with a reinforcement learning task for TicTacToe.
    """
    def __init__(self):
        total_actions = 9 # spaces in the board
        total_inputs = 9 # spaces in the board (0, 1, 2 as the states, 0: no player, 1: player 1, 2: player 2)
        coded_opponents = [TictactoeRandomOpponent, TictactoeSmartOpponent]
        super(TictactoeEnvironment, self).__init__(total_actions, total_inputs, coded_opponents, coded_opponents)
        self.total_positions_ = 2
        self.action_mapping_ = {
            '[0,0]': 0, '[0,1]': 1, '[0,2]': 2,
            '[1,0]': 3, '[1,1]': 4, '[1,2]': 5,
            '[2,0]': 6, '[2,1]': 7, '[2,2]': 8,
        }

    def _instantiate_point_for_coded_opponent_class(self, opponent_class):
        instance = opponent_class()
        return TictactoePoint(str(instance), instance)

    def _instantiate_point_for_sbb_opponent(self, team):
        return TictactoePoint(team.__repr__(), team)

    def _play_match(self, team, point, is_training):
        """

        """
        outputs = []
        for position in range(1, self.total_positions_+1):
            if position == 1:
                first_player = point.opponent
                is_training_for_first_player = False
                second_player = team
                is_training_for_second_player = is_training
                sbb_player = 2
            else:
                first_player = team
                is_training_for_first_player = is_training
                second_player = point.opponent
                is_training_for_second_player = False
                sbb_player = 1

            match = TictactoeMatch()
            point.opponent.initialize()
            while True:
                player = 1
                inputs = match.inputs_from_the_point_of_view_of(player)
                action = first_player.execute(point.point_id, inputs, match.valid_actions(), is_training_for_first_player)
                if action is None:
                    action = random.choice(match.valid_actions())
                if is_training_for_first_player:
                    first_player.action_sequence_.append(str(action))
                match.perform_action(player, action)
                if match.is_over():
                    outputs.append(match.result_for_player(sbb_player))
                    break
                player = 2
                inputs = match.inputs_from_the_point_of_view_of(player)
                action = second_player.execute(point.point_id, inputs, match.valid_actions(), is_training_for_second_player)
                if action is None:
                    action = random.choice(match.valid_actions())
                if is_training_for_second_player:
                    second_player.action_sequence_.append(str(action))
                match.perform_action(player, action)
                if match.is_over():
                    outputs.append(match.result_for_player(sbb_player))
                    break
        return numpy.mean(outputs)

    def metrics(self):
        msg = ""
        msg += "\n### Environment Info:"
        msg += "\ntotal inputs: "+str(self.total_inputs_)
        msg += "\ntotal actions: "+str(self.total_actions_)
        msg += "\nactions mapping: "+str(self.action_mapping_)
        msg += "\npositions: "+str(self.total_positions_)
        msg += "\nmatches per opponents (for each position): "+str(self.population_size_)
        return msg