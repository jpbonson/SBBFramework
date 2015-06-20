import os
import subprocess
import threading
from poker_player_sketch import PokerPlayer

def player(player, port):
    player.initialize(port)
    player.execute()

if not os.path.exists("./ACPC/outputs/"):
    os.makedirs("./ACPC/outputs/")
debug = True
players_ids = ['Alice', 'Bob']
ports = [18790, 18791]
total_hand = 7
seed = 0

p1 = PokerPlayer()
p2 = PokerPlayer()
t1 = threading.Thread(target=player, args=[p1, ports[0]])
t2 = threading.Thread(target=player, args=[p2, ports[1]])
p = subprocess.Popen(['./ACPC/dealer', './ACPC/outputs/test_match', './ACPC/holdem.limit.2p.reverse_blinds.game', str(total_hand), str(seed),
    players_ids[0], players_ids[1], '-p', str(ports[0]), str(ports[1]), '-l'], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
t1.start()
t2.start()
out, err = p.communicate()
if debug:
    with open("./ACPC/outputs/match.log", "w") as text_file:
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