import subprocess

p = subprocess.Popen(['./ACPC/dealer', './ACPC/results/test_match', './ACPC/holdem.limit.2p.reverse_blinds.game', '7', '0', 'Alice', 'Bob', '-p', '18790', '18791'], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
out, err = p.communicate()
print "err: "+err
print "out: "+out
score = out.split("\n")[1]
print "score: "+score
score = score.replace("SCORE:", "")
print "splitted: "+str(score.split(":"))

# corrigir, unrequested responses sendo enviadas!
# chamar players nesse arquivo