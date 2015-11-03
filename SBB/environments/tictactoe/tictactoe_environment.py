import random
import numpy
from tictactoe_match import TictactoeMatch
from tictactoe_opponents import TictactoeRandomOpponent, TictactoeSmartOpponent
from ..reinforcement_environment import ReinforcementEnvironment, ReinforcementPoint
from ...config import Config

class TictactoePoint(ReinforcementPoint):
    """
    Encapsulates a tictactoe opponent as a point.
    """

    def __init__(self):
        super(TictactoePoint, self).__init__()

class TictactoeEnvironment(ReinforcementEnvironment):
    """
    This environment encapsulates all methods to deal with a reinforcement learning task for TicTacToe.
    """
    def __init__(self):
        total_actions = 9 # spaces in the board
        total_inputs = 9 # spaces in the board (0, 1, 2 as the states, 0: no player, 1: player 1, 2: player 2)
        total_labels = 1 # since no labels are being used, group everything is just one label
        coded_opponents = [TictactoeRandomOpponent, TictactoeSmartOpponent]
        point_class = TictactoePoint
        super(TictactoeEnvironment, self).__init__(total_actions, total_inputs, total_labels, coded_opponents, coded_opponents, point_class)
        self.total_positions_ = 2
        self.action_mapping_ = {
            '[0,0]': 0, '[0,1]': 1, '[0,2]': 2,
            '[1,0]': 3, '[1,1]': 4, '[1,2]': 5,
            '[2,0]': 6, '[2,1]': 7, '[2,2]': 8,
        }

    def _play_match(self, team, opponent, point, mode):
        """

        """
        if mode == Config.RESTRICTIONS['mode']['training']:
            is_training = True
        else:
            is_training = False
        outputs = []
        for position in range(1, self.total_positions_+1):
            if position == 1:
                first_player = opponent
                is_training_for_first_player = False
                second_player = team
                is_training_for_second_player = is_training
                sbb_player = 2
            else:
                first_player = team
                is_training_for_first_player = is_training
                second_player = opponent
                is_training_for_second_player = False
                sbb_player = 1

            match = TictactoeMatch()
            opponent.initialize(point.seed_)
            while True:
                player = 1
                inputs = match.inputs_from_the_point_of_view_of(player)
                action = first_player.execute(point.point_id_, inputs, match.valid_actions(), is_training_for_first_player)
                if action is None:
                    action = random.choice(match.valid_actions())
                if is_training_for_first_player:
                    first_player.action_sequence_['coding1'].append(str(action))
                    first_player.action_sequence_['coding2'].append(str(action))
                    first_player.action_sequence_['coding4'].append(str(action))
                match.perform_action(player, action)
                if match.is_over():
                    result = match.result_for_player(sbb_player)
                    outputs.append(result)
                    team.action_sequence_['coding3'].append(int(result*2))
                    break
                player = 2
                inputs = match.inputs_from_the_point_of_view_of(player)
                action = second_player.execute(point.point_id_, inputs, match.valid_actions(), is_training_for_second_player)
                if action is None:
                    action = random.choice(match.valid_actions())
                if is_training_for_second_player:
                    second_player.action_sequence_['coding1'].append(str(action))
                    second_player.action_sequence_['coding2'].append(str(action))
                    second_player.action_sequence_['coding4'].append(str(action))
                match.perform_action(player, action)
                if match.is_over():
                    result = match.result_for_player(sbb_player)
                    outputs.append(result)
                    team.action_sequence_['coding3'].append(int(result*2))
                    break
        return numpy.mean(outputs)

    def metrics(self):
        msg = ""
        msg += "\n### Environment Info:"
        msg += "\ntotal inputs: "+str(self.total_inputs_)
        msg += "\ntotal actions: "+str(self.total_actions_)
        msg += "\nactions mapping: "+str(self.action_mapping_)
        msg += "\npositions: "+str(self.total_positions_)
        return msg