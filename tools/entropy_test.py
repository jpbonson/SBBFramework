import numpy
from scipy import stats

def pdf(array):
    options = 3
    probs = [0] * options
    for value in array:
        probs[int(value)] += 1
    for index, value in enumerate(probs):
        probs[index] = value/float(len(array))
        if probs[index] == 0.0:
            probs[index] = 0.000000000001 # to avoid values being divided by 0
    total = sum(probs)
    for index, value in enumerate(probs):
        probs[index] = value/total
    return probs

# def relative_entropy1(action_sequence, other_action_sequence): # based on matlab + paper long version
#     options = 3
#     pdf1 = pdf(action_sequence)
#     other_pdf = pdf(other_action_sequence)
#     temp = 0.0
#     for x in range(options):
#         temp += pdf1[x]*numpy.log(pdf1[x]/other_pdf[x])
#     dxy = temp
#     temp = 0.0
#     for x in range(options):
#         temp += other_pdf[x]*numpy.log(other_pdf[x]/pdf1[x])
#     dyx = temp
#     total = (dxy + dyx)/float(options*2)
#     return total/9.21034037197

def relative_entropy1(action_sequence, other_action_sequence):
    pdf1 = pdf(action_sequence)
    other_pdf = pdf(other_action_sequence)
    distance1 = stats.entropy(pdf1, qk=other_pdf)
    distance1 = distance1/27.6310211158
    distance2 = stats.entropy(other_pdf, qk=pdf1)
    distance2 = distance2/27.6310211158
    return (distance1 + distance2)/2.0

if __name__ == "__main__":
    # 15 hands against random opponents
    # is able to detect that two arrays are distant because they dont have an action in common, but it 
    # is not able to differentiate a player that often fold and rerely raise from one that often raise and 
    # rarely fold
    folds = ['0', '0', '0', '0', '0', '0', '0', '0', '0', '0', '0', '0', '0', '0', '0', '0', '0']
    raises = ['2', '2', '2', '2', '2', '2', '2', '2', '2', '2', '2', '2', '2', '2', '2', '2', '2', '2', '2', '2', '2', '2', '2', '2', '2', '2', '2', '2', '2', '2', '2', '2', '2', '2', '2', '2', '2', '2', '2', '2', '2', '2', '2', '2', '2', '2', '2', '2', '2', '2', '2', '2', '2', '2', '2', '2', '2', '2', '2', '2', '2', '2', '2', '2', '2', '2', '2', '2']
    calls = ['1', '1', '1', '1', '1', '1', '1', '1', '1', '1', '1', '1', '1', '1', '1', '1', '1', '1', '1', '1', '1', '1', '1', '1', '1', '1', '1', '1', '1', '1', '1', '1', '1', '1', '1', '1', '1', '1', '1', '1', '1', '1', '1', '1', '1', '1', '1', '1', '1', '1', '1', '1', '1', '1', '1', '1', '1', '1', '1', '1', '1', '1', '1', '1']
    raises_2 = ['2', '2', '2', '2', '1', '2', '2', '2', '2', '2', '2', '2', '2', '2', '2', '2', '2', '2', '2', '2', '2', '2', '2', '2', '2']
    f1 = ['0', '0', '0', '0', '0', '0', '0', '0', '0', '0', '0', '0']
    fr = ['0', '0', '0', '0', '0', '0', '0', '0', '2', '2', '0', '2', '2', '2', '2', '0']
    fr_2 = ['0', '0', '0', '0', '0', '0', '0', '2', '2', '0', '0', '2', '2', '0', '0']
    fc = ['0', '0', '0', '0', '0', '0', '0', '0', '1', '1', '0', '1', '1', '1', '1', '0', '1', '1', '0', '1', '1', '1', '0', '0']
    cr = ['2', '2', '1', '1', '2', '1', '1', '1', '2', '1', '2', '1', '2', '2', '2', '1', '2', '2', '2', '1', '1', '1', '2', '2', '2', '2', '1', '2', '1', '2', '2', '2', '2', '2', '2']
    cr_2 = ['2', '2', '2', '2', '1', '2', '1', '2', '1', '2', '1', '2', '2', '2', '1', '2', '1', '2', '2', '2', '2', '2', '1', '1', '2', '1', '1', '2', '2', '2', '1', '2', '1', '2', '2', '1', '1', '1', '2']
    fc_2 = ['0', '0', '0', '0', '0', '0', '0', '1', '1', '1', '0', '0', '0', '1', '1', '0', '1', '1', '1', '1', '0', '0']
    fr2 = ['2', '0', '2', '2', '2', '2', '0', '2', '2', '2', '2', '2', '2', '2', '2', '2', '2', '2', '2', '2', '2', '2', '2', '2', '2', '2', '2', '2', '2', '2', '2']
    fcr = ['2', '0', '2', '2', '1', '1', '0', '2', '2', '1', '2', '2', '1', '1', '2', '2', '2', '2', '2', '1', '1', '2', '2', '2', '2', '2', '2', '2', '2', '1', '1']
    fr3 = ['2', '2', '2', '2', '2', '2', '2', '2', '0', '0', '2', '0', '0', '0', '0', '2']
    fcr2 = ['0', '1', '0', '0', '2', '2', '1', '0', '0', '2', '0', '0', '2', '2', '0', '0', '0', '0', '0', '2', '2', '0', '0', '0', '0', '0', '0', '0', '0', '2', '2']

    print "--- low distances => better"
    i = [raises, raises_2]
    print "raises x raises_2: "+str(relative_entropy1(i[0], i[1]))
    i = [fr, fr_2]
    print "fr x fr_2: "+str(relative_entropy1(i[0], i[1]))
    i = [cr, cr_2]
    print "cr x cr_2: "+str(relative_entropy1(i[0], i[1]))
    i = [fc, fc_2]
    print "fc x fc_2: "+str(relative_entropy1(i[0], i[1]))
    i = [fcr, fcr]
    print "fcr x fcr: "+str(relative_entropy1(i[0], i[1]))
    print "---"
    print "--- high distances => better"
    i = [folds, raises]
    print "folds x raises: "+str(relative_entropy1(i[0], i[1]))
    i = [folds, calls]
    print "folds x calls: "+str(relative_entropy1(i[0], i[1]))
    i = [raises, calls]
    print "raises x calls: "+str(relative_entropy1(i[0], i[1]))
    i = [fr, cr]
    print "fr x cr: "+str(relative_entropy1(i[0], i[1]))
    i = [cr, fc]
    print "cr x fc: "+str(relative_entropy1(i[0], i[1]))
    i = [fc, fr]
    print "fc x fr: "+str(relative_entropy1(i[0], i[1]))
    i = [folds, cr]
    print "folds x cr: "+str(relative_entropy1(i[0], i[1]))
    i = [calls, fr]
    print "calls x fr: "+str(relative_entropy1(i[0], i[1]))
    i = [raises, fc]
    print "raises x fc: "+str(relative_entropy1(i[0], i[1]))
    i = [fcr, fr]
    print "fcr x fr: "+str(relative_entropy1(i[0], i[1]))
    i = [fcr, fc]
    print "fcr x fc: "+str(relative_entropy1(i[0], i[1]))
    i = [calls, fr2]
    print "calls x fr2: "+str(relative_entropy1(i[0], i[1]))
    i = [fcr, cr]
    print "fcr x cr: "+str(relative_entropy1(i[0], i[1]))
    i = [fr, fr3]
    print "fr x fr3: "+str(relative_entropy1(i[0], i[1]))
    i = [fcr, fcr2]
    print "fcr x fcr2: "+str(relative_entropy1(i[0], i[1]))
    i = [f1, fr]
    print "f1 x fr: "+str(relative_entropy1(i[0], i[1]))
    print "---"

"""
manual:
--- low distances => better
raises x raises_2: 0.01769964793
fr x fr_2: 0.000981698359299
cr x cr_2: 1.33842559667e-05
fc x fc_2: 0.000178811913565
fcr x fcr: 0.0
---
--- high distances => better
folds x raises: 0.999999999998
folds x calls: 0.999999999998
raises x calls: 0.999999999998
fr x cr: 0.488612052714
cr x fc: 0.574158963603
fc x fr: 0.403756203299
folds x cr: 0.988062120243
calls x fr: 0.988028614008
raises x fc: 0.987519988393
fcr x fr: 0.164347871045
fcr x fc: 0.337223959199
calls x fr2: 0.995671222338
fcr x cr: 0.0294276475584
fr x fr3: 0.00462184895034
fcr x fcr2: 0.0354665993883
f1 x fr: 0.184033613287
---

scipy:
--- low distances => better
raises x raises_2: 0.0176996479301
fr x fr_2: 0.000981698359302
cr x cr_2: 1.33842559668e-05
fc x fc_2: 0.000178811913565
fcr x fcr: -0.0
---
--- high distances => better
folds x raises: 1.0
folds x calls: 1.0
raises x calls: 1.0
fr x cr: 0.488612052716
cr x fc: 0.574158963606
fc x fr: 0.403756203301
folds x cr: 0.988062120247
calls x fr: 0.988028614012
raises x fc: 0.987519988397
fcr x fr: 0.164347871046
fcr x fc: 0.337223959201
calls x fr2: 0.995671222342
fcr x cr: 0.0294276475585
fr x fr3: 0.00462184895036
fcr x fcr2: 0.0354665993885
f1 x fr: 0.184033613287
---

"""