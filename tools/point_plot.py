import pylab as pl
import json
import numpy
import matplotlib.patches as mpatches

def round_value(value, round_decimals_to = 4):
    number = float(10**round_decimals_to)
    return int(value * number) / number

filename = 'properties_per_team__sbb_trained_against_bayesian_vs_bayesian_opponent__1260_balanced_points.json'

with open(filename) as data_file:    
    data = json.load(data_file)

all_teams = []
for value in data.values():
    all_teams += value

print str(all_teams[0].values()[0])
print str(all_teams[0].values()[0].keys())

x = []
y = []
scores = {}
scores['scores'] = []
scores['position'] = {}
scores['position']['0'] = []
scores['position']['1'] = []
scores['sbb_label'] = {}
for index in range(0, 9):
    scores['sbb_label'][index] = []
scores['sbb_sd'] = {}
for index in range(0, 3):
    scores['sbb_sd'][index] = []
scores['hands_played'] = {}
scores['hands_played']['total'] = []
scores['hands_played']['played'] = []
scores['hands_played']['won'] = []
scores['hands_played']['total2'] = []
scores['hands_played']['played2'] = []
scores['hands_played']['won2'] = []
scores['properties'] = {}
scores['properties']['bluffing_only_raise'] = []
scores['properties']['normalized_result_std'] = []
scores['properties']['passive_aggressive'] = []
scores['properties']['agressiveness'] = []
scores['properties']['tight_loose'] = []
scores['properties']['bluffing'] = []
scores['properties']['normalized_result_mean'] = []

# metric_name = 'wins'
# metric_name = 'played'
metric_name = 'agressiveness'
# metric_name = 'bluffing'
# metric_name = 'bluffing_only_raise'
for value in all_teams:

    # if metric_name == 'wins':
    #     if value.values()[0]['hands_played']['overall']['won'] is not None:
    #         total_wins = value.values()[0]['hands_played']['overall']['played']*value.values()[0]['hands_played']['overall']['won']
    #     else:
    #         total_wins = 0.0
    #     x.append(total_wins)
    # elif metric_name == 'played':
    #     x.append(value.values()[0]['hands_played']['overall']['played'])
    # else:
    #     x.append(value.values()[0]['properties'][metric_name])

    # y.append(value.values()[0]['properties']['normalized_result_mean'])


    x.append(value.values()[0]['properties']['passive_aggressive'])
    y.append(value.values()[0]['properties']['tight_loose'])


    scores['properties']['bluffing_only_raise'].append(value.values()[0]['properties']['bluffing_only_raise'])
    scores['properties']['normalized_result_std'].append(value.values()[0]['properties']['normalized_result_std'])
    scores['properties']['passive_aggressive'].append(value.values()[0]['properties']['passive_aggressive'])
    scores['properties']['agressiveness'].append(value.values()[0]['properties']['agressiveness'])
    scores['properties']['tight_loose'].append(value.values()[0]['properties']['tight_loose'])
    scores['properties']['bluffing'].append(value.values()[0]['properties']['bluffing'])
    scores['properties']['normalized_result_mean'].append(value.values()[0]['properties']['normalized_result_mean'])

    scores['scores'].append(value.values()[0]['properties']['normalized_result_mean'])
    scores['position']['0'].append(value.values()[0]['points']['position']['0'])
    scores['position']['1'].append(value.values()[0]['points']['position']['1'])
    for index in range(0, 9):
        scores['sbb_label'][index].append(value.values()[0]['points']['sbb_label'][str(index)])
    for index in range(0, 3):
        scores['sbb_sd'][index].append(value.values()[0]['points']['sbb_sd'][str(index)])
    scores['hands_played']['total'].append(value.values()[0]['hands_played']['overall']['total'])
    scores['hands_played']['played'].append(value.values()[0]['hands_played']['overall']['played'])
    if value.values()[0]['hands_played']['overall']['won'] is not None:
        scores['hands_played']['won'].append(value.values()[0]['hands_played']['overall']['won'])

    scores['hands_played']['total2'].append((value.values()[0]['hands_played']['position']['0']['total']+value.values()[0]['hands_played']['position']['1']['total'])/2.0)
    scores['hands_played']['played2'].append((value.values()[0]['hands_played']['position']['0']['played']+value.values()[0]['hands_played']['position']['1']['played'])/2.0)
    if value.values()[0]['hands_played']['position']['0']['won'] is not None and value.values()[0]['hands_played']['position']['1']['won'] is not None:
        scores['hands_played']['won2'].append((value.values()[0]['hands_played']['position']['0']['won']+value.values()[0]['hands_played']['position']['1']['won'])/2.0)
    # print "value.values()[0]: "+str(value.values()[0]['hands_played']['position'])
    # print "value.values()[0].keys(): "+str(value.values()[0]['hands_played']['position'].keys())
    # raise SystemExit

print
print "Scores (mean): "+str(round_value(numpy.mean(scores['scores'])))
print "Scores (max): "+str(max(scores['scores']))
print
print "Positions"
print "- 0: "+str(round_value(numpy.mean(scores['position']['0'])))
print "- 1: "+str(round_value(numpy.mean(scores['position']['1'])))
print
print "Hand Strengths"
for index in range(0, 9):
    print "- "+str(index)+": "+str(round_value(numpy.mean(scores['sbb_label'][index])))
print
print "Showdowns"
for index in range(0, 3):
    print "- "+str(index)+": "+str(round_value(numpy.mean(scores['sbb_sd'][index])))
print
print "Hands Played"
print "- total: "+str(round_value(numpy.mean(scores['hands_played']['total'])))
print "- played/total: "+str(round_value(numpy.mean(scores['hands_played']['played'])))
print "- won/played: "+str(round_value(numpy.mean(scores['hands_played']['won'])))
print
print "Hands Played 2"
print "- total: "+str(round_value(numpy.mean(scores['hands_played']['total2'])))
print "- played/total: "+str(round_value(numpy.mean(scores['hands_played']['played2'])))
print "- won/played: "+str(round_value(numpy.mean(scores['hands_played']['won2'])))
print
print "Properties"
print "- bluffing_only_raise: "+str(round_value(numpy.mean(scores['properties']['bluffing_only_raise'])))
print "- normalized_result_std: "+str(round_value(numpy.mean(scores['properties']['normalized_result_std'])))
print "- passive_aggressive: "+str(round_value(numpy.mean(scores['properties']['passive_aggressive'])))
print "- agressiveness: "+str(round_value(numpy.mean(scores['properties']['agressiveness'])))
print "- tight_loose: "+str(round_value(numpy.mean(scores['properties']['tight_loose'])))
print "- bluffing: "+str(round_value(numpy.mean(scores['properties']['bluffing'])))
print "- normalized_result_mean: "+str(round_value(numpy.mean(scores['properties']['normalized_result_mean'])))
print

# 'properties': {u'bluffing_only_raise': 0., u'normalized_result_std': 0., u'passive_aggressive': 0.,
# 'agressiveness': 0., u'tight_loose': 0., u'bluffing': 0., u'normalized_result_mean': 0.}

# print str(len(all_teams))
# print str(len(data))
# print str(data[0])

# x = [0.0,0.1,0.2,0.3,0.4,0.5]

# y = [0.0,0.1,0.2,0.3,0.4,0.5]

pl.grid(b=True, which='both', color='0.65',linestyle='-')

if metric_name == 'bluffing_only_raise':
    metric_name = 'aggressive_bluffing'

if metric_name == 'agressiveness':
    metric_name = 'aggressiveness'

pl.xlabel('passive/aggressive')
pl.ylabel('tight/loose')
pl.axis([-0.05, 1.05, -0.05, 1.05])
pl.plot(x, y,'bo',markersize=2.0) #, alpha=0.2)
pl.plot([-0.05, 700], [0.6488, 0.6488], 'k-', lw=2, color='blue', linestyle='--')
pl.plot([0.4641, 0.4641], [-0.05, 700], 'k-', lw=2, color='blue', linestyle='--')

# %- passive_aggressive: 0.4641
# %- tight_loose: 0.6488

# %- passive_aggressive: 0.4565
# %- tight_loose: 0.4969

# pl.xlabel(metric_name)
# pl.ylabel('score')
# pl.axis([0.0, 1.0, 0.2, 0.8])
# pl.plot(x, y,'bo',markersize=2.0) #, alpha=0.2)
# pl.plot([0, 700], [0.5, 0.5], 'k-', lw=2, color='gray') # ,linestyle='--'

# pl.show()
# pl.savefig(metric_name+'_vs_score_for_balanced_points.pdf', bbox_inches='tight')
pl.savefig('behaviors_against_bayesian_opp_for_balanced_points.png', bbox_inches='tight')