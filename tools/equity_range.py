import itertools
from SBB.environments.poker.tables.equity_table import EQUITY_TABLE

RANKS = ['2', '3', '4', '5', '6', '7', '8', '9', 'T', 'J', 'Q', 'K', 'A']
SUITS = ['s', 'd', 'h', 'c']

def round_value(value, round_decimals_to = 3):
    number = float(10**round_decimals_to)
    return int(value * number) / number

def initialize_deck():
    deck = []
    for rank in RANKS:
        for suit in SUITS:
            deck.append(rank+suit)
    return deck

def calculate_equity(hole_cards):
    if hole_cards[0][1] == hole_cards[1][1]:
        suit = 's'
    else:
        suit = 'o'
    key = hole_cards[0][0]+hole_cards[1][0]+suit
    result = EQUITY_TABLE[key][0]
    return result

if __name__ == "__main__":
    deck = initialize_deck()
    hole_cards = list(itertools.combinations(deck, 2))
    # equities = []
    # for card1, card2 in hole_cards:
    #     equities.append(calculate_equity([card1, card2]))
    # s = sorted(zip(equities, hole_cards), reverse=True)
    # print str(len(s)) # 1326
    # print "---"
    # print str(s[int(round(len(s)*0.2))]) # 20% (>= 0.564089482, ('9h', 'Kc'))
    # print str(s[int(round(len(s)*0.5))]) # 30% (>= 0.478209277, ('8c', 'Ts'))
    # print str(s[int(round(len(s)*0.6))]) # 50% (< 0.478209277, ('5c', 'Jh'))
    # print "---"
    # print str(s[int(round(len(s)*0.1))]) # 10% (>= 0.605853525, ('Tc', 'Kc'))
    # print str(s[int(round(len(s)*0.2))]) # 20% (>= 0.564089482, ('9h', 'Kc'))
    # print str(s[int(round(len(s)*0.6))]) # 30% (>= 0.449015885, ('5c', 'Jh'))
    # print str(s[int(round(len(s)*0.7))]) # 40% (< 0.449015885, ('4s', 'Tc'))
    # print "---"
    # print str(len(s[:int(round(len(s)*0.1))]))
    # print str(s[:int(round(len(s)*0.1))])

    open('lookup_table_equity.py', 'w').close()
    minv = 0.29240095
    maxv = 0.84933161
    with open('lookup_table_equity.py', 'a') as the_file:
        the_file.write('NORMALIZED_HAND_EQUITY = {')
        for card1, card2 in hole_cards:
            hand_equity = calculate_equity([card1, card2])
            hand_equity = (hand_equity - minv)/(maxv - minv)
            the_file.write(str(frozenset([card1, card2]))+": "+str(hand_equity)+", ")
        the_file.write('}')