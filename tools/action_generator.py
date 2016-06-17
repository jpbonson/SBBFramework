import json
from glob import glob

root = "config_layer1_without_bayes_seed"
for seed_id in range(1, 6):
    print "# "+str(seed_id)
    for run_id in range(1, 6):
        print str(run_id)
        actions = {}
        cont = 0
        for json_file in glob(root+str(seed_id)+'/run'+str(run_id)+'/last_generation_teams/json/*.json'):
            with open(json_file) as data_file:
                content = json.load(data_file)
                actions[cont] = content
                cont += 1

        with open(root+str(seed_id)+'/run'+str(run_id)+"/second_layer_files/actions_all_teams.json", 'w') as f:
            json.dump(actions, f)