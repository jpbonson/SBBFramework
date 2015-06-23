import random
import numpy
from poker_match import PokerMatch
from poker_opponents import PokerRandomOpponent
from ..reinforcement_environment import ReinforcementEnvironment, ReinforcementPoint

class PokerPoint(ReinforcementPoint):
    """
    Encapsulates a tictactoe board configuration as a point.
    """

    def __init__(self, point_id, opponent):
        super(PokerPoint, self).__init__(point_id, opponent)

class PokerEnvironment(ReinforcementEnvironment):
    """
    This environment encapsulates all methods to deal with a reinforcement learning task for TicTacToe.
    """
    def __init__(self):
        total_actions = 3 # call, fold, raise
        total_inputs = None # TODO
        coded_opponents = [PokerRandomOpponent] # TODO more opponents
        super(PokerEnvironment, self).__init__(total_actions, total_inputs, coded_opponents)
        self.total_positions_ = 2
        self.action_mapping_ = {'call': 0, 'fold': 1, 'raise': 2}

    def instantiate_point_for_coded_opponent_class(self, opponent_class):
        """
        
        """
        instance = opponent_class()
        return PokerPoint(str(instance), instance)

    def instantiate_point_for_sbb_opponent(self, team):
        """
        
        """
        return PokerPoint(team.__repr__(), team)

    def play_match(self, team, point, is_training):
        """

        """
        outputs = []
        # TODO
        # for position in range(1, self.total_positions_+1):
        #     if position == 1:
        #         first_player = point.opponent
        #         is_training_for_first_player = False
        #         second_player = team
        #         is_training_for_second_player = is_training
        #         sbb_player = 2
        #     else:
        #         first_player = team
        #         is_training_for_first_player = is_training
        #         second_player = point.opponent
        #         is_training_for_second_player = False
        #         sbb_player = 1

        #     match = TictactoeMatch()
        #     point.opponent.initialize()
        #     while True:
        #         player = 1
        #         inputs = match.inputs_from_the_point_of_view_of(player)
        #         action = first_player.execute(point.point_id, inputs, match.valid_actions(), is_training_for_first_player)
        #         if action is None:
        #             action = random.choice(match.valid_actions())
        #         match.perform_action(player, action)
        #         if match.is_over():
        #             outputs.append(match.result_for_player(sbb_player))
        #             break
        #         player = 2
        #         inputs = match.inputs_from_the_point_of_view_of(player)
        #         action = second_player.execute(point.point_id, inputs, match.valid_actions(), is_training_for_second_player)
        #         if action is None:
        #             action = random.choice(match.valid_actions())
        #         match.perform_action(player, action)
        #         if match.is_over():
        #             outputs.append(match.result_for_player(sbb_player))
        #             break
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