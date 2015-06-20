import subprocess
from poker_test import PokerPlayer

p = subprocess.Popen(['./ACPC/dealer', './ACPC/results/test_match', './ACPC/holdem.limit.2p.reverse_blinds.game', '7', '0', 'Alice', 'Bob', '-p', '18790', '18791'], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
# PokerPlayer(18790).execute()
# PokerPlayer(18791).execute()
out, err = p.communicate()
print "err: "+err
print "out: "+out
score = out.split("\n")[1]
score = score.replace("SCORE:", "")
splitted_score = score.split(":")
scores = splitted_score[0].split("|")
players = splitted_score[1].split("|")
print "scores: "+str(scores)
print "players: "+str(players)

# chamar players nesse arquivo