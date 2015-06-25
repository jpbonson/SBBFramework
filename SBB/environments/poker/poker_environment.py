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
        self.seed = random.randint(0, Config.RESTRICTIONS['max_seed'])

class PokerEnvironment(ReinforcementEnvironment):
    """
    This environment encapsulates all methods to deal with a reinforcement learning task for TicTacToe.
    """

    def __init__(self):
        total_actions = 3 # call, fold, raise
        total_inputs = None # TODO
        coded_opponents = [PokerRandomOpponent] # TODO more opponents
        super(PokerEnvironment, self).__init__(total_actions, total_inputs, coded_opponents)
        self.total_positions_ = 2
        self.action_mapping_ = {'fold': 0, 'call': 1, 'raise': 2}

    def instantiate_point_for_coded_opponent_class(self, opponent_class):
        instance = opponent_class()
        return PokerPoint(str(instance), instance)

    def instantiate_point_for_sbb_opponent(self, team):
        return PokerPoint(team.__repr__(), team)

    def play_match(self, team, point, is_training):
        """

        """
        # temp, for debug
        team = PokerRandomOpponent()
        team.initialize()
        point = self.instantiate_point_for_coded_opponent_class(PokerRandomOpponent)
        point.seed = 0
        #

        if not os.path.exists(Config.RESTRICTIONS['poker']['acpc_path']+"outputs/"):
            os.makedirs(Config.RESTRICTIONS['poker']['acpc_path']+"outputs/")
        debug = True

        point.opponent.initialize()
        t1 = threading.Thread(target=PokerEnvironment.execute_player, args=[team, Config.RESTRICTIONS['poker']['available_ports'][0]])
        t2 = threading.Thread(target=PokerEnvironment.execute_player, args=[point.opponent, Config.RESTRICTIONS['poker']['available_ports'][1]])
        p = subprocess.Popen([
                                Config.RESTRICTIONS['poker']['acpc_path']+'dealer', 
                                Config.RESTRICTIONS['poker']['acpc_path']+'outputs/test_match', 
                                Config.RESTRICTIONS['poker']['acpc_path']+'holdem.limit.2p.reverse_blinds.game', 
                                str(Config.USER['reinforcement_parameters']['poker']['total_hand']), 
                                str(point.seed),
                                'sbb', 'opponent', 
                                '-p', str(Config.RESTRICTIONS['poker']['available_ports'][0]), str(Config.RESTRICTIONS['poker']['available_ports'][1]), 
                                '-l'
                            ], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        time.sleep(1) # so the dealer have enough time to initialize
        t1.start()
        t2.start()
        out, err = p.communicate()
        if debug:
            with open(Config.RESTRICTIONS['poker']['acpc_path']+"outputs/match.log", "w") as text_file:
                text_file.write(str(err))
        score = out.split("\n")[1]
        score = score.replace("SCORE:", "")
        splitted_score = score.split(":")
        scores = splitted_score[0].split("|")
        players = splitted_score[1].split("|")
        print "scores: "+str(scores)
        print "players: "+str(players)
        if players[0] != 'sbb':
            print "\nbug!\n"
            raise SystemExit
        avg_score = float(scores[0])/float(Config.USER['reinforcement_parameters']['poker']['total_hand'])
        print "avg score: "+str(avg_score)
        normalized_value = self._normalize_winning(avg_score)
        print "normalized_value: "+str(normalized_value)
        return normalized_value

        # outputs = []
        # for position in range(1, self.total_positions_+1):
        #     if position == 1:
        #         first_player = point.opponent
        #         is_training_for_first_player = False
        #         second_player = team
        #         is_training_for_second_player = is_training
        #         sbb_player = 2
        #     else:
        #         first_player = team
        #         is_training_for_first_player = is_training
        #         second_player = point.opponent
        #         is_training_for_second_player = False
        #         sbb_player = 1

        #     match = TictactoeMatch()
        #     point.opponent.initialize()
        #     while True:
        #         player = 1
        #         inputs = match.inputs_from_the_point_of_view_of(player)
        #         action = first_player.execute(point.point_id, inputs, match.valid_actions(), is_training_for_first_player)
        #         if action is None:
        #             action = random.choice(match.valid_actions())
        #         match.perform_action(player, action)
        #         if match.is_over():
        #             outputs.append(match.result_for_player(sbb_player))
        #             break
        #         player = 2
        #         inputs = match.inputs_from_the_point_of_view_of(player)
        #         action = second_player.execute(point.point_id, inputs, match.valid_actions(), is_training_for_second_player)
        #         if action is None:
        #             action = random.choice(match.valid_actions())
        #         match.perform_action(player, action)
        #         if match.is_over():
        #             outputs.append(match.result_for_player(sbb_player))
        #             break
        # return numpy.mean(outputs)

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
        msg += "\nactions mapping: "+str(self.action_mapping_)
        msg += "\npositions: "+str(self.total_positions_)
        msg += "\nmatches per opponents (for each position): "+str(self.population_size_)
        return msg

    @staticmethod
    def execute_player(player, port):
        debug = Config.USER['reinforcement_parameters']['debug_matches']
        socket_tmp = socket.socket()
        socket_tmp.connect(("localhost", port))
        if debug:
            debug_file = open(Config.RESTRICTIONS['poker']['acpc_path']+'outputs/player'+str(port)+'.log','w')
        socket_tmp.send("VERSION:2.0.0\r\n")
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
            if debug:
                debug_file.write("messages: "+str(message)+"\n\n")
                debug_file.write("last_message: "+str(last_message)+"\n\n")
                debug_file.write("match_state: "+str(match_state)+"\n\n")
            if match_state.is_current_player_to_act() and not match_state.is_showdown():
                action = player.execute(point_id = None, inputs = None, valid_actions = ["r"], is_training = None)
                send_msg = "MATCHSTATE"+last_message+":"+action+"\r\n"
                socket_tmp.send(send_msg)
                if debug:
                    debug_file.write("send_msg: "+str(send_msg)+"\n\n")
            else:
                if debug:
                    debug_file.write("nothing to do\n\n")
        socket_tmp.close()
        if debug:
            debug_file.write("The end.\n\n")
            debug_file.close()