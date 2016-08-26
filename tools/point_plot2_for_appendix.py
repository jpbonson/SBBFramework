import pylab as plt
import json
import numpy
import matplotlib.patches as mpatches

def round_value(value, round_decimals_to = 4):
    number = float(10**round_decimals_to)
    return int(value * number) / number

# filename = 'properties_per_team__sbb_trained_against_bayesian_vs_bayesian_opponent__1260_balanced_points.json'
# filename2 = 'properties_per_team__sbb_trained_against_bayesian_vs_bayesian_opponent__1260_unbalanced_points.json'

blah = "hamming_and_genotype"
filenames = ['genotype_vs_ncd/'+blah+'/properties_per_team_'+blah+'_with_profiling__unbalanced.json']

# 'genotype_vs_ncd/'+blah+'/properties_per_team_'+blah+'__unbalanced__LA.json',
# 'genotype_vs_ncd/'+blah+'/properties_per_team_'+blah+'__unbalanced__LP.json',
# 'genotype_vs_ncd/'+blah+'/properties_per_team_'+blah+'__unbalanced__TA.json',
# 'genotype_vs_ncd/'+blah+'/properties_per_team_'+blah+'__unbalanced__TP.json']
results_per_type = {}
for filename in filenames:

    with open(filename) as data_file:    
        data = json.load(data_file)
    all_teams = []
    for value in data.values():
        all_teams += value

    x = []
    y = []

    

    results =[]
    for value in all_teams:

        if value.values()[0]['properties']['normalized_result_mean'] > 0.5:
            results.append(value)

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
    results_per_type[filename] = results

# print
# print "Properties"
# print "- metric_name1: "+str(round_value(numpy.mean(x)))
# print "- metric_name2: "+str(round_value(numpy.mean(x2)))
# print
# print "balanced: "+str([round_value(a, 2) for a in x])
# print
# print "unbalanced: "+str([round_value(a, 2) for a in x2])

# print str(balanced_results[0])
# print str(balanced_results[0].keys())

for filename in filenames:
    print "size: "+str(len(results_per_type[filename]))

# print
# partial = list(set([x.keys()[0] for x in results_per_type[filenames[0]]]) & set([x.keys()[0] for x in results_per_type[filenames[1]]]))
# print "size: "+str(len(partial))
# partial = list(set([x for x in partial]) & set([x.keys()[0] for x in results_per_type[filenames[2]]]))
# print "size: "+str(len(partial))
# partial = list(set([x for x in partial]) & set([x.keys()[0] for x in results_per_type[filenames[3]]]))
# print "size: "+str(len(partial))
# partial = list(set([x for x in partial]) & set([x.keys()[0] for x in results_per_type[filenames[4]]]))
# print "size: "+str(len(partial))

# # print str(partial)

# against_bayesian = [x for x in results_per_type[filenames[0]] if x.keys()[0] in partial]
# print
# print "size: "+str(len(against_bayesian))
# print str([x.keys()[0] for x in against_bayesian])

# print
# print "size: "+str(len(set(partial)))
# print "size: "+str(len(set([x.keys()[0] for x in against_bayesian])))

# print "unbalanced_results: "+str([x.keys()[0] for x in results_per_type[filenames[0]]])

against_bayesian = results_per_type[filenames[0]]

# metric_name = 'wins'
# metric_name = 'played'
metric_name = 'agressiveness'
# metric_name = 'bluffing'
# metric_name = 'bluffing_only_raise'
# metric_name = 'passive_aggressive'
# metric_name = 'tight_loose'

results = []
for team in against_bayesian:
    if team.values()[0]['properties'][metric_name] > 0.8 and team.values()[0]['properties']['normalized_result_mean'] > 0.54:
        results.append(team)

metric_name = 'normalized_result_mean'

print str([x.values()[0]['properties'][metric_name] for x in results])
print str(len(results))

# with open("for_appendix_aggressive.json", 'w') as f:
#     for r in results:
#         json.dump(r, f)
#         f.write("\n")