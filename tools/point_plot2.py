import pylab as plt
import json
import numpy
import matplotlib.patches as mpatches

def round_value(value, round_decimals_to = 4):
    number = float(10**round_decimals_to)
    return int(value * number) / number

filename = 'properties_per_team__sbb_trained_against_bayesian_vs_bayesian_opponent__1260_balanced_points.json'
filename2 = 'properties_per_team__sbb_trained_against_bayesian_vs_bayesian_opponent__1260_unbalanced_points.json'

with open(filename) as data_file:    
    data = json.load(data_file)
all_teams = []
for value in data.values():
    all_teams += value

with open(filename2) as data_file:    
    data = json.load(data_file)
all_teams2 = []
for value in data.values():
    all_teams2 += value

x = []
y = []

x2 = []
y2 = []

# metric_name = 'wins'
# metric_name = 'played'
# metric_name = 'agressiveness'
metric_name = 'bluffing'
# metric_name = 'bluffing_only_raise'
# metric_name = 'passive_aggressive'
# metric_name = 'tight_loose'

for value in all_teams:

    if metric_name == 'wins':
        if value.values()[0]['hands_played']['overall']['won'] is not None:
            total_wins = value.values()[0]['hands_played']['overall']['played']*value.values()[0]['hands_played']['overall']['won']
        else:
            total_wins = 0.0
        x.append(total_wins)
    elif metric_name == 'played':
        x.append(value.values()[0]['hands_played']['overall']['played'])
    else:
        x.append(value.values()[0]['properties'][metric_name])

    y.append(value.values()[0]['properties']['normalized_result_mean'])

for value in all_teams2:

    if metric_name == 'wins':
        if value.values()[0]['hands_played']['overall']['won'] is not None:
            total_wins = value.values()[0]['hands_played']['overall']['played']*value.values()[0]['hands_played']['overall']['won']
        else:
            total_wins = 0.0
        x2.append(total_wins)
    elif metric_name == 'played':
        x2.append(value.values()[0]['hands_played']['overall']['played'])
    else:
        x2.append(value.values()[0]['properties'][metric_name])

    y2.append(value.values()[0]['properties']['normalized_result_mean'])


plt.grid(b=True, which='both', color='0.65',linestyle='-')

patches = []

if metric_name == 'bluffing_only_raise':
    metric_name = 'aggressive_bluffing'

if metric_name == 'agressiveness':
    metric_name = 'aggressiveness'

if metric_name == 'tight_loose':
    metric_name = 'tight/loose'

plt.xlabel(metric_name)
plt.ylabel('score')

if metric_name == 'tight/loose':
    metric_name = 'tight_loose'

plt.axis([0.0, 1.0, 0.2, 0.8])

# red_dot, = plt.plot(x2, y2,'bo',markersize=3.0) #, alpha=0.2)
# patches.append(mpatches.Patch(color='b', marker='o', label='unbalanced'))

# white_cross, = plt.plot(x, y,'rx',markersize=3.0) #, alpha=0.2)
# patches.append(mpatches.Patch(color='r', marker='x', label='balanced'))

# plt.legend(handles=patches, loc=3)
# plt.legend([red_dot, white_cross], ["unbalanced", "balanced"])

plt.scatter(x2, y2, c='b',marker='o', label='unbalanced')
plt.scatter(x, y, c='r',marker='x', label='balanced')
plt.legend()

temp1 = 0.1345
plt.plot([temp1, temp1], [0, 700], 'k-', lw=2, color='red', linestyle='--')
temp2 = 0.3298
plt.plot([temp2, temp2], [0, 700], 'k-', lw=2, color='blue', linestyle='--')


# %Properties (balanced)
# %- passive_aggressive: 0.4641
# %- agressiveness: 0.4875
# %- tight_loose: 0.6488
# %- bluffing: 0.1345
# %- normalized_result_mean: 0.4854
# %
# %Properties (unbalanced)
# %- passive_aggressive: 0.4565
# %- agressiveness: 0.3957
# %- tight_loose: 0.4969
# %- bluffing: 0.3298
# %- normalized_result_mean: 0.5055


# plt.show()
plt.savefig(metric_name+'_vs_score_for_unbalanced_and_balanced_points.png', bbox_inches='tight')