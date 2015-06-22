import sys
import errno
import socket
from socket import error as socket_error
# from ..default_opponent import DefaultOpponent
# from ...config import Config
import os
import subprocess
import threading
# from poker_player_sketch import PokerPlayer

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
    debug = True # Config.USER['reinforcement_parameters']['debug_matches']
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
        if debug:
            debug_file.write("messages: "+str(message)+"\n\n")
        partial_messages = message.split("MATCHSTATE")
        message = partial_messages[-1] # only cares about the last message sent (ie. the one where this player should act)
        match_state = MatchState(message)
        if debug:
            debug_file.write("last_message: "+str(message)+"\n\n")
            debug_file.write("match_state: "+str(match_state)+"\n\n")
        if match_state.is_current_player_to_act() and not match_state.is_showdown():
            send_msg = "MATCHSTATE"+message+":c\r\n"
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

if not os.path.exists(path+"/outputs/"):
    os.makedirs(path+"/outputs/")
debug = True
players_ids = ['Alice', 'Bob']
ports = [18790, 18791]
total_hand = 7
seed = 0

# p1 = PokerPlayer()
# p2 = PokerPlayer()
p1 = None
p2 = None
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

# mix o player_sketch e a classe de oponents
# mix match_sketch e a classe de match