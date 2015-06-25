from ...config import Config

class PokerMatch():
    """
    
    """

    def __init__(self):
        self.inputs_ = [] # TODO
        self.result_ = -1
        self.print_game_ = Config.USER['reinforcement_parameters']['debug_matches']

    def perform_action(self, current_player, action):
        """
        
        """
        pass # TODO
        # self.inputs_[action] = current_player
        # if self.print_game_:
        #     print "---"
        #     print str(self.inputs_[0:3])
        #     print str(self.inputs_[3:6])
        #     print str(self.inputs_[6:9])

    def valid_actions(self): # precisa ser um array com [0,1,2]
        """
        
        """
        pass # TODO
        # valids = []
        # for index, space in enumerate(self.inputs_):
        #     if space == TictactoeMatch.EMPTY:
        #         valids.append(index)
        # return valids

    def inputs_from_the_point_of_view_of(self, position):
        """
        
        """
        pass # TODO
        # if position == 1:
        #     return list(self.inputs_)
        # else:
        #     mapping = [0, 2, 1]
        #     inputs = [mapping[x] for x in self.inputs_]
        #     return inputs

    def is_over(self):
        """
        
        """
        pass # TODO
        # winner = TictactoeMatch.get_winner(self.inputs_)
        # if winner:
        #     self.result_ = winner
        #     if self.print_game_:
        #         print "It is over! Player "+str(self.result_)+" wins!"
        #     return True
        # for value in self.inputs_:
        #     if value == TictactoeMatch.EMPTY:
        #         if self.print_game_:
        #             print "Go!"
        #         return False
        # self.result_ = TictactoeMatch.DRAW
        # if self.print_game_:
        #     print "It is over! Draw!"
        # return True

    def result_for_player(self, current_player):
        pass
        # if self.result_ == current_player:
        #     return 1 # win
        # if self.result_ == TictactoeMatch.DRAW:
        #     return 0.5 # draw
        # else:
        #     return 0 # lose

    @staticmethod
    def get_winner(inputs):
        pass
        # winning_configs = ((0, 1, 2), (3, 4, 5), (6, 7, 8), (0, 3, 6),
        #                (1, 4, 7), (2, 5, 8), (0, 4, 8), (2, 4, 6))
        # for config in winning_configs:
        #     if inputs[config[0]] == inputs[config[1]] and inputs[config[1]] == inputs[config[2]]:
        #         return inputs[config[0]]
        # return None # no winner