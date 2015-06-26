from ...config import Config

class MatchState():

    INPUTS = ['pot', 'bet', 'pot odds']

    def __init__(self, message):
        self.position = None
        self.hand_id = None
        self.rounds = None
        self.hole_cards = None
        self.current_hole_cards = None
        self.opponent_hole_cards = None
        self.board_cards = None
        self._decode_message(message)

    def _decode_message(self, message):
        splitted = message.split(":")
        self.position = int(splitted[1])
        self.hand_id = int(splitted[2])
        self.rounds = splitted[3].split("/")
        cards = splitted[4].split("/")
        self.hole_cards = cards[0].split("|")
        if self.position == 0:
            self.current_hole_cards = self.hole_cards[0]
            self.opponent_hole_cards = self.hole_cards[1]
        else:
            self.current_hole_cards = self.hole_cards[1]
            self.opponent_hole_cards = self.hole_cards[0]
        self.board_cards = cards[1:-1]

    def is_current_player_to_act(self):
        if len(self.rounds) == 1: # since the game uses reverse blinds
            if len(self.rounds[0]) % 2 == 0:
                current_player = 1
            else:
                current_player = 0
        else:
            if len(self.rounds[-1]) % 2 == 0:
                current_player = 0
            else:
                current_player = 1
        if int(self.position) == current_player:
            return True
        else:
            return False

    def is_showdown(self):
        if self.opponent_hole_cards:
            return True
        else:
            return False

    def inputs(self):
        """
        ATTENTION: If you change the order or remove inputs the SBB teams that were already trained will 
        behave unexpectedly! The only safe modification is to add new inputs at the end of the list.

        inputs[0] = pot
        inputs[1] = bet
        inputs[2] = pot odds
        
        the Pot (pot odds); the Bet; the Position; the Card evaluator (hand strenght, hand potential, 
        effective hand strength (EHS)); and Opponent model (percentage of actions, shot-term agressiveness, 
        long-term agressiveness). + qual o round?

        from_the_point_of_view_of the current player
        """
        inputs = [0] * len(MatchState.INPUTS)
        inputs[0] = self._calculate_pot()
        inputs[1] = self._calculate_bet()
        if inputs[0] + inputs[1] > 0:
            inputs[2] = inputs[1] / float(inputs[0] + inputs[1])
        else:
            inputs[2] = 0
        return inputs

    def _calculate_pot(self):
        pot = Config.RESTRICTIONS['poker']['small_bet']
        for i, r in enumerate(self.rounds):
            if i == 0 or i == 1:
                bet = Config.RESTRICTIONS['poker']['small_bet']
            else:
                bet = Config.RESTRICTIONS['poker']['big_bet']
            for action in r:
                if action == 'r':
                    pot += bet
        return pot

    def _calculate_bet(self):
        bet = 0
        # check if the opponent raised
        current_round = self.rounds[-1]
        current_round_index = len(self.rounds)
        if current_round: # if there is previous actions
            last_action = current_round[-1]
            if last_action == 'r':
                if current_round_index == 1 or current_round_index == 2:
                    bet = Config.RESTRICTIONS['poker']['small_bet']
                else:
                    bet = Config.RESTRICTIONS['poker']['big_bet']
        return bet

    def valid_actions(self):
        """
        
        """
        # valid = [0, 1]
        valid = [1]
        # check if can raise
        if len(self.rounds) == 1:
            max_raises = 3
        else:
            max_raises = 4
        raises = 0
        for action in self.rounds[-1]:
            if action == 'r':
                raises += 1
        if raises < max_raises:
            valid.append(2)
        return valid

    def __str__(self):
        msg = "\n"
        msg += "position: "+str(self.position)+"\n"
        msg += "hand_id: "+str(self.hand_id)+"\n"
        msg += "rounds: "+str(self.rounds)+"\n"
        msg += "hole_cards: "+str(self.hole_cards)+"\n"
        msg += "current_hole_cards: "+str(self.current_hole_cards)+"\n"
        msg += "opponent_hole_cards: "+str(self.opponent_hole_cards)+"\n"
        msg += "board_cards: "+str(self.board_cards)+"\n"
        msg += "inputs: "+str(self.inputs())+"\n"
        return msg