import subprocess
import threading
from poker_test import PokerPlayer

def task1():
    print "starting game 1"
    p1 = PokerPlayer()
    p1.initialize(18790)
    p1.execute()

def task2():
    print "starting game 2"
    p2 = PokerPlayer()
    p2.initialize(18791)
    p2.execute()

t1 = threading.Thread(target=task1)
t2 = threading.Thread(target=task2)
p = subprocess.Popen(['./ACPC/dealer', './ACPC/results/test_match', './ACPC/holdem.limit.2p.reverse_blinds.game', '7', '0', 'Alice', 'Bob', '-p', '18790', '18791'], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
print "starting game 3"
t1.start()
t2.start()
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

# escrever output dos players em arquivo
# fazer port serem attributes