import os
import numpy
import random
import itertools
if os.name == 'posix':
    from pokereval import PokerEval
from poker_config import PokerConfig
from tables.normalized_equity_table import NORMALIZED_HAND_EQUITY
from tables.strenght_table_for_2cards import STRENGTH_TABLE_FOR_2_CARDS

class PokerMetrics():
    
    @staticmethod
    def normalize_winning(value):
        max_small_bet_turn_winning = PokerConfig.CONFIG['small_bet']*4
        max_big_bet_turn_winning = PokerConfig.CONFIG['big_bet']*4
        max_winning = max_small_bet_turn_winning*2 + max_big_bet_turn_winning*2
        max_losing = -max_winning
        return (value - max_losing)/float(max_winning - max_losing)

    @staticmethod
    def initialize_deck():
        deck = []
        for rank in PokerConfig.CONFIG['ranks']:
            for suit in PokerConfig.CONFIG['suits']:
                deck.append(rank+suit)
        return deck

    @staticmethod
    def initialize_hole_cards_based_on_equity():
        deck = initialize_deck()
        hole_cards = list(itertools.combinations(deck, 2))
        equities = []
        for card1, card2 in hole_cards:
            equities.append(NORMALIZED_HAND_EQUITY[frozenset([card1, card2])])
        total_equities = sum(equities)
        probabilities = [e/float(total_equities) for e in equities]
        hole_cards_indices = numpy.random.choice(range(len(hole_cards)), size = int(len(hole_cards)*0.3), replace = False, p = probabilities)
        final_cards = []
        for index in hole_cards_indices:
            final_cards.append(hole_cards[index])
        return final_cards

    @staticmethod
    def calculate_hand_strength(current_hole_cards, board_cards, full_deck):
        """
        Implemented as described in the page 21 of the thesis in: http://poker.cs.ualberta.ca/publications/davidson.msc.pdf
        """
        our_cards = current_hole_cards + board_cards
        our_cards_set = frozenset(our_cards)
        if len(our_cards_set) == 2:
            return STRENGTH_TABLE_FOR_2_CARDS[our_cards_set]
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
            return hand_strength

    @staticmethod
    def calculate_hand_potential_without_heuristics(current_hole_cards, board_cards, round_id, full_deck):
        """
        Implemented as described in the page 23 of the thesis in: http://poker.cs.ualberta.ca/publications/davidson.msc.pdf
        """
        our_cards = current_hole_cards + board_cards
        out_cards_set = frozenset(our_cards)

        # hand potential array, each index represents ahead, tied, and behind
        ahead = 0
        tied = 1
        behind = 2
        hp = [[0.0, 0.0, 0.0], [0.0, 0.0, 0.0], [0.0, 0.0, 0.0]]
        hp_total = [0.0, 0.0, 0.0]
        total = 0.0
        pokereval = PokerEval()
        our_rank = pokereval.evaln(our_cards)
        # considers all two card combinations of the remaining cards for the opponent

        opponent_cards_combinations = list(itertools.combinations(full_deck, 2))
        indices = []
        for index, cards in enumerate(opponent_cards_combinations):
            card1, card2 = cards
            if card1 in our_cards or card2 in our_cards:
                indices.append(index)
        for index in reversed(indices):
            opponent_cards_combinations.pop(index)

        for opponent_card1, opponent_card2 in opponent_cards_combinations:
            opponent_rank = pokereval.evaln([opponent_card1] + [opponent_card2] + board_cards)
            if our_rank > opponent_rank:
                index = ahead
            elif our_rank == opponent_rank:
                index = tied
            else:
                index = behind
            # hp_total[index] += 1.0 # original version

            # all possible board cards to come
            deck = list(full_deck)
            dealt_card = current_hole_cards + board_cards + [opponent_card1] + [opponent_card2]
            deck_without_dealt_cards = [card for card in deck if card not in dealt_card]
            if round_id == 2: # flop
                cards_combinations = list(itertools.combinations(deck_without_dealt_cards, 2))
                # cards_combinations = random.sample(cards_combinations, int(len(cards_combinations)*0.2))
                for turn, river in cards_combinations:
                    # final 5-card board
                    board = board_cards + [turn] + [river]
                    our_future_rank = pokereval.evaln(current_hole_cards + board)
                    opponent_future_rank = pokereval.evaln([opponent_card1] + [opponent_card2] + board)
                    if our_future_rank > opponent_future_rank:
                        hp[index][ahead] += 1.0
                    elif our_future_rank == opponent_future_rank:
                        hp[index][tied] += 1.0
                    else:
                        hp[index][behind] += 1.0
                    total += 1.0
                    hp_total[index] += 1.0 # new version
            else: # turn
                # cards = random.sample(deck_without_dealt_cards, int(len(deck_without_dealt_cards)*0.75))
                cards = deck_without_dealt_cards
                for river in cards:
                    # final 5-card board
                    board = board_cards + [river]
                    our_future_rank = pokereval.evaln(current_hole_cards + board)
                    opponent_future_rank = pokereval.evaln([opponent_card1] + [opponent_card2] + board)
                    if our_future_rank > opponent_future_rank:
                        hp[index][ahead] += 1.0
                    elif our_future_rank == opponent_future_rank:
                        hp[index][tied] += 1.0
                    else:
                        hp[index][behind] += 1.0
                    total += 1.0
                    hp_total[index] += 1.0 # new version

        # the original formula:
        # ppot = (hp[behind][ahead] + hp[behind][tied]/2.0 + hp[tied][ahead]/2.0) / (hp_total[behind] + hp_total[tied]/2.0)
        # npot = (hp[ahead][behind] + hp[tied][behind]/2.0 + hp[ahead][tied]/2.0) / (hp_total[ahead] + hp_total[tied]/2.0)

        # ppot: were behind but moved ahead: cant use the original hp_total, because the result isnt normalzied and because it dont work for the heuristics
        # added hp[ahead][ahead] so already good hands wouldnt be given a below average potential
        ppot = (hp[ahead][ahead] + hp[behind][ahead] + hp[behind][tied]/2.0 + hp[tied][ahead]) / (hp_total[behind]*1.5 + hp_total[tied]*1.0 + hp_total[ahead]*1.0)

        # npot: were ahead but fell behind
        # npot = ((hp[ahead][behind]/total)*2.0 + (hp[ahead][tied]/total)*1.0 + (hp[tied][behind]/total)*1.0)/4.0

        return ppot

    @staticmethod
    def calculate_ehs(hand_strength, hand_equity, hand_potential, round_id):
            if round_id == 4:
                return hand_strength
            if round_id == 1:
                potential = hand_equity
            if round_id == 2 or round_id == 3: # too expensive if calculated for the pre-flop, and useless if calculated for the river
                potential = hand_potential
            weigth = 0.5
            ehs = (hand_strength + potential * weigth)/float(1+weigth)
            return ehs

    @staticmethod
    def calculate_ep(hand_strength, hand_equity, hand_potential, round_id):
            if round_id == 4:
                return hand_strength
            if round_id == 1:
                return hand_equity
            if round_id == 2 or round_id == 3: # too expensive if calculated for the pre-flop, and useless if calculated for the river
                return hand_potential

    @staticmethod
    def calculate_equity(hole_cards):
        return NORMALIZED_HAND_EQUITY[frozenset(hole_cards)]

    @staticmethod
    def get_hand_strength_label(value):
        if value >= 9.0:
            return 0
        if value >= 7.0:
            return 1
        if value >= 4.0:
            return 2
        return 3
