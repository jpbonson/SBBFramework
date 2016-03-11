from ...config import Config

class TictactoeMatch():
    """
    Implements a TicTacToe match
    """

    EMPTY = 0
    DRAW = 0

    def __init__(self, player1_label, player2_label):
        self.inputs_ = [TictactoeMatch.EMPTY, TictactoeMatch.EMPTY, TictactoeMatch.EMPTY,
                        TictactoeMatch.EMPTY, TictactoeMatch.EMPTY, TictactoeMatch.EMPTY,
                        TictactoeMatch.EMPTY, TictactoeMatch.EMPTY, TictactoeMatch.EMPTY]
        self.result_ = -1
        self.print_game_ = Config.USER['reinforcement_parameters']['debug']['print']
        self.player_label = {}
        self.player_label[1] = player1_label
        self.player_label[2] = player2_label

    def perform_action(self, current_player, action):
        """
        Perform the action for the current_player in the board, modifying 
        the attribute inputs_.
        """
        self.inputs_[action] = current_player
        if self.print_game_:
            print "---"
            print str(self.inputs_[0:3])
            print str(self.inputs_[3:6])
            print str(self.inputs_[6:9])

    def valid_actions(self):
        """
        The valid actions are the empty spaces.
        """
        valids = []
        for index, space in enumerate(self.inputs_):
            if space == TictactoeMatch.EMPTY:
                valids.append(index)
        return valids

    def inputs_from_the_point_of_view_of(self, position):
        """
        Get a copy of the inputs so that the player in 'position' always see the board with 
        spaces with '1' as their spaces, and '2' as the opponent's spaces.
        """
        if position == 1:
            return [x*Config.RESTRICTIONS['multiply_normalization_by'] for x in list(self.inputs_)]
        else:
            mapping = [0, 2, 1]
            inputs = [mapping[x]*Config.RESTRICTIONS['multiply_normalization_by'] for x in list(self.inputs_)]
            return inputs

    def is_over(self):
        """
        Check if all spaces were used. If yes, sets the attribute result_ with the 
        number of the winner or 0 if a draw occured.
        """
        winner = TictactoeMatch.get_winner(self.inputs_)
        if winner:
            self.result_ = winner
            if self.print_game_:
                print "It is over! Player "+str(self.result_)+" ("+str(self.player_label[self.result_])+") wins!"
            return True
        for value in self.inputs_:
            if value == TictactoeMatch.EMPTY:
                if self.print_game_:
                    print "Go!"
                return False
        self.result_ = TictactoeMatch.DRAW
        if self.print_game_:
            print "It is over! Draw!"
        return True

    def result_for_player(self, current_player):
        if self.result_ == current_player:
            return 1 # win
        if self.result_ == TictactoeMatch.DRAW:
            return 0.5 # draw
        else:
            return 0 # lose

    @staticmethod
    def get_winner(inputs):
        winning_configs = ((0, 1, 2), (3, 4, 5), (6, 7, 8), (0, 3, 6),
                       (1, 4, 7), (2, 5, 8), (0, 4, 8), (2, 4, 6))
        for config in winning_configs:
            if inputs[config[0]] == inputs[config[1]] and inputs[config[1]] == inputs[config[2]]:
                return inputs[config[0]]
        return None # no winner