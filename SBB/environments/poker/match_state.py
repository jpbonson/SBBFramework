from ...config import Config

class MatchState():

    INPUTS = ['pot', 'bet', 'pot odds', 'betting position']

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
        inputs[3] = betting position (0: firt betting, 1: last betting)

        Chips (the stacks are infinite, but it may be useful to play more conservative if it is losing a lot)
        Card evaluator (hand strenght, hand potential, effective hand strength (EHS));
        Opponent model (percentage of actions, shot-term agressiveness, long-term agressiveness)

        from_the_point_of_view_of the current player

        (Andy)
        The most immediate exists in the ACPC distribution under the rankHand function in the game.c file.  The way 
        how this works is that it loads a large lookup table into memory via the evalHandTables file (conspicuously 
        lacking a file extension and then oddly included with the preprocessor in game.c) and returns the hand rank.  
        The upside is that it seems the evalHandTables file can likely be used as-is without too much fussing with other 
        components of the server. The downside is that it relies on a specific data structure that isn't apparent to me 
        how it works but can probably be inferred from a few little tests.  

        (Andy)
        A backup option for this would be to go to a more generic, 'stand-alone' evaluator; the so-called cactus Kev evaluator 
        (http://www.suffecool.net/poker/evaluator.html) is one that is written in C and has been used as the basis for some 
        commercial software, an improved version that uses perfect hashing is also available 
        (http://www.paulsenzee.com/2006/06/some-perfect-hash.html) but I'm not so sure how thoroughly this has been tested.  
        Since a 5, 6 and 7-card evaluation is eventually required one can either write their own wrapper for the above 5-card 
        evaluators or there is a good looking 7-card evaluator by Moritz Hammer (http://www.pst.ifi.lmu.de/~hammer/poker/handeval.html) 
        and the code is provided in both C and java, though his timings appear to show a pretty clear advantage for the former. 
        ---

        (Andy)
        For item 7, I might suggest that we use two separate factors, the first being aggressiveness, per Nicolai / Hilderman (both (a) 
        short-term, as measured only with respect to the last 10 hands and (b) overall, which has complete history in mind).  
        The second factor that we might consider is volatility which would measure relative frequency of proceeding with a hand (call), 
        initiating bets, and folding in both the pre-flop and post-flop stages.  So a total of six values for each opponent (or eight if 
        you include the two proposed aggressiveness features).  If we wanted to go a little further it might be handy to do the volatility 
        features with respect to short-term and overall as well.
        """
        inputs = [0] * len(MatchState.INPUTS)
        inputs[0] = self._calculate_pot()
        inputs[1] = self._calculate_bet()
        if inputs[0] + inputs[1] > 0:
            inputs[2] = inputs[1] / float(inputs[0] + inputs[1])
        else:
            inputs[2] = 0
        inputs[3] = self._betting_position()
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

    def _betting_position(self):
        if len(self.rounds) == 1: # reverse blinds
            if self.position == 0:
                return 1
            else:
                return 0
        else:
            return self.position

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