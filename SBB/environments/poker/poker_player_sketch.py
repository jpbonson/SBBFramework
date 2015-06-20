import sys
import errno
import socket
from socket import error as socket_error

# import random
# import numpy
# from ..default_opponent import DefaultOpponent
# from ...config import Config

# class PokerRandomOpponent(DefaultOpponent):
#     def __init__(self):
#         super(PokerRandomOpponent, self).__init__("random")
#         self.seed_ = random.randint(0, Config.RESTRICTIONS['max_seed'])

#     def initialize(self):
#         self.random_generator_ = numpy.random.RandomState(seed=self.seed_)

#     def execute(self, point_id, inputs, valid_actions, is_training):
#         return self.random_generator_.choice(valid_actions)

#     def __str__(self):
#         return self.opponent_id +":"+str(self.seed_)

#     def __repr__(self):
#         return self.opponent_id +":"+str(self.seed_)

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

class PokerPlayer():

    def __init__(self):
        self.debug = True

    def initialize(self, port):
        self.socket = socket.socket()
        self.socket.connect(("localhost", port))
        if self.debug:
            self.debug_file = open('./ACPC/outputs/player'+str(port)+'.log','w')

    def execute(self):
        self.socket.send("VERSION:2.0.0\r\n")
        while True:
            try:
                message = self.socket.recv(1000)
            except socket_error as e:
                if e.errno == errno.ECONNRESET:
                    break
                else:
                    raise e
            if not message:
                break
            message = message.replace("\r\n", "")
            if self.debug:
                self.debug_file.write("messages: "+str(message)+"\n\n")
            partial_messages = message.split("MATCHSTATE")
            message = partial_messages[-1] # only cares about the last message sent (ie. the one where this player should act)
            match_state = MatchState(message)
            if self.debug:
                self.debug_file.write("last_message: "+str(message)+"\n\n")
                self.debug_file.write("match_state: "+str(match_state)+"\n\n")
            if match_state.is_current_player_to_act() and not match_state.is_showdown():
                send_msg = "MATCHSTATE"+message+":c\r\n"
                self.socket.send(send_msg)
                if self.debug:
                    self.debug_file.write("send_msg: "+str(send_msg)+"\n\n")
            else:
                if self.debug:
                    self.debug_file.write("nothing to do\n\n")
        if self.debug:
            self.debug_file.write("The end.\n\n")
        self.finalize()

    def finalize(self):
        self.socket.close()
        if self.debug:
            self.debug_file.close()