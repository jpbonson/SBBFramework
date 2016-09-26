import os
import json
import random
from poker_metrics import PokerMetrics
from ..match_state import MatchState
from ..poker_config import PokerConfig
from ....utils.helpers import available_ports, round_value
from ....config import Config

def set_metrics(point, round_id, full_deck, key):
    s = PokerMetrics.calculate_hand_strength(point[key]['hc'], point['bc'], full_deck)
    if round_id == 1 or round_id == 2:
        p = PokerMetrics.calculate_hand_potential_without_heuristics(point[key]['hc'], point['bc'], round_id, full_deck)
    else:
        p = 0
    e = PokerMetrics.calculate_equity(point[key]['hc'])
    ep = PokerMetrics.calculate_ep(s, e, p, round_id)
    point[key]['str'][round_id] = round_value(s*Config.RESTRICTIONS['multiply_normalization_by'], 3)
    point[key]['ep'][round_id] = round_value(ep*Config.RESTRICTIONS['multiply_normalization_by'], 3)
    return point

def initialize_metrics(seed, port_pos0, port_pos1, full_deck):
    seeded_deck = PokerMetrics.initialize_deck()
    random.seed(seed)
    random.shuffle(seeded_deck)

    point = {}
    point['bc'] = []
    point['pos'] = 0
    point['p'] = {}
    point['o'] = {}
    point['p']['hc'] = [seeded_deck.pop(), seeded_deck.pop()]
    point['o']['hc'] = [seeded_deck.pop(), seeded_deck.pop()]
    point['p']['str'] = [-1] * 4
    point['p']['ep'] = [-1] * 4
    point['o']['str'] = [-1] * 4
    point['o']['ep'] = [-1] * 4

    for round_id, poker_round in enumerate(['preflop', 'flop', 'turn', 'river']):
        if poker_round == 'flop':
            point['bc'] = [seeded_deck.pop(), seeded_deck.pop(), seeded_deck.pop()]
        if poker_round == 'turn' or poker_round == 'river':
            point['bc'].append(seeded_deck.pop())
        set_metrics(point, round_id, full_deck, 'p')
        set_metrics(point, round_id, full_deck, 'o')
    
    point_pos1 = {}
    point_pos1['bc'] = point['bc']
    point_pos1['pos'] = 1
    point_pos1['p'] = {}
    point_pos1['o'] = {}
    point_pos1['p']['hc'] = point['o']['hc']
    point_pos1['o']['hc'] = point['p']['hc']
    point_pos1['p']['str'] = point['o']['str']
    point_pos1['p']['ep'] = point['o']['ep']
    point_pos1['o']['str'] = point['p']['str']
    point_pos1['o']['ep'] = point['p']['ep']

    return point, point_pos1

def generate_poker_hands(from_seed, to_seed):
    path = "hands_generated/hands"+str(to_seed)
    index = 0
    indeces = 9
    mapping = {'00': 0, '01': 1, '02': 2, '10': 3, '11': 4, '12': 5, '20': 6, '21': 7, '22': 8}

    print "starting"
    full_deck = PokerMetrics.initialize_deck()
    port0, port1 = available_ports()
    if not os.path.exists('hands_generated'):
        os.makedirs('hands_generated')
    if not os.path.exists(path):
        os.makedirs(path)
    files = []
    for x in range(indeces):
        files.append(open(path+'/hands_type_'+str(x)+'.json','a'))
    for seed in range(from_seed, to_seed):
        point_pos0, point_pos1 = initialize_metrics(seed, port0, port1, full_deck)
        point_pos0['id'] = seed
        point_pos1['id'] = seed
        label0_player = PokerConfig.get_hand_strength_label(point_pos0['p']['str'][index])
        label0_opp = PokerConfig.get_hand_strength_label(point_pos0['o']['str'][index])
        label1_player = PokerConfig.get_hand_strength_label(point_pos1['p']['str'][index])
        label1_opp = PokerConfig.get_hand_strength_label(point_pos1['o']['str'][index])
        label0 = str(label0_player)+str(label0_opp)
        label1 = str(label1_player)+str(label1_opp)
        print str(label0)+","+str(mapping[label0])+": "+str(point_pos0)
        print str(label1)+","+str(mapping[label1])+": "+str(point_pos1)
        print "#"
        files[mapping[label0]].write(json.dumps(point_pos0)+'\n')
        files[mapping[label1]].write(json.dumps(point_pos1)+'\n')
        print "#"
    for f in files:
        f.close()

if __name__ == "__main__":
    start_time = time.time()
    generate_poker_hands(from_seed=20000, to_seed=25000)
    elapsed_time = round_value((time.time() - start_time)/60.0)
    print("\nFinished, elapsed time: "+str(elapsed_time)+" mins")