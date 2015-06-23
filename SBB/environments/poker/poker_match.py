import sys
import errno
import socket
from socket import error as socket_error
import os
import subprocess
import threading
from poker_opponents import PokerRandomOpponent
from ...config import Config

class PokerMatch2():
    """
    
    """

    def __init__(self):
        self.inputs_ = [] # TODO
        self.result_ = -1
        self.print_game_ = Config.USER['reinforcement_parameters']['debug_matches']

    def perform_action(self, current_player, action):
        """
        
        """
        pass # TODO
        # self.inputs_[action] = current_player
        # if self.print_game_:
        #     print "---"
        #     print str(self.inputs_[0:3])
        #     print str(self.inputs_[3:6])
        #     print str(self.inputs_[6:9])

    def valid_actions(self):
        """
        
        """
        pass # TODO
        # valids = []
        # for index, space in enumerate(self.inputs_):
        #     if space == TictactoeMatch.EMPTY:
        #         valids.append(index)
        # return valids

    def inputs_from_the_point_of_view_of(self, position):
        """
        
        """
        pass # TODO
        # if position == 1:
        #     return list(self.inputs_)
        # else:
        #     mapping = [0, 2, 1]
        #     inputs = [mapping[x] for x in self.inputs_]
        #     return inputs

    def is_over(self):
        """
        
        """
        pass # TODO
        # winner = TictactoeMatch.get_winner(self.inputs_)
        # if winner:
        #     self.result_ = winner
        #     if self.print_game_:
        #         print "It is over! Player "+str(self.result_)+" wins!"
        #     return True
        # for value in self.inputs_:
        #     if value == TictactoeMatch.EMPTY:
        #         if self.print_game_:
        #             print "Go!"
        #         return False
        # self.result_ = TictactoeMatch.DRAW
        # if self.print_game_:
        #     print "It is over! Draw!"
        # return True

    def result_for_player(self, current_player):
        if self.result_ == current_player:
            return 1 # win
        if self.result_ == TictactoeMatch.DRAW:
            return 0.5 # draw
        else:
            return 0 # lose

    @staticmethod
    def get_winner(inputs):
        winning_configs = ((0, 1, 2), (3, 4, 5), (6, 7, 8), (0, 3, 6),
                       (1, 4, 7), (2, 5, 8), (0, 4, 8), (2, 4, 6))
        for config in winning_configs:
            if inputs[config[0]] == inputs[config[1]] and inputs[config[1]] == inputs[config[2]]:
                return inputs[config[0]]
        return None # no winner

class MatchState():
    def __init__(self, message):
        self.position = None
        self.hand_number = None
        self.rounds = None
        self.hole_cards = None
        self.current_hole_cards = None
        self.opponent_hole_cards = None
        self.board_cards = None
        self._decode_message(message)

    def _decode_message(self, message):
        splitted = message.split(":")
        self.position = int(splitted[1])
        self.hand_number = int(splitted[2])
        self.rounds = splitted[3].split("/")
        cards = splitted[4].split("/")
        self.hole_cards = cards[0].split("|")
        if self.position == 0:
            self.current_hole_cards = self.hole_cards[0]
            self.opponent_hole_cards = self.hole_cards[1]
        else:
            self.current_hole_cards = self.hole_cards[1]
            self.opponent_hole_cards = self.hole_cards[0]
        self.board_cards = cards[1:-1]

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

    def __str__(self):
        msg = "\n"
        msg += "position: "+str(self.position)+"\n"
        msg += "hand_number: "+str(self.hand_number)+"\n"
        msg += "rounds: "+str(self.rounds)+"\n"
        msg += "hole_cards: "+str(self.hole_cards)+"\n"
        msg += "current_hole_cards: "+str(self.current_hole_cards)+"\n"
        msg += "opponent_hole_cards: "+str(self.opponent_hole_cards)+"\n"
        msg += "board_cards: "+str(self.board_cards)+"\n"
        return msg

path = "SBB/environments/poker/ACPC"

def player(player, port):
    debug = Config.USER['reinforcement_parameters']['debug_matches']
    socket_tmp = socket.socket()
    socket_tmp.connect(("localhost", port))
    if debug:
        debug_file = open(path+'/outputs/player'+str(port)+'.log','w')
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
            action = player.execute(point_id = None, inputs = None, valid_actions = ["c"], is_training = None)
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

class PokerMatch():
    """

    """

    def _play_match(self):
        if not os.path.exists(path+"/outputs/"):
            os.makedirs(path+"/outputs/")
        debug = True
        players_ids = ['Alice', 'Bob']
        ports = [18790, 18791]
        total_hand = 7
        seed = 0

        p1 = PokerRandomOpponent()
        p2 = PokerRandomOpponent()
        p1.initialize()
        p2.initialize()
        t1 = threading.Thread(target=player, args=[p1, ports[0]])
        t2 = threading.Thread(target=player, args=[p2, ports[1]])
        p = subprocess.Popen([path+'/dealer', path+'/outputs/test_match', path+'/holdem.limit.2p.reverse_blinds.game', str(total_hand), str(seed),
            players_ids[0], players_ids[1], '-p', str(ports[0]), str(ports[1]), '-l'], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        t1.start()
        t2.start()
        out, err = p.communicate()
        if debug:
            with open(path+"/outputs/match.log", "w") as text_file:
                text_file.write(str(err))
        score = out.split("\n")[1]
        score = score.replace("SCORE:", "")
        splitted_score = score.split(":")
        scores = splitted_score[0].split("|")
        players = splitted_score[1].split("|")
        print "scores: "+str(scores)
        print "players: "+str(players)