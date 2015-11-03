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
from SBB.environments.poker.poker_metrics import PokerMetrics
from SBB.utils.helpers import available_ports, round_value
from SBB.config import Config

def test_execution(point, port, full_deck):
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
            try:
                match_state = MatchState(last_message, PokerConfig.CONFIG['small_bet'], PokerConfig.CONFIG['big_bet'])
            except ValueError as e:
                print "---ERROR in initialization of MatchState:"
                print "last_message: "+str(last_message)
                print "partial_messages: "+str(partial_messages)
                print "message: "+str(message)
                print "previous_messages: "+str(previous_messages)
                print "---"
                raise
            action = "c"
            send_msg = "MATCHSTATE"+last_message+":"+action+"\r\n"
            socket_tmp.send(send_msg)
            round_id = len(match_state.rounds)
            s = PokerMetrics.calculate_hand_strength(match_state.current_hole_cards, match_state.board_cards, full_deck)
            if round_id == 2 or round_id == 3:
                p = PokerMetrics.calculate_hand_potential_without_heuristics(match_state.current_hole_cards, match_state.board_cards, round_id, full_deck)
            else:
                p = 0
            e = PokerMetrics.calculate_equity(match_state.current_hole_cards)
            ep = PokerMetrics.calculate_ep(s, e, p, round_id)
            point['str'][round_id-1] = round_value(s*Config.RESTRICTIONS['multiply_normalization_by'], 3)
            # point['pot'][round_id-1] = round_value(p, 3)
            # point['eq'] = round_value(e)
            point['ep'][round_id-1] = round_value(ep*Config.RESTRICTIONS['multiply_normalization_by'], 3)
            point['final'] = s
    except socket_error as e:
        print "socket_error: "+str(e)
        if e.errno != errno.ECONNRESET and e.errno != errno.EPIPE:
            raise ValueError("Error: "+str(e))
    socket_tmp.close()

    try:
        point['hole_cards'] = match_state.current_hole_cards
        point['board_cards'] = match_state.board_cards
        point['p'] = match_state.position
    except:
        print "--- ERROR:"
        print "socket_tmp: "+str(socket_tmp)
        print "total: "+str(total)
        print "attempt: "+str(attempt)
        print "point: "+str(point)
        print "port: "+str(port)
        print "full_deck: "+str(full_deck)
        if message:
            print "message: "+str(message)
        print "---"
        raise

def initialize_metrics(seed, port_pos0, port_pos1, full_deck):
    point_pos0 = {}
    point_pos1 = {}
    point_pos0['str'] = [-1] * 4
    point_pos1['str'] = [-1] * 4
    # point_pos0['pot'] = [-1] * 4
    # point_pos1['pot'] = [-1] * 4
    point_pos0['ep'] = [-1] * 4
    point_pos1['ep'] = [-1] * 4

    t1 = threading.Thread(target=test_execution, args=[point_pos0, port_pos0, full_deck])
    t2 = threading.Thread(target=test_execution, args=[point_pos1, port_pos1, full_deck])
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

    # print str(point_pos0['str'])+", "+str(point_pos0['ep'])+", "+str(point_pos0['hole_cards']+point_pos0['board_cards'])
    # print str(point_pos1['str'])+", "+str(point_pos1['ep'])+", "+str(point_pos1['hole_cards']+point_pos1['board_cards'])

    point_pos0['oep'] = point_pos1['ep']
    point_pos1['oep'] = point_pos0['ep']
    point_pos0['ostr'] = point_pos1['str']
    point_pos1['ostr'] = point_pos0['str']

    return point_pos0, point_pos1

if __name__ == "__main__":
    # 'hand strength' for the 4 rounds, 'EHS' for the 4 rounds, + labels (strength, ehs? holes+board strength?), win, draw or loose showdown
    # organizar arquivos pelas labels, uma seed por linha
    # inicialmente, pegar 1000 hands

    Config.USER['reinforcement_parameters']['poker']['balance_based_on'] = 'pstr_ostr'
    path = "hand_types_temp/pstr_ostr40000"
    index = 3
    indeces = 9
    mapping = {'00': 0, '01': 1, '02': 2, '10': 3, '11': 4, '12': 5, '20': 6, '21': 7, '22': 8}

    print "starting"
    start_time = time.time()
    full_deck = PokerMetrics.initialize_deck()
    port0, port1 = available_ports()
    if not os.path.exists('hand_types_temp'):
        os.makedirs('hand_types_temp')
    if not os.path.exists(path):
        os.makedirs(path)
    files = []
    for x in range(indeces):
        files.append(open(path+'/hands_type_'+str(x)+'.json','a'))
    for seed in range(35000, 40000):
        point_pos0, point_pos1 = initialize_metrics(seed, port0, port1, full_deck)
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
        label0_player = PokerConfig.get_hand_strength_label(point_pos0['str'][index])
        label0_opp = PokerConfig.get_hand_strength_label(point_pos0['ostr'][index])
        label1_player = PokerConfig.get_hand_strength_label(point_pos1['str'][index])
        label1_opp = PokerConfig.get_hand_strength_label(point_pos1['ostr'][index])
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
    elapsed_time = time.time() - start_time
    print "finishing, "+str(elapsed_time)+" secs"