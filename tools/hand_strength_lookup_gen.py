import itertools
from pokereval import PokerEval

RANKS = ['2', '3', '4', '5', '6', '7', '8', '9', 'T', 'J', 'Q', 'K', 'A']
SUITS = ['s', 'd', 'h', 'c']

def calculate_hand_strength(deck, current_hole_cards, board = []):
    """
    Implemented as described in the page 21 of the thesis in: http://poker.cs.ualberta.ca/publications/davidson.msc.pdf
    """
    pokereval = PokerEval()
    our_cards = current_hole_cards
    ahead = 0.0
    tied = 0.0
    behind = 0.0
    our_rank = pokereval.evaln(our_cards + board)
    # considers all two card combinations of the remaining cards
    opponent_cards_combinations = itertools.combinations(deck, 2)
    for opponent_card1, opponent_card2 in opponent_cards_combinations:
        opponent_rank = pokereval.evaln([opponent_card1] + [opponent_card2] + board)
        if our_rank > opponent_rank:
            ahead += 1.0
        elif our_rank == opponent_rank:
            tied += 1.0
        else:
            behind += 1.0
    hand_strength = (ahead + tied/2.0) / (ahead + tied + behind)
    return hand_strength

def initialize_deck():
    deck = []
    for rank in RANKS:
        for suit in SUITS:
            deck.append(rank+suit)
    return deck

def lookup_table_for_2cards():
    lookup_table = {}
    deck = initialize_deck()
    all_hole_cards = itertools.combinations(deck, 2)
    for card1, card2 in all_hole_cards:
        deck2 = list(deck)
        deck2.remove(card1)
        deck2.remove(card2)
        hand_strength = calculate_hand_strength(deck2, [card1, card2])
        lookup_table[frozenset([card1, card2])] = hand_strength
    with open('lookup_table_for_2cards', 'w') as the_file:
        the_file.write(str(lookup_table))

def lookup_table_for_5cards():
    deck = initialize_deck()
    all_hole_cards = itertools.combinations(deck, 2)
    cont = 0
    open('lookup_table_for_5cards', 'w').close()
    for card1, card2 in all_hole_cards:
        cont += 1
        print str(cont)
        deck2 = list(deck)
        deck2.remove(card1)
        deck2.remove(card2)
        all_flop_cards = itertools.combinations(deck2, 3)
        for card3, card4, card5 in all_flop_cards:
            deck3 = list(deck2)
            deck3.remove(card3)
            deck3.remove(card4)
            deck3.remove(card5)
            hand_strength = calculate_hand_strength(deck3, [card1, card2], [card3, card4, card5])
            with open('lookup_table_for_5cards', 'a') as the_file:
                the_file.write(str(frozenset([card1, card2, card3, card4, card5]))+": "+str(hand_strength)+", ")

if __name__ == "__main__":
    # lookup_table_for_2cards()
    lookup_table_for_5cards()