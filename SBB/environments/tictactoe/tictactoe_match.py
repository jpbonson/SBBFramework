class TictactoeMatch():
    """

    """

    def __init__(self):
        self.inputs_ = [0, 0, 0,
                        0, 0, 0,
                        0, 0, 0]
        self.result_ = -1

    def perform_action(self, current_player, action):
        """
        Perform the action for the current_player in the board, modifying 
        the attribute inputs_.
        """
        self.inputs_[action] = current_player

    def is_valid_action(self, action):
        """
        If the chosen space (represented by the action) is empty, the 
        action is valid. If not, it is invalid.
        """
        if self.inputs_[action] == 0:
            return True
        return False

    def is_over(self):
        """
        Check if all spaces were used. If yes, sets the attribute result_ with the 
        number of the winner or 0 if a draw occured.
        """
        for value in self.inputs_:
            if value == 0:
                return False
        self.result_ = self._define_winner()
        return True

    def _define_winner(self):
        winning_configs = ((0, 1, 2), (3, 4, 5), (6, 7, 8), (0, 3, 6),
                       (1, 4, 7), (2, 5, 8), (0, 4, 8), (2, 4, 6))
        for config in winning_configs:
            if self.inputs_[config[0]] == self.inputs_[config[1]] and self.inputs_[config[1]] == self.inputs_[config[2]]:
                winner = self.inputs_[config[0]]
                return winner
        return 0 # tie

    def result_for_player(self, current_player):
        if self.result_ == current_player:
            return 1 # win
        if self.result_ == 0:
            return 0.5 # draw
        else:
            return 0 # lose