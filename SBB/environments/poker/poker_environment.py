import sys
import errno
import socket
import time
from socket import error as socket_error
import os
import subprocess
import threading
import random
import numpy
from match_state import MatchState
from poker_match import PokerMatch
from poker_opponents import PokerRandomOpponent
from ..reinforcement_environment import ReinforcementEnvironment, ReinforcementPoint
from ...config import Config

class PokerPoint(ReinforcementPoint):
    """
    Encapsulates a poker opponent as a point.
    """

    def __init__(self, point_id, opponent):
        super(PokerPoint, self).__init__(point_id, opponent)
        self.seed_ = random.randint(0, Config.RESTRICTIONS['max_seed'])

class PokerEnvironment(ReinforcementEnvironment):
    """
    This environment encapsulates all methods to deal with a reinforcement learning task for TicTacToe.
    """

    ACTION_MAPPING = {0: 'f', 1: 'c', 2: 'r'}

    def __init__(self):
        total_actions = 3 # call, fold, raise
        total_inputs = MatchState.TOTAL_INPUTS
        coded_opponents = [PokerRandomOpponent] # TODO more opponents
        super(PokerEnvironment, self).__init__(total_actions, total_inputs, coded_opponents)
        self.total_positions_ = 2

    def instantiate_point_for_coded_opponent_class(self, opponent_class):
        instance = opponent_class()
        return PokerPoint(str(instance), instance)

    def instantiate_point_for_sbb_opponent(self, team):
        return PokerPoint(team.__repr__(), team)

    def play_match(self, team, point, is_training):
        """

        """
        # TODO temp, for debug
        team = PokerRandomOpponent()
        team.seed_ = 0
        point = self.instantiate_point_for_coded_opponent_class(PokerRandomOpponent)
        point.opponent.seed_ = 0
        point.seed_ = 0
        #

        if Config.USER['reinforcement_parameters']['debug_matches'] and not os.path.exists(Config.RESTRICTIONS['poker']['acpc_path']+"outputs/"):
            os.makedirs(Config.RESTRICTIONS['poker']['acpc_path']+"outputs/")

        t1 = threading.Thread(target=PokerEnvironment.execute_player, args=[team, Config.RESTRICTIONS['poker']['available_ports'][0], point.point_id, is_training])
        t2 = threading.Thread(target=PokerEnvironment.execute_player, args=[point.opponent, Config.RESTRICTIONS['poker']['available_ports'][1], None, False])
        p = subprocess.Popen([
                                Config.RESTRICTIONS['poker']['acpc_path']+'dealer', 
                                Config.RESTRICTIONS['poker']['acpc_path']+'outputs/test_match', 
                                Config.RESTRICTIONS['poker']['acpc_path']+'holdem.limit.2p.reverse_blinds.game', 
                                str(Config.USER['reinforcement_parameters']['poker']['total_hands']), 
                                str(point.seed_),
                                'sbb', 'opponent', 
                                '-p', str(Config.RESTRICTIONS['poker']['available_ports'][0]), str(Config.RESTRICTIONS['poker']['available_ports'][1]), 
                                '-l'
                            ], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        time.sleep(1) # so the dealer have enough time to initialize
        t1.start()
        t2.start()
        out, err = p.communicate()
        if Config.USER['reinforcement_parameters']['debug_matches']:
            with open(Config.RESTRICTIONS['poker']['acpc_path']+"outputs/match.log", "w") as text_file:
                text_file.write(str(err))
        score = out.split("\n")[1]
        score = score.replace("SCORE:", "")
        splitted_score = score.split(":")
        scores = splitted_score[0].split("|")
        players = splitted_score[1].split("|")
        if players[0] != 'sbb':
            print "\nbug!\n"
            raise SystemExit
        avg_score = float(scores[0])/float(Config.USER['reinforcement_parameters']['poker']['total_hands'])
        normalized_value = self._normalize_winning(avg_score)
        if Config.USER['reinforcement_parameters']['debug_matches']:
            print "scores: "+str(scores)
            print "players: "+str(players)
            print "avg score: "+str(avg_score)
            print "normalized_value: "+str(normalized_value)
        return normalized_value

    def _normalize_winning(self, value):
        max_winning = self._get_maximum_winning()
        max_losing = -max_winning
        return (value - max_losing)/(max_winning - max_losing)

    def _get_maximum_winning(self):
        max_small_bet_turn_winning = Config.RESTRICTIONS['poker']['small_bet']*4
        max_big_bet_turn_winning = Config.RESTRICTIONS['poker']['big_bet']*4
        return max_small_bet_turn_winning*2 + max_big_bet_turn_winning*2

    def metrics(self):
        msg = ""
        msg += "\n### Environment Info:"
        msg += "\ntotal inputs: "+str(self.total_inputs_)
        msg += "\ntotal actions: "+str(self.total_actions_)
        msg += "\nactions mapping: "+str(PokerEnvironment.ACTION_MAPPING)
        msg += "\npositions: "+str(self.total_positions_)
        msg += "\nmatches per opponents (for each position): "+str(self.population_size_)
        return msg

    @staticmethod
    def execute_player(player, port, point_id, is_training):
        socket_tmp = socket.socket()
        socket_tmp.connect(("localhost", port))
        if Config.USER['reinforcement_parameters']['debug_matches']:
            debug_file = open(Config.RESTRICTIONS['poker']['acpc_path']+'outputs/player'+str(port)+'.log','w')
        socket_tmp.send("VERSION:2.0.0\r\n")
        last_hand_id = -1
        has_folded = False
        while True:
            try:
                message = socket_tmp.recv(1000)
            except socket_error as e:
                if e.errno == errno.ECONNRESET:
                    break
                else:
                    raise e
            if not message:
                break
            message = message.replace("\r\n", "")
            partial_messages = message.split("MATCHSTATE")
            last_message = partial_messages[-1] # only cares about the last message sent (ie. the one where this player should act)
            match_state = MatchState(last_message)
            if match_state.hand_id != last_hand_id:
                last_hand_id = match_state.hand_id
                player.initialize() # so a probabilistic opponent will always play equal for the same hands and actions
                has_folded = False
            if Config.USER['reinforcement_parameters']['debug_matches']:
                debug_file.write("match_state: "+str(match_state)+"\n\n")
            if not has_folded and match_state.is_current_player_to_act() and not match_state.is_showdown():
                action = player.execute(point_id, match_state.inputs(), match_state.valid_actions(), is_training)
                if action is None:
                    action = "c"
                else:
                    action = PokerEnvironment.ACTION_MAPPING[action]
                if action == 'f':
                    has_folded = True
                send_msg = "MATCHSTATE"+last_message+":"+action+"\r\n"
                socket_tmp.send(send_msg)
                if Config.USER['reinforcement_parameters']['debug_matches']:
                    debug_file.write("send_msg: "+str(send_msg)+"\n\n")
            else:
                if Config.USER['reinforcement_parameters']['debug_matches']:
                    debug_file.write("nothing to do\n\n")
        socket_tmp.close()
        if Config.USER['reinforcement_parameters']['debug_matches']:
            debug_file.write("The end.\n\n")
            debug_file.close()