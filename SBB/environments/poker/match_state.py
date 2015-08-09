import os
import re
import random
import itertools
import numpy
if os.name == 'posix':
    from pokereval import PokerEval
from tables.normalized_equity_table import NORMALIZED_HAND_EQUITY
from tables.strenght_table_for_2cards import STRENGTH_TABLE_FOR_2_CARDS

class MatchState():

    INPUTS = ['pot', 'bet', 'pot odds', 'betting position', 'round', 'equity', 'hand strength', 'EHS']

    def __init__(self, message, small_bet, big_bet, full_deck, hole_cards_based_on_equity):
        self.message = message
        self.small_bet = small_bet
        self.big_bet = big_bet
        self.full_deck = list(full_deck)
        self.hole_cards_based_on_equity = hole_cards_based_on_equity
        self.position = None
        self.opponent_position = None
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
        if self.position == 0:
            self.opponent_position = 1
        else:
            self.opponent_position = 0
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

    def last_player_to_act(self):
        if len(self.rounds[-1]) == 0:
            acted_round = self.rounds[-2]
        else:
            acted_round = self.rounds[-1]
        if acted_round == self.rounds[0]: # since the game uses reverse blinds
            if len(acted_round) % 2 == 0:
                last_player = 0
            else:
                last_player = 1
        else: # cc/cr/rr 10/01/01
            if len(acted_round) % 2 == 0:
                last_player = 1
            else:
                last_player = 0
        return last_player

    def is_showdown(self):
        if self.opponent_hole_cards:
            return True
        else:
            return False

    def get_winner_of_showdown(self):
        our_rank = self.pokereval.evaln(self.current_hole_cards + self.board_cards)
        opponent_rank = self.pokereval.evaln(self.opponent_hole_cards + self.board_cards)
        if our_rank > opponent_rank:
            return self.position
        if our_rank < opponent_rank:
            return self.opponent_position
        return None # draw

    def is_last_action_a_fold(self):
        actions = self.rounds[-1]
        if len(actions) > 0 and actions[-1] == 'f':
            return True
        else:
            return False

    def actions_per_player(self):
        # check the other cases
        self_actions = []
        opponent_actions = []
        for round_index, actions in enumerate(self.rounds):
            if round_index == 0 or round_index == 1:
                bet = self.small_bet
            else:
                bet = self.big_bet
            for action_index, action in enumerate(actions):
                if round_index == 0:
                    if self.position == 0:
                        if action_index % 2 == 0:
                            opponent_actions.append(action)
                        else:
                            self_actions.append(action)
                    else:
                        if action_index % 2 == 0:
                            self_actions.append(action)
                        else:
                            opponent_actions.append(action)
                else:
                    if self.position == 0:
                        if action_index % 2 == 0:
                            self_actions.append(action)
                        else:
                            opponent_actions.append(action)
                    else:
                        if action_index % 2 == 0:
                            opponent_actions.append(action)
                        else:
                            self_actions.append(action)
        return self_actions, opponent_actions

    def inputs(self, memories):
        """
        ATTENTION: If you change the order, add or remove inputs the SBB teams that were already trained will 
        behave unexpectedly!

        All inputs are normalized, so they influence the SBB player potentially equal.

        inputs[0] = pot
        inputs[1] = bet
        inputs[2] = pot odds
        inputs[3] = betting position (0: first betting, 1: last betting)
        inputs[4] = round 
        inputs[5] = equity
        inputs[6] = hand_strength
        inputs[7] = EHS
        """
        hand_strength_memory, hand_ppotential_memory = memories
        inputs = [0] * len(MatchState.INPUTS)
        inputs[0] = self.calculate_pot()/float(self.maximum_winning())
        inputs[1] = self._calculate_bet()
        if inputs[0] + inputs[1] > 0:
            inputs[2] = inputs[1] / float(inputs[0] + inputs[1])
        else:
            inputs[2] = 0.0
        inputs[3] = float(self._betting_position())
        inputs[4] = (len(self.rounds)-1)/3.0
        inputs[5] = NORMALIZED_HAND_EQUITY[frozenset(self.current_hole_cards)]
        inputs[6] = MatchState.calculate_hand_strength(self.current_hole_cards, self.board_cards, self.full_deck, hand_strength_memory)
        if len(self.rounds) == 2 or len(self.rounds) == 3:
            ppotential = self._calculate_hand_potential(hand_ppotential_memory)
        else: # too expensive if calculated for the pre-flop, and useless if calculated for the river
            ppotential = 0.0
        inputs[7] = inputs[6] + (1 - inputs[6]) * ppotential
        return inputs

    def calculate_pot(self):
        # check if is the small blind
        if len(self.rounds) == 1:
            if len(self.rounds[0]) == 0 or (len(self.rounds[0]) == 1 and self.rounds[0][0] == 'f'):
                return self.small_bet/2.0

        # check if someone raised
        pot = self.small_bet
        for i, r in enumerate(self.rounds):
            if i == 0 or i == 1:
                bet = self.small_bet
            else:
                bet = self.big_bet
            for action in r:
                if action == 'r':
                    pot += bet
        return pot

    def maximum_winning(self):
        max_small_bet_turn_winning = self.small_bet*4
        max_big_bet_turn_winning = self.big_bet*4
        return max_small_bet_turn_winning*2 + max_big_bet_turn_winning*2

    def _calculate_bet(self):
        # check if is the small blind
        if len(self.rounds) == 1 and len(self.rounds[0]) == 0:
            return 0.5
        
        # check if the opponent raised
        bet = 0.0
        current_round = self.rounds[-1]
        if current_round: # if there is previous actions
            last_action = current_round[-1]
            if last_action == 'r':
                bet = 1.0 # since the value is normalized and the poker is limited, 1 means the maximum bet
        return bet

    def _betting_position(self):
        if len(self.rounds) == 1: # reverse blinds
            if self.position == 0:
                return 1
            else:
                return 0
        else:
            return self.position

    @staticmethod
    def calculate_hand_strength(current_hole_cards, board_cards, full_deck, hand_strength_memmory):
        """
        Implemented as described in the page 21 of the thesis in: http://poker.cs.ualberta.ca/publications/davidson.msc.pdf
        """
        our_cards = current_hole_cards + board_cards
        our_cards_set = frozenset(our_cards)
        if len(our_cards_set) == 2:
            return STRENGTH_TABLE_FOR_2_CARDS[our_cards_set]
        if our_cards_set in hand_strength_memmory:
            return hand_strength_memmory[our_cards_set]
        else:
            pokereval = PokerEval()
            ahead = 0.0
            tied = 0.0
            behind = 0.0
            our_rank = pokereval.evaln(our_cards)
            # considers all two card combinations of the remaining cards

            deck = list(full_deck)
            for card in our_cards:
                if card not in deck:
                    print "Warning! Card not in deck: "+str(card)+", current_hole_cards: "+str(current_hole_cards)+", board_cards: "+str(board_cards)
                deck.remove(card)
            opponent_cards_combinations = itertools.combinations(deck, 2)

            for opponent_card1, opponent_card2 in opponent_cards_combinations:
                opponent_rank = pokereval.evaln([opponent_card1] + [opponent_card2] + board_cards)
                if our_rank > opponent_rank:
                    ahead += 1.0
                elif our_rank == opponent_rank:
                    tied += 1.0
                else:
                    behind += 1.0
            hand_strength = (ahead + tied/2.0) / (ahead + tied + behind)
            hand_strength_memmory[our_cards_set] = hand_strength
            return hand_strength

    def _calculate_hand_potential(self, hand_ppotential_memory):
        """
        Implemented as described in the page 23 of the thesis in: http://poker.cs.ualberta.ca/publications/davidson.msc.pdf
        """
        our_cards = self.current_hole_cards + self.board_cards
        out_cards_set = frozenset(our_cards)
        if out_cards_set in hand_ppotential_memory:
            return hand_ppotential_memory[out_cards_set]
        else:
            # hand potential array, each index represents ahead, tied, and behind
            ahead = 0
            tied = 1
            behind = 2
            hp = [[0.0, 0.0, 0.0], [0.0, 0.0, 0.0], [0.0, 0.0, 0.0]]
            # hp_total = [0.0, 0.0, 0.0]
            total = 0.0
            our_rank = self.pokereval.evaln(our_cards)
            # considers all two card combinations of the remaining cards for the opponent

            opponent_cards_combinations = list(self.hole_cards_based_on_equity)
            indices = []
            for index, cards in enumerate(opponent_cards_combinations):
                card1, card2 = cards
                if card1 in our_cards or card2 in our_cards:
                    indices.append(index)
            for index in reversed(indices):
                opponent_cards_combinations.pop(index)

            for opponent_card1, opponent_card2 in opponent_cards_combinations:
                opponent_rank = self.pokereval.evaln([opponent_card1] + [opponent_card2] + self.board_cards)
                if our_rank > opponent_rank:
                    index = ahead
                elif our_rank == opponent_rank:
                    index = tied
                else:
                    index = behind
                # hp_total[index] += 1.0

                # all possible board cards to come
                deck = list(self.full_deck)
                dealt_card = self.current_hole_cards + self.board_cards + [opponent_card1] + [opponent_card2]
                deck_without_dealt_cards = [card for card in deck if card not in dealt_card]
                if len(self.rounds) == 2: # flop
                    cards_combinations = list(itertools.combinations(deck_without_dealt_cards, 2))
                    cards_combinations = random.sample(cards_combinations, int(len(cards_combinations)*0.2))
                    for turn, river in cards_combinations:
                        # final 5-card board
                        board = self.board_cards + [turn] + [river]
                        our_future_rank = self.pokereval.evaln(self.current_hole_cards + board)
                        opponent_future_rank = self.pokereval.evaln([opponent_card1] + [opponent_card2] + board)
                        if our_future_rank > opponent_future_rank:
                            hp[index][ahead] += 1.0
                        elif our_future_rank == opponent_future_rank:
                            hp[index][tied] += 1.0
                        else:
                            hp[index][behind] += 1.0
                        total += 1.0
                else: # turn
                    cards = random.sample(deck_without_dealt_cards, int(len(deck_without_dealt_cards)*0.75))
                    for river in cards:
                        # final 5-card board
                        board = self.board_cards + [river]
                        our_future_rank = self.pokereval.evaln(self.current_hole_cards + board)
                        opponent_future_rank = self.pokereval.evaln([opponent_card1] + [opponent_card2] + board)
                        if our_future_rank > opponent_future_rank:
                            hp[index][ahead] += 1.0
                        elif our_future_rank == opponent_future_rank:
                            hp[index][tied] += 1.0
                        else:
                            hp[index][behind] += 1.0
                        total += 1.0

            # the original formula:
            # ppot = (hp[behind][ahead] + hp[behind][tied]/2.0 + hp[tied][ahead]/2.0) / (hp_total[behind] + hp_total[tied]/2.0)
            # npot = (hp[ahead][behind] + hp[tied][behind]/2.0 + hp[ahead][tied]/2.0) / (hp_total[ahead] + hp_total[tied]/2.0)

            # ppot: were behind but moved ahead
            ppot = ((hp[behind][ahead]/total)*2.0 + (hp[behind][tied]/total)*1.0 + (hp[tied][ahead]/total)*1.0)/4.0

            # npot: were ahead but fell behind
            npot = ((hp[ahead][behind]/total)*2.0 + (hp[ahead][tied]/total)*1.0 + (hp[tied][behind]/total)*1.0)/4.0

            hand_ppotential_memory[out_cards_set] = ppot

            return ppot

    def valid_actions(self):
        """
        
        """
        valid = [1]
        # check if can fold
        if len(self.rounds) > 1:
            current_round = self.rounds[-1]
            if 'r' in current_round:
                valid.append(0)
        else:
            current_round = self.rounds[-1]
            if len(current_round) == 0 or 'r' in current_round:
                valid.append(0)

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
        msg += "opponent_position: "+str(self.opponent_position)+"\n"
        msg += "hand_id: "+str(self.hand_id)+"\n"
        msg += "rounds: "+str(self.rounds)+"\n"
        msg += "current_hole_cards: "+str(self.current_hole_cards)+"\n"
        msg += "opponent_hole_cards: "+str(self.opponent_hole_cards)+"\n"
        msg += "board_cards: "+str(self.board_cards)+"\n"
        return msg