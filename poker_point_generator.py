import os
import json
import random
import time
import errno
import socket
from socket import error as socket_error
import subprocess
import threading
from SBB.environments.poker.match_state import MatchState
from SBB.environments.poker.poker_config import PokerConfig
from SBB.environments.poker.tables.strenght_table_for_2cards import STRENGTH_TABLE_FOR_2_CARDS
from SBB.environments.poker.tables.normalized_equity_table import NORMALIZED_HAND_EQUITY
from SBB.environments.poker.poker_metrics import *
from SBB.utils.helpers import available_ports, round_value

def test_execution(point, port, full_deck, hole_cards_based_on_equity):
    socket_tmp = socket.socket()

    total = 10
    attempt = 0
    while True:
        try:
            socket_tmp.connect(("localhost", port))
            break
        except socket_error as e:
            attempt += 1
            if e.errno == errno.ECONNREFUSED:
                time.sleep(1)
            if attempt > total:
                raise ValueError("Could not connect to port "+str(port))

    socket_tmp.send("VERSION:2.0.0\r\n")

    try:
        while True:
            message = socket_tmp.recv(1000)
            message = message.replace("\r\n", "")
            partial_messages = message.split("MATCHSTATE")
            if partial_messages[-1]:
                last_message = partial_messages[-1] # only cares about the last message sent (ie. the one where this player should act)
            match_state = MatchState(last_message, PokerConfig.CONFIG['small_bet'], PokerConfig.CONFIG['big_bet'])
            action = "c"
            send_msg = "MATCHSTATE"+last_message+":"+action+"\r\n"
            socket_tmp.send(send_msg)
            round_id = len(match_state.rounds)
            s = calculate_hand_strength(match_state.current_hole_cards, match_state.board_cards, full_deck)
            if round_id == 2 or round_id == 3:
                # p = calculate_hand_potential(match_state.current_hole_cards, match_state.board_cards, round_id, full_deck, hole_cards_based_on_equity)
                p = calculate_hand_potential_without_heuristics(match_state.current_hole_cards, match_state.board_cards, round_id, full_deck)
            else:
                p = 0
            e = calculate_equity(match_state.current_hole_cards)
            ehs = calculate_ehs(s, e, p, round_id)
            point['str'][round_id-1] = round_value(s, 3)
            # point['pot'][round_id-1] = round_value(p, 3)
            # point['eq'] = round_value(e)
            point['ehs'][round_id-1] = round_value(ehs, 3)
            point['final'] = s
    except socket_error as e:
        if e.errno != errno.ECONNRESET and e.errno != errno.EPIPE:
            raise ValueError("Error: "+str(e))
    socket_tmp.close()

    point['hole_cards'] = match_state.current_hole_cards
    point['board_cards'] = match_state.board_cards
    point['p'] = match_state.position

def initialize_metrics(seed, port_pos0, port_pos1, full_deck, hole_cards_based_on_equity):
    point_pos0 = {}
    point_pos1 = {}
    point_pos0['str'] = [-1] * 4
    point_pos1['str'] = [-1] * 4
    # point_pos0['pot'] = [-1] * 4
    # point_pos1['pot'] = [-1] * 4
    point_pos0['ehs'] = [-1] * 4
    point_pos1['ehs'] = [-1] * 4

    t1 = threading.Thread(target=test_execution, args=[point_pos0, port_pos0, full_deck, hole_cards_based_on_equity])
    t2 = threading.Thread(target=test_execution, args=[point_pos1, port_pos1, full_deck, hole_cards_based_on_equity])
    args = [PokerConfig.CONFIG['acpc_path']+'dealer', 
            PokerConfig.CONFIG['acpc_path']+'outputs/match_output', 
            PokerConfig.CONFIG['acpc_path']+'holdem.limit.2p.reverse_blinds.game', 
            "1", # total hands 
            str(seed),
            'pos0', 'pos1', 
            '-p', str(port_pos0)+","+str(port_pos1),
            '-l']
    p = subprocess.Popen(args, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    t1.start()
    t2.start()
    out, err = p.communicate()
    t1.join()
    t2.join()

    point_pos0['oehs'] = point_pos1['ehs']
    point_pos1['oehs'] = point_pos0['ehs']
    point_pos0['ostr'] = point_pos1['str']
    point_pos1['ostr'] = point_pos0['str']

    return point_pos0, point_pos1

if __name__ == "__main__":
    # 'hand strength' for the 4 rounds, 'EHS' for the 4 rounds, + labels (strength, ehs? holes+board strength?), win, draw or loose showdown
    # organizar arquivos pelas labels, uma seed por linha
    # inicialmente, pegar 1000 hands

    path = "hand_types/board_strength"
    index = 3

    # path = "hand_types/hole_cards_strength"
    # index = 0

    print "starting"
    full_deck = initialize_deck()
    hole_cards_based_on_equity = initialize_hole_cards_based_on_equity()
    port0, port1 = available_ports()
    if not os.path.exists('hands_types'):
        os.makedirs('hands_types')
    if not os.path.exists(path):
        os.makedirs(path)
    files = []
    for x in range(4):
        files.append(open(path+'/hands_type_'+str(x)+'.json','w'))
    for seed in range(1000):
        point_pos0, point_pos1 = initialize_metrics(seed, port0, port1, full_deck, hole_cards_based_on_equity)
        point_pos0['id'] = seed
        point_pos1['id'] = seed
        point_pos0.pop('hole_cards')
        point_pos1.pop('hole_cards')
        point_pos0.pop('board_cards')
        point_pos1.pop('board_cards')
        if point_pos0['final'] > point_pos1['final']:
            point_pos0['r'] = 1.0
            point_pos1['r'] = 0.0
        elif point_pos0['final'] < point_pos1['final']:
            point_pos0['r'] = 0.0
            point_pos1['r'] = 1.0
        else:
            point_pos0['r'] = 0.5
            point_pos1['r'] = 0.5
        point_pos0.pop('final')
        point_pos1.pop('final')
        label0 = get_label(point_pos0['str'][index], 'hand_strength_labels')
        label1 = get_label(point_pos1['str'][index], 'hand_strength_labels')
        print str(label0)+": "+str(point_pos0)
        print str(label1)+": "+str(point_pos1)
        files[label0].write(json.dumps(point_pos0)+'\n')
        files[label1].write(json.dumps(point_pos1)+'\n')
    for f in files:
        f.close()
    print "finishing"