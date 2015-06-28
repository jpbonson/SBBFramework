import os
import re
import itertools
if os.name == 'posix':
    from pokereval import PokerEval
from ...config import Config

class MatchState():

    INPUTS = ['pot', 'bet', 'pot odds', 'betting position', 'chips', 'hand strength', 'hand potential']

    def __init__(self, message):
        self.message = message
        self.position = None
        self.hand_id = None
        self.rounds = None
        self.current_hole_cards = None
        self.opponent_hole_cards = None
        self.board_cards = None
        self._decode_message(message)
        self.pokereval = PokerEval()

    def _decode_message(self, message):
        splitted = message.split(":")
        self.position = int(splitted[1])
        self.hand_id = int(splitted[2])
        self.rounds = splitted[3].split("/")
        cards = splitted[4].split("/")
        hole_cards = cards[0].split("|")
        if self.position == 0:
            self.current_hole_cards = re.findall('..', hole_cards[0])
            self.opponent_hole_cards = re.findall('..', hole_cards[1])
        else:
            self.current_hole_cards = re.findall('..', hole_cards[1])
            self.opponent_hole_cards = re.findall('..', hole_cards[0])
        self.board_cards = []
        for turn in cards[1:]:
            self.board_cards += re.findall('..', turn)

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
        inputs[4] = chips
        inputs[5] = hand_strength
        inputs[6] = hand_potential

        Chips (the stacks are infinite, but it may be useful to play more conservative if it is losing a lot)
        Card evaluator (hand strenght, hand potential, effective hand strength (EHS));
        Opponent model (percentage of actions?, shot-term agressiveness, long-term agressiveness)

        from_the_point_of_view_of the current player

        (Andy)
        For item 7, I might suggest that we use two separate factors, the first being aggressiveness, per Nicolai / Hilderman (both (a) 
        short-term, as measured only with respect to the last 10 hands and (b) overall, which has complete history in mind).  
        The second factor that we might consider is volatility which would measure relative frequency of proceeding with a hand (call), 
        initiating bets, and folding in both the pre-flop and post-flop stages.  So a total of six values for each opponent (or eight if 
        you include the two proposed aggressiveness features).  If we wanted to go a little further it might be handy to do the volatility 
        features with respect to short-term and overall as well.

        pokereval.evaln(['As', 'Qd', 'Qh', 'Ks', 'Qc', '4c', '4d', 'Kc'])

        http://poker.cs.ualberta.ca/publications/davidson.msc.pdf, pages 21 and 23
        """
        inputs = [0] * len(MatchState.INPUTS)
        inputs[0] = self._calculate_pot()
        inputs[1] = self._calculate_bet()
        if inputs[0] + inputs[1] > 0:
            inputs[2] = inputs[1] / float(inputs[0] + inputs[1])
        else:
            inputs[2] = 0
        inputs[3] = self._betting_position()
        inputs[4] = 0 # TODO
        inputs[5] = self._calculate_hand_strength()
        if len(self.rounds) > 1:
            inputs[6] = self._calculate_hand_potential()
        else:
            inputs[6] = 0 # ?
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

    def _calculate_hand_strength(self):
        """
        Implemented as described in the page 21 of the thesis in: http://poker.cs.ualberta.ca/publications/davidson.msc.pdf
        """
        ahead = 0.0
        tied = 0.0
        behind = 0.0
        our_rank = self.pokereval.evaln(self.current_hole_cards + self.board_cards)
        # considers all two card combinations of the remaining cards
        opponent_cards_combinations = self._cards_combinations(without_cards = self.current_hole_cards + self.board_cards)
        for opponent_card1, opponent_card2 in opponent_cards_combinations:
            opponent_rank = self.pokereval.evaln([opponent_card1] + [opponent_card2] + self.board_cards)
            if our_rank > opponent_rank:
                ahead += 1.0
            elif our_rank == opponent_rank:
                tied += 1.0
            else:
                behind += 1.0
        hand_strength = (ahead + tied/2) / (ahead + tied + behind)
        return hand_strength

    def _cards_combinations(self, without_cards):
        deck = self._initialize_deck()
        for card in without_cards:
            deck.remove(card)
        return itertools.combinations(deck, 2)

    def _initialize_deck(self):
        ranks = ['2', '3', '4', '5', '6', '7', '8', '9', 'T', 'J', 'Q', 'K', 'A']
        suits = ['s', 'd', 'h', 'c']
        deck = []
        for rank in ranks:
            for suit in suits:
                deck.append(rank+suit)
        return deck

    def _calculate_hand_potential(self):
        # hand potential array, each index represents ahead, tied, and behind
        hp = [[0.0, 0.0, 0.0], [0.0, 0.0, 0.0], [0.0, 0.0, 0.0]]
        hp_total = [0.0, 0.0, 0.0]
        our_rank = self.pokereval.evaln(self.current_hole_cards + self.board_cards)
        # considers all two card combinations of the remaining cards for the opponent
        return 0 # TODO

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
        msg += "current_hole_cards: "+str(self.current_hole_cards)+"\n"
        msg += "opponent_hole_cards: "+str(self.opponent_hole_cards)+"\n"
        msg += "board_cards: "+str(self.board_cards)+"\n"
        msg += "inputs: "+str(self.inputs())+"\n"
        return msg