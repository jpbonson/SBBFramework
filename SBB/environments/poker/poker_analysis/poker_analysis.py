import json
import random
import linecache
import numpy
import glob
import os
import re
import ast
import glob
import shutil
import operator
from collections import defaultdict, Counter
from ..poker_environment import PokerEnvironment
from ..poker_match import PokerMatch
from ..poker_point import PokerPoint
from ..poker_config import PokerConfig
from ..poker_opponents import (PokerAlwaysCallOpponent, PokerAlwaysRaiseOpponent, PokerLooseAgressiveOpponent, 
    PokerLoosePassiveOpponent, PokerTightAgressiveOpponent, PokerTightPassiveOpponent, PokerBayesianTesterOpponent, 
    PokerBayesianOpponent)
from ...default_opponent import DefaultOpponent
from ...default_environment import reset_points_ids
from ....utils.team_reader import read_team_from_json, initialize_actions_for_second_layer
from ....utils.helpers import round_value, flatten, accumulative_performances
from ....config import Config

class PokerFranksteinOpponent(DefaultOpponent):

    OPPONENT_ID = "frankstein_opponent"

    def __init__(self, teams, use_weights = False):
        super(PokerFranksteinOpponent, self).__init__(PokerFranksteinOpponent.OPPONENT_ID)
        self.programs = []
        self.extra_metrics_ = {}
        self.results_per_points_for_validation_ = {}
        self.action_sequence_ = {}
        self.last_selected_program_ = None
        self.teams = teams
        self.use_weights = use_weights
        if use_weights:
            scores = []
            for team in teams:
                if team.score_testset_ == 0.0:
                    scores.append(0.000001)
                else:
                    scores.append(team.score_testset_)
            total_scores = sum(scores)
            self.weights = [f/float(total_scores) for f in scores]

    def initialize(self, seed):
        pass

    def execute(self, point_id, inputs, valid_actions, is_training):
        actions = []
        for team in self.teams:
            action = team.execute(point_id, inputs, valid_actions, is_training, force_reset = True)
            actions.append(action)
        if self.use_weights:
            counts = {0: 0.0, 1: 0.0, 2: 0.0}
            for action, weight in zip(actions, self.weights):
                counts[action] += weight
            action = max(counts.iteritems(), key=operator.itemgetter(1))[0]
            return action
        else:
            counter = Counter(actions)
            action = counter.most_common(1)[0][0]
            return action

    def reset_registers(self):
        for team in self.teams:
            team.reset_registers()

    def get_behaviors_metrics(self):
        result = {}
        result['agressiveness'] = self.extra_metrics_['agressiveness']
        result['tight_loose'] = self.extra_metrics_['tight_loose']
        result['passive_aggressive'] = self.extra_metrics_['passive_aggressive']
        result['bluffing'] = self.extra_metrics_['bluffing']
        result['normalized_result_mean'] = numpy.mean(self.results_per_points_for_validation_.values())
        result['normalized_result_std'] = numpy.std(self.results_per_points_for_validation_.values())
        return result

    def metrics(self, full_version = False):
        print "Metrics for Played Hands:"
        print "- total_hands: "+str(float(self.extra_metrics_['total_hands']['validation']))
        print "- hand_played: "+str(self.extra_metrics_['hand_played']['validation'])
        print "- won_hands: "+str(self.extra_metrics_['won_hands']['validation'])
        print "- hand_played/total_hands: "+str(self.extra_metrics_['hand_played']['validation']/float(self.extra_metrics_['total_hands']['validation']))
        print "- won_hands/total_hands: "+str(self.extra_metrics_['won_hands']['validation']/float(self.extra_metrics_['total_hands']['validation']))
        print "- won_hands/hand_played: "+str(self.extra_metrics_['won_hands']['validation']/float(self.extra_metrics_['hand_played']['validation']))
        return ""

class PokerSBBBayesianOpponent(DefaultOpponent):

    OPPONENT_ID = "sbb_bayesian_opponent"

    def __init__(self, anti_tp_teams, anti_ta_teams, anti_lp_teams, anti_la_teams):
        super(PokerSBBBayesianOpponent, self).__init__(PokerSBBBayesianOpponent.OPPONENT_ID)
        action_prob_from_tests_with_4bets = {
            'la': {
                'f': 0.053,                'c': 0.43,                'r': 0.517,
            },
            'lp': {
                'f': 0.047,                'c': 0.728,                'r': 0.225,
            },
            'ta': {
                'f': 0.373,                'c': 0.357,                'r': 0.270,
            },
            'tp': {
                'f': 0.355,                'c': 0.559,                'r': 0.086,
            }
        }
        self.action_prob = action_prob_from_tests_with_4bets
        self.antiplayers = {
            'tp': anti_tp_teams,
            'ta': anti_ta_teams,
            'lp': anti_lp_teams,
            'la': anti_la_teams,
        }
        self.programs = []
        self.extra_metrics_ = {}
        self.results_per_points_for_validation_ = {}
        self.action_sequence_ = {}
        self.last_selected_program_ = None
        self.opponent_past_actions_history = []
        self.initial_prob = {
            'tp': 0.25,
            'ta': 0.25,
            'lp': 0.25,
            'la': 0.25,
        }

    def initialize(self, seed):
        pass

    def update_opponent_actions(self, opponent_actions):
        self.opponent_past_actions_history += opponent_actions
        for opp_action in opponent_actions:
            temp = {}
            for key in self.initial_prob.keys():
                temp[key] = self.action_prob[key][opp_action] * self.initial_prob[key]

            normalization_param = sum(temp.values())
            for key in self.initial_prob.keys():
                temp[key] /= normalization_param
                self.initial_prob[key] = temp[key]

    def execute(self, point_id, inputs, valid_actions, is_training):
        play_style = max(self.initial_prob.iterkeys(), key=(lambda key: self.initial_prob[key]))
        actions = []
        for team in self.antiplayers[play_style]:
            action = team.execute(point_id, inputs, valid_actions, is_training, force_reset = True)
            actions.append(action)
        counter = Counter(actions)
        action = counter.most_common(1)[0][0]
        return action

    def reset_registers(self):
        for team in self.antiplayers['tp']:
            team.reset_registers()
        for team in self.antiplayers['ta']:
            team.reset_registers()
        for team in self.antiplayers['lp']:
            team.reset_registers()
        for team in self.antiplayers['la']:
            team.reset_registers()

    def get_behaviors_metrics(self):
        result = {}
        result['agressiveness'] = self.extra_metrics_['agressiveness']
        result['tight_loose'] = self.extra_metrics_['tight_loose']
        result['passive_aggressive'] = self.extra_metrics_['passive_aggressive']
        result['bluffing'] = self.extra_metrics_['bluffing']
        result['normalized_result_mean'] = numpy.mean(self.results_per_points_for_validation_.values())
        result['normalized_result_std'] = numpy.std(self.results_per_points_for_validation_.values())
        return result

    def metrics(self, full_version = False):
        print "Metrics for Played Hands:"
        print "- total_hands: "+str(float(self.extra_metrics_['total_hands']['validation']))
        print "- hand_played: "+str(self.extra_metrics_['hand_played']['validation'])
        print "- won_hands: "+str(self.extra_metrics_['won_hands']['validation'])
        print "- hand_played/total_hands: "+str(self.extra_metrics_['hand_played']['validation']/float(self.extra_metrics_['total_hands']['validation']))
        print "- won_hands/total_hands: "+str(self.extra_metrics_['won_hands']['validation']/float(self.extra_metrics_['total_hands']['validation']))
        print "- won_hands/hand_played: "+str(self.extra_metrics_['won_hands']['validation']/float(self.extra_metrics_['hand_played']['validation']))
        return ""

class PokerAnalysis():

    def __init__(self):
        pass

    def run_folder_for_text_analysis(self, folder_path, debug_folder):
        inputs_per_team = []
        cont = 0
        for folder in glob.glob(folder_path+"*"):
            print "Executing folder "+str(folder)+"..."
            for subfolder in glob.glob(folder+"/run*"):
                print "Executing subfolder "+str(subfolder)+"..."
                teams_population = []
                run_seed_id = subfolder.split("/")[-2]+"_"+subfolder.split("/")[-1]
                for filename in glob.glob(subfolder+"/last_generation_teams/*.txt"):
                    print str(filename)
                    with open(filename) as f:
                # with open(subfolder+"/best_team.txt") as f:
                        content = f.readlines()
                        content = '\n'.join(content)
                        match = re.search(r'inputs distribution: Counter\((.*)\)\n', content)
                        try:
                            new_dict = ast.literal_eval(match.group(1))
                            inputs_per_team.append(new_dict)
                        except:
                            print str(match.group(1))
                            cont += 1
        for x in inputs_per_team:
            to_remove = []
            for key, value in x.iteritems():
                if value < 2:
                    to_remove.append(key)
            for y in to_remove:
                x.pop(y)

        sizes = [len(x) for x in inputs_per_team]
        print str(numpy.mean(sizes))
        print str(numpy.std(sizes))
        print "cont: "+str(cont)

    def run_folder_for_voting(self, folder_path, subfolder_path, matches, balanced, player2_file_or_opponent_type, 
            player2_is_sbb, generate_debug_files_per_match, debug_folder, output_file_name, rank_on_the_run, rank_size, 
            create_player_using_all_runs, use_weights, seed = None):
        second_layer_enabled = False
        self._setup_config(second_layer_enabled, generate_debug_files_per_match, False, seed)
        environment, points = self._setup_environment(balanced, matches)

        if rank_on_the_run or use_weights:
            environment_temp, points_temp = self._setup_environment(balanced, matches/2)

        player1_is_sbb = True

        print "Loading player 2..."
        if player2_is_sbb and not player2_file_or_opponent_type == PokerBayesianTesterOpponent and not player2_file_or_opponent_type == PokerBayesianOpponent:
            player2 = self._create_player("sbb", balanced, second_layer_enabled, None, json_path=player2_file_or_opponent_type)
            self._setup_attributes(player2)
        else:
            if player2_file_or_opponent_type == PokerBayesianTesterOpponent or player2_file_or_opponent_type == PokerBayesianOpponent:
                player2 = self._create_player("static", balanced, second_layer_enabled, None, json_path=None, classname=player2_file_or_opponent_type, test_bayesian_alfa=None, test_bayesian_beta=None)
                self._setup_attributes(player2)
            else:
                player2 = self._create_player("static", balanced, second_layer_enabled, None, classname=player2_file_or_opponent_type)
        print "...finished loading player 2."

        scores = []
        properties_per_team = defaultdict(list)
        teams_together = []
        for folder in glob.glob(folder_path+"*"):
            print "Executing folder "+str(folder)+"..."
            for subfolder in glob.glob(folder+"/*/"):
                print "Executing subfolder "+str(subfolder)+"..."
                teams_population = []
                with open(subfolder+subfolder_path) as data_file:
                    data = json.load(data_file)
                for index, team_json in data.iteritems():
                    team = read_team_from_json(team_json)
                    self._setup_attributes(team)
                    if rank_on_the_run or use_weights:
                        self._execute_matches(team, player2, player1_is_sbb, player2_is_sbb, points_temp, environment_temp)
                    teams_population.append(team)

                if rank_on_the_run:
                    teams_population.sort(key=lambda x: x.score_testset_, reverse=True)
                    teams_population = teams_population[:rank_size]

                if create_player_using_all_runs:
                    teams_together += teams_population
                else:
                    voting_team = PokerFranksteinOpponent(teams_population, use_weights)
                    self._setup_attributes(voting_team)
                    self._execute_matches(voting_team, player2, player1_is_sbb, player2_is_sbb, points, environment)
                    scores.append(voting_team.score_testset_)
                    properties_per_team[subfolder].append(
                        {'voting_team': {
                            'properties': voting_team.get_behaviors_metrics(),
                            'points': voting_team.extra_metrics_['points'],
                            'hands_played': self._hand_player_metrics(voting_team),
                            }}
                        )

        if create_player_using_all_runs:
            voting_team = PokerFranksteinOpponent(teams_together)
            self._setup_attributes(voting_team)
            self._execute_matches(voting_team, player2, player1_is_sbb, player2_is_sbb, points, environment)
            scores.append(voting_team.score_testset_)
            properties_per_team[subfolder].append(
                {'voting_team': {
                    'properties': voting_team.get_behaviors_metrics(),
                    'points': voting_team.extra_metrics_['points'],
                    'hands_played': self._hand_player_metrics(voting_team),
                    }}
                )

        with open(debug_folder+"voting_properties_per_team_"+output_file_name+".json", 'w') as f:
            json.dump(properties_per_team, f)
        print
        print output_file_name
        print "scores mean: "+str(numpy.mean(scores))
        print "scores std: "+str(numpy.std(scores))

    def run_folder_for_acc_curve_for_all_statics(self, folder_path, matches, balanced, 
            generate_debug_files_per_match, debug_folder, output_file_name, river_round_only, 
            seed = None):
        second_layer_enabled = False
        self._setup_config(second_layer_enabled, generate_debug_files_per_match, river_round_only, seed)
        environment_la, points_la = self._setup_environment(balanced, matches)
        environment_lp, points_lp = self._setup_environment(balanced, matches)
        environment_ta, points_ta = self._setup_environment(balanced, matches)
        environment_tp, points_tp = self._setup_environment(balanced, matches)

        player1_is_sbb = True

        print "Loading player 2..."
        player2_la = self._create_player("static", balanced, second_layer_enabled, None, classname=PokerLooseAgressiveOpponent)
        player2_lp = self._create_player("static", balanced, second_layer_enabled, None, classname=PokerLoosePassiveOpponent)
        player2_ta = self._create_player("static", balanced, second_layer_enabled, None, classname=PokerTightAgressiveOpponent)
        player2_tp = self._create_player("static", balanced, second_layer_enabled, None, classname=PokerTightPassiveOpponent)
        print "...finished loading player 2."

        individual_performances_summary = []
        accumulative_performances_summary = []
        properties_per_team = defaultdict(list)
        for folder in glob.glob(folder_path+"*"):
            print "Executing folder "+str(folder)+"..."
            for subfolder in glob.glob(folder+"/*"):
                print "Executing subfolder "+str(subfolder)+"..."
                teams_population = []
                run_seed_id = subfolder.split("/")[-2]+"_"+subfolder.split("/")[-1]
                for filename in glob.glob(subfolder+"/last_generation_teams/json/*"):
                    if "actions.json" not in filename:
                        player1 = self._create_player("sbb", balanced, second_layer_enabled, None, json_path=filename)
                        self._setup_attributes(player1)
                        self._evaluate_teams_for_all_statics(player1, environment_la, points_la, player2_la, 
                            environment_lp, points_lp, player2_lp, environment_ta, points_ta, player2_ta, 
                            environment_tp, points_tp, player2_tp)
                        self._setup_final_attributes(player1)
                        teams_population.append(player1)
                        properties_per_team[run_seed_id].append(
                            {player1.team_id_: {
                                'properties': player1.get_behaviors_metrics(),
                                'points': player1.extra_metrics_['points'],
                                'hands_played': self._hand_player_metrics(player1),
                                }}
                            )
              
                if len(teams_population) > 0:
                    sorting_criteria = lambda x: x.score_testset_
                    get_results_per_points = lambda x: x.results_per_points_for_validation_
                    point_ids = ([point.point_id_ for point in points_la] + [point.point_id_ for point in points_lp] +
                        [point.point_id_ for point in points_ta] + [point.point_id_ for point in points_tp])
                    r = accumulative_performances(teams_population, point_ids, sorting_criteria, get_results_per_points)
                    individual_performance, accumulative_performance, teams_ids = r
                    individual_performances_summary.append(individual_performance)
                    accumulative_performances_summary.append(accumulative_performance)
        msg = ""
        msg += "individual_values = "+str(individual_performances_summary)
        msg += "\nacc_values = "+str(accumulative_performances_summary)
        print msg
        with open(debug_folder+"acc_curves_summary_"+output_file_name+".log", 'w') as f:
            f.write(msg)
        with open(debug_folder+"properties_per_team_"+output_file_name+".json", 'w') as f:
            json.dump(properties_per_team, f)
        print "\ntotal points: "+str(len(point_ids))

    def _evaluate_teams_for_all_statics(self, player1, environment_la, points_la, player2_la, 
        environment_lp, points_lp, player2_lp, environment_ta, points_ta, player2_ta, 
        environment_tp, points_tp, player2_tp):
        environments = [environment_la, environment_lp, environment_ta, environment_tp]
        points = [points_la, points_lp, points_ta, points_tp]
        players2 = [player2_la, player2_lp, player2_ta, player2_tp]
        results = []
        team = player1
        extra_metrics_opponents = defaultdict(list)
        match_id = 0
        for index in range(0, 4):
            extra_metrics_points = environments[index]._initialize_extra_metrics_for_points()
            for point in points[index]:
                # opponent team
                match_id += 1
                result = environments[index]._play_match(team, players2[index], point, Config.RESTRICTIONS['mode']['validation'], match_id)
                team.reset_registers()
                extra_metrics_opponents['player2_'+str(index)].append(result)
                extra_metrics_points = environments[index]._update_extra_metrics_for_points(extra_metrics_points, point, result)
                team.results_per_points_for_validation_[point.point_id_] = result
                results.append(result)
        for key in extra_metrics_opponents:
            extra_metrics_opponents[key] = round_value(numpy.mean(extra_metrics_opponents[key]))
        team.extra_metrics_['opponents'] = extra_metrics_opponents
        for key in extra_metrics_points:
            for subkey in extra_metrics_points[key]:
                extra_metrics_points[key][subkey] = round_value(numpy.mean(extra_metrics_points[key][subkey]))
        team.extra_metrics_['points'] = extra_metrics_points
        team.score_testset_ = numpy.mean(results)

    def run_folder_for_acc_curve(self, folder_path, matches, balanced, player2_file_or_opponent_type, 
            player2_is_sbb, generate_debug_files_per_match, debug_folder, output_file_name, river_round_only, 
            second_layer_enabled, second_layer_action_folder, sort_by_points = True, seed = None):
        self._setup_config(second_layer_enabled, generate_debug_files_per_match, river_round_only, seed)
        environment, points = self._setup_environment(balanced, matches)

        player1_is_sbb = True

        print "Loading player 2..."
        if player2_is_sbb and not player2_file_or_opponent_type == PokerBayesianTesterOpponent and not player2_file_or_opponent_type == PokerBayesianOpponent:
            player2 = self._create_player("sbb", balanced, second_layer_enabled, None, json_path=player2_file_or_opponent_type)
            self._setup_attributes(player2)
        else:
            if player2_file_or_opponent_type == PokerBayesianTesterOpponent or player2_file_or_opponent_type == PokerBayesianOpponent:
                player2 = self._create_player("static", balanced, second_layer_enabled, None, json_path=None, classname=player2_file_or_opponent_type, test_bayesian_alfa=None, test_bayesian_beta=None)
                self._setup_attributes(player2)
            else:
                player2 = self._create_player("static", balanced, second_layer_enabled, None, classname=player2_file_or_opponent_type)
        print "...finished loading player 2."

        cont_folders = 0
        individual_performances_summary = []
        accumulative_performances_summary = []
        properties_per_team = defaultdict(list)
        for folder in glob.glob(folder_path+"*"):
            print "Executing folder "+str(folder)+"..."
            for subfolder in glob.glob(folder+"/*"):
                print "Executing subfolder "+str(subfolder)+"..."
                cont_folders += 1
                teams_population = []
                run_seed_id = subfolder.split("/")[-2]+"_"+subfolder.split("/")[-1]
                for filename in glob.glob(subfolder+"/last_generation_teams/json/*"):
                    if "actions.json" not in filename:
                        second_layer_action_folder_per_run = None
                        if second_layer_enabled:
                            run_id = subfolder.split("\\")[-1]
                            run_id = run_id.split("/")[-1]
                            seed_id = folder.split("\\")[-1]
                            seed_id = seed_id.split("/")[-1]
                            seed_id = seed_id.split("_")[-1]
                            second_layer_action_folder_per_run = str(second_layer_action_folder).replace("[run_id]", run_id)
                            second_layer_action_folder_per_run = str(second_layer_action_folder_per_run).replace("[seed_id]", seed_id)
                        player1 = self._create_player("sbb", balanced, second_layer_enabled, second_layer_action_folder_per_run, json_path=filename)
                        self._setup_attributes(player1)
                        self._execute_matches(player1, player2, player1_is_sbb, player2_is_sbb, points, environment)
                        teams_population.append(player1)
                        properties_per_team[run_seed_id].append(
                            {player1.team_id_: {
                                'properties': player1.get_behaviors_metrics(),
                                'points': player1.extra_metrics_['points'],
                                'hands_played': self._hand_player_metrics(player1),
                                }}
                            )
              
                if len(teams_population) > 0:
                    if sort_by_points:
                        sorting_criteria = lambda x: x.score_testset_
                        get_results_per_points = lambda x: x.results_per_points_for_validation_
                    else:
                        sorting_criteria = lambda x: numpy.mean(x.extra_metrics_['hands_won_or_lost_per_point'].values())
                        get_results_per_points = lambda x: x.extra_metrics_['hands_won_or_lost_per_point']
                    point_ids = [point.point_id_ for point in points]
                    r = accumulative_performances(teams_population, point_ids, sorting_criteria, get_results_per_points)
                    individual_performance, accumulative_performance, teams_ids = r
                    individual_performances_summary.append(individual_performance)
                    accumulative_performances_summary.append(accumulative_performance)

                    msg = ""
                    msg += "\n\nindividual_values = "+str(individual_performance)
                    msg += "\n\nacc_values = "+str(accumulative_performance)
                    msg += "\n\nteams_ids = "+str(teams_ids)
                    # print msg
                    # with open(debug_folder+"acc_curves.log", 'w') as f:
                    #     f.write(msg)
        msg = ""
        msg += "best_individual_values = "+str([x[0] for x in individual_performances_summary])
        msg += "\nbest_acc_values = "+str([x[-1] for x in accumulative_performances_summary])
        msg += "\n"
        msg += "\nindividual_values = "+str(individual_performances_summary)
        msg += "\nacc_values = "+str(accumulative_performances_summary)
        print msg
        with open(debug_folder+"acc_curves_summary_"+output_file_name+".log", 'w') as f:
            f.write(msg)
        with open(debug_folder+"properties_per_team_"+output_file_name+".json", 'w') as f:
            json.dump(properties_per_team, f)
        print "\ntotal points: "+str(len(points))
        print "\ntotal folders: "+str(cont_folders)

    def _hand_player_metrics(self, team):
        mode = 'validation'
        msg = {}
        a = round_value(team.extra_metrics_['hand_played'][mode]/float(team.extra_metrics_['total_hands'][mode]))
        b = None
        if team.extra_metrics_['hand_played'][mode] > 0:
            b = round_value(team.extra_metrics_['won_hands'][mode]/float(team.extra_metrics_['hand_played'][mode]))
        msg['overall'] = {}
        msg['overall']['total'] = team.extra_metrics_['total_hands'][mode]
        msg['overall']['played'] = a
        msg['overall']['won'] = b
        for metric in team.extra_metrics_['total_hands_per_point_type'][mode]:
            msg[metric] = {}
            for key in team.extra_metrics_['total_hands_per_point_type'][mode][metric]:
                msg[metric][key] = {}
                a = team.extra_metrics_['total_hands_per_point_type'][mode][metric][key]
                b = None
                c = None
                if a > 0:
                    b = round_value(team.extra_metrics_['hand_played_per_point_type'][mode][metric][key]/float(team.extra_metrics_['total_hands_per_point_type'][mode][metric][key]))
                    if team.extra_metrics_['hand_played_per_point_type'][mode][metric][key] > 0:
                        c = round_value(team.extra_metrics_['won_hands_per_point_type'][mode][metric][key]/float(team.extra_metrics_['hand_played_per_point_type'][mode][metric][key]))
                msg[metric][key]['total'] = a
                msg[metric][key]['played'] = b
                msg[metric][key]['won'] = c
        return msg

    def run_for_all_opponents(self, matches, balanced, team_file, generate_debug_files_per_match, debug_folder, 
            river_round_only, second_layer_enabled, seed = None):
        opponents = [PokerLooseAgressiveOpponent, PokerLoosePassiveOpponent, PokerTightAgressiveOpponent, PokerTightPassiveOpponent]
        results = []
        for opponent in opponents:
            result = self.run(matches, balanced, team_file, opponent, True,
                False, generate_debug_files_per_match, debug_folder, river_round_only, second_layer_enabled, seed)
            results.append(result)
        player1 = self._create_player("sbb", balanced, second_layer_enabled, json_path=team_file)
        print "\n\nPLAYER: "+str(player1.__repr__())
        m = ""
        for o, r in zip(opponents, results):
            m += "\n###### "+o.OPPONENT_ID+"\n"
            for key, value in r.iteritems():
                m += key+": "+str(value)+"\n"
        print m
        with open(debug_folder+str(player1.OPPONENT_ID)+"/team_summary_overall.log", 'w') as f:
            f.write(m)

    def run(self, matches, balanced, player1_file_or_opponent_type, player2_file_or_opponent_type, 
            player1_is_sbb, player2_is_sbb, generate_debug_files_per_match, debug_folder, river_round_only, 
            second_layer_enabled, second_layer_action_folder, seed = None, test_bayesian_alfa = None, test_bayesian_beta = None):
        print "Starting poker analysis tool"

        self._setup_config(second_layer_enabled, generate_debug_files_per_match, river_round_only, seed)
        environment, points = self._setup_environment(balanced, matches)
        player1, player2 = self._setup_players(player1_is_sbb, player1_file_or_opponent_type, player2_is_sbb, 
            player2_file_or_opponent_type, balanced, second_layer_enabled, second_layer_action_folder, test_bayesian_alfa, test_bayesian_beta, debug_folder)
        
        if not player1_is_sbb:
            player1.initialize(seed)
            player1.extra_metrics_ = {}
            player1.action_sequence_ = {}
            player1.results_per_points_for_validation_ = {}
            self._setup_attributes(player1)
        self._execute_matches(player1, player2, player1_is_sbb, player2_is_sbb, points, environment)
        
        # WARNING: The stats are only support one sbb player
        metrics_player = player1
        # sum1 = sum([int(r['score'][0]) for r in messages if r['players'][0] == 'sbb'])
        # sum2 = sum([int(r['score'][1]) for r in messages if r['players'][1] == 'sbb'])
        if player1_is_sbb:
            final_message = "\nResult (team stats): "+str(metrics_player.metrics(full_version=True))
        else:
            final_message = "\nResult (normalized): "+str(metrics_player.score_testset_)+" ("+str(metrics_player.score_testset_*1260.0)+" points out of 1260)"
        # final_message += "\n--- Results for matches:"
        # final_message += "\nResult (total chips): "+str(sum1+sum2)+" out of [-"+str(self._maximum_winning()*matches)+",+"+str(self._maximum_winning()*matches)+"]"
        # final_message += "\nResult (normalized): "+str(metrics_player.score_testset_)

        print "won / played / total: "+str(metrics_player.extra_metrics_['won_hands']['validation'])+" / "+str(metrics_player.extra_metrics_['hand_played']['validation'])+" / "+str(metrics_player.extra_metrics_['total_hands']['validation'])

        print final_message
        # with open(Config.USER['reinforcement_parameters']['debug']['output_path']+"team_summary.log", 'w') as f:
        #     f.write(final_message)
        if player1_is_sbb:
            result = metrics_player.get_behaviors_metrics()
            # result['total_chips'] = sum1+sum2
            print "\nProperties:"
            for key, value in result.iteritems():
                print "- "+str(key)+": "+str(value)
        # return metrics_player.score_testset_

    def _setup_config(self, second_layer_enabled, generate_debug_files_per_match, river_round_only, seed):
        print "Setup the configuration..."
        # WARNING: Config.RESTRICTIONS should be exactly the same as the one used to train these teams
        Config.USER['task'] = 'reinforcement'
        Config.USER['reinforcement_parameters']['environment'] = 'poker'
        # Config.USER['advanced_training_parameters']['extra_registers'] = 4
        Config.USER['advanced_training_parameters']['second_layer']['enabled'] = second_layer_enabled
        Config.USER['reinforcement_parameters']['debug']['matches'] = generate_debug_files_per_match
        Config.USER['reinforcement_parameters']['debug']['print'] = False
        Config.USER['reinforcement_parameters']['poker']['river_round_only'] = river_round_only
        Config.USER['reinforcement_parameters']['poker']['river_only_to_fullgame'] = False
        Config.RESTRICTIONS['genotype_options']['total_registers'] = Config.RESTRICTIONS['genotype_options']['output_registers'] + Config.USER['advanced_training_parameters']['extra_registers']
        if seed is None:
            seed = random.randint(0, Config.RESTRICTIONS['max_seed'])
        random.seed(seed)
        numpy.random.seed(seed)
        print "...seed = "+str(seed)
        print "...finished setup the configuration."

    def _setup_environment(self, balanced, matches):
        print "Initializing the environment..."
        environment = PokerEnvironment()
        reset_points_ids()
        if balanced:
            if matches < 9:
                print "Error! For balanced points, the minimum number of matches is 9!"
                raise SystemExit
            points = environment._initialize_random_population_of_points(matches, ignore_cache = True)
        else:
            points = self._create_unbalanced_points(matches)
        for point in points:
            point.teams_results_ = []
        print "...created "+str(len(points))+" points."
        if len(points) == 0:
            print "Error! Zero points created!"
            raise SystemExit
        print "...initialized the environment."
        return environment, points

    def _setup_players(self, player1_is_sbb, player1_file_or_opponent_type, player2_is_sbb, 
            player2_file_or_opponent_type, balanced, second_layer_enabled, second_layer_action_folder, 
            test_bayesian_alfa, test_bayesian_beta, debug_folder):
        print "Loading players..."

        if player1_is_sbb and not player1_file_or_opponent_type == PokerBayesianTesterOpponent and not player1_file_or_opponent_type == PokerBayesianOpponent:
            player1 = self._create_player("sbb", balanced, second_layer_enabled, second_layer_action_folder, json_path=player1_file_or_opponent_type)
            self._setup_attributes(player1)
        else:
            if player1_file_or_opponent_type == PokerBayesianTesterOpponent or player1_file_or_opponent_type == PokerBayesianOpponent:
                player1 = self._create_player("static", balanced, second_layer_enabled, second_layer_action_folder, json_path=None, classname=player1_file_or_opponent_type, test_bayesian_alfa=test_bayesian_alfa, test_bayesian_beta=test_bayesian_beta)
                self._setup_attributes(player1)
            else:
                player1 = self._create_player("static", balanced, second_layer_enabled, second_layer_action_folder, classname=player1_file_or_opponent_type)

        if player2_is_sbb and not player2_file_or_opponent_type == PokerBayesianTesterOpponent and not player2_file_or_opponent_type == PokerBayesianOpponent:
            player2 = self._create_player("sbb", balanced, second_layer_enabled, second_layer_action_folder, json_path=player2_file_or_opponent_type)
            self._setup_attributes(player2)
        else:
            if player2_file_or_opponent_type == PokerBayesianTesterOpponent or player2_file_or_opponent_type == PokerBayesianOpponent:
                player2 = self._create_player("static", balanced, second_layer_enabled, second_layer_action_folder, json_path=None, classname=player2_file_or_opponent_type, test_bayesian_alfa=test_bayesian_alfa, test_bayesian_beta=test_bayesian_beta)
                self._setup_attributes(player2)
            else:
                player2 = self._create_player("static", balanced, second_layer_enabled, second_layer_action_folder, classname=player2_file_or_opponent_type)
        
        Config.USER['reinforcement_parameters']['debug']['output_path'] = debug_folder+str(player1.OPPONENT_ID)+"/"+str(player2.OPPONENT_ID)+"/"
        if not os.path.exists(Config.USER['reinforcement_parameters']['debug']['output_path']):
            os.makedirs(Config.USER['reinforcement_parameters']['debug']['output_path'])
        print "...finished loading players."
        return player1, player2

    def _execute_matches(self, player1, player2, player1_is_sbb, player2_is_sbb, points, environment):
        print "Executing matches..."
        self._evaluate_teams(player1, player2, player1_is_sbb, player2_is_sbb, points, environment)
        if player1_is_sbb:
            self._setup_final_attributes(player1)
        if player2_is_sbb:
            self._setup_final_attributes(player2)
        print "...finished executing matches."
        print

    def _maximum_winning(self):
        max_raises_overall = Config.USER['reinforcement_parameters']['poker']['maximum_bets']
        max_small_bet_turn_winning = PokerConfig.CONFIG['small_bet']*max_raises_overall
        if Config.USER['reinforcement_parameters']['poker']['river_round_only']:  
            return max_small_bet_turn_winning
        else:
            max_big_bet_turn_winning = PokerConfig.CONFIG['big_bet']*max_raises_overall
            return max_small_bet_turn_winning*2 + max_big_bet_turn_winning*2

    def _create_unbalanced_points(self, total_points):
        num_lines_per_file = sum([1 for line in open("SBB/environments/poker/hand_generator/poker_hands/hands_type_all.json")])
        idxs = random.sample(range(1, num_lines_per_file+1), total_points)
        result = [linecache.getline("SBB/environments/poker/hand_generator/poker_hands/hands_type_all.json", i) for i in idxs]
        data = [PokerPoint(0, json.loads(r)) for r in result]
        mapping = {'00': 0, '01': 1, '02': 2, '10': 3, '11': 4, '12': 5, '20': 6, '21': 7, '22': 8}
        for point in data:
            label0_player = PokerConfig.get_hand_strength_label(point.players['team']['hand_strength'][3])
            label0_opp = PokerConfig.get_hand_strength_label(point.players['opponent']['hand_strength'][3])
            label0 = str(label0_player)+str(label0_opp)
            point.label_ = mapping[label0]
        return data

    def _create_player(self, player_type, balanced, second_layer_enabled, second_layer_action_folder,
            json_path=None, classname=None, test_bayesian_alfa=None, test_bayesian_beta=None):
        """
        Create a player.
        - sbb player: read a .json file with the team structure
        - static player: select one of the classes available in poker_opponents.py
        - human player: [TODO]
        """
        if player_type == "sbb":
            print "Loading 'sbb' player"
            if json_path is None:
                print "Error: 'json_path' is None"
            with open(json_path) as data_file:    
                data = json.load(data_file)
            player = read_team_from_json(data)

            player.generation = 0 # gambiarra/workaround
            for program in player.programs:
                program.generation = 0 # gambiarra/workaround

            print "...loaded 'sbb' player: "+str(player.__repr__())
            if second_layer_enabled:
                player.generation = 0 # workaround for second layer
                for program in player.programs:
                    program.generation = 0 # workaround for second layer

                if os.path.isfile(second_layer_action_folder):
                    initialize_actions_for_second_layer(second_layer_action_folder)
                    print "...loaded actions"
                else:
                    raise ValueError("Enabled second layer, but no actions.json file found!")
            return player
        elif player_type == "static":
            print "Loading 'static' player"
            if classname is None:
                print "Error: 'classname' is None"
            if classname == PokerBayesianTesterOpponent:
                player = classname(test_bayesian_alfa, test_bayesian_beta)
            elif classname == PokerBayesianOpponent:
                player = classname(balanced)
            else:
                player = classname()
            print "...loaded 'static' player: "+str(player.__repr__())
            return player
        elif player_type == "human":
            print "player_type = human still to be developed!"
        print "Error: No 'player_type' = "+str(player_type)+" implemented."
        raise SystemExit

    def _setup_attributes(self, team):
        team.extra_metrics_.pop('validation_score', None)
        team.extra_metrics_.pop('validation_opponents', None)
        team.extra_metrics_.pop('validation_points', None)
        team.opponent_model = {}
        team.chips = {} # Chips (the stacks are infinite, but it may be useful to play more conservative if it is losing a lot)

        team.action_sequence_['coding2'] = []
        team.action_sequence_['coding3'] = []
        team.action_sequence_['coding4'] = []

        keys = ['validation']
        subkeys = ['position', 'sbb_label', 'sbb_sd']
        metrics_with_counts = ['total_hands', 'hand_played', 'won_hands']
        metrics_with_dicts = ['total_hands_per_point_type', 'hand_played_per_point_type', 'won_hands_per_point_type']
        for metric in (metrics_with_counts + metrics_with_dicts):
            team.extra_metrics_[metric] = {}
        team.extra_metrics_['hands_played_or_not_per_point'] = {}
        team.extra_metrics_['hands_won_or_lost_per_point'] = {}
        for key in keys:
            for metric in metrics_with_counts:
                team.extra_metrics_[metric][key] = 0
            for metric in metrics_with_dicts:
                team.extra_metrics_[metric][key] = {}
                for subkey in subkeys:
                    team.extra_metrics_[metric][key][subkey] = defaultdict(int)

    def _evaluate_teams(self, player1, player2, player1_is_sbb, player2_is_sbb, points, environment):
        results = []
        team = player1
        extra_metrics_opponents = defaultdict(list)
        extra_metrics_points = environment._initialize_extra_metrics_for_points()
        match_id = 0
        for point in points:
            # opponent team
            match_id += 1
            result = environment._play_match(team, player2, point, Config.RESTRICTIONS['mode']['validation'], match_id)
            if player1_is_sbb:
                team.reset_registers()
            if player2_is_sbb:
                player2.reset_registers()
            extra_metrics_opponents['player2'].append(result)
            extra_metrics_points = environment._update_extra_metrics_for_points(extra_metrics_points, point, result)
            team.results_per_points_for_validation_[point.point_id_] = result
            results.append(result)
        for key in extra_metrics_opponents:
            extra_metrics_opponents[key] = round_value(numpy.mean(extra_metrics_opponents[key]))
        team.extra_metrics_['opponents'] = extra_metrics_opponents
        for key in extra_metrics_points:
            for subkey in extra_metrics_points[key]:
                extra_metrics_points[key][subkey] = round_value(numpy.mean(extra_metrics_points[key][subkey]))
        team.extra_metrics_['points'] = extra_metrics_points
        team.score_testset_ = numpy.mean(results)

    def _setup_final_attributes(self, team):
        self_long_term_agressiveness = []
        self_tight_loose = []
        self_passive_aggressive = []
        self_bluffing = []
        self_bluffing_only_raise = []
        for key, item in team.opponent_model.iteritems():
            self_long_term_agressiveness += item.self_agressiveness
            self_tight_loose += item.self_tight_loose
            self_passive_aggressive += item.self_passive_aggressive
            self_bluffing += item.self_bluffing
            self_bluffing_only_raise += item.self_bluffing_only_raise
        agressiveness = 0.5
        tight_loose = 0.5
        passive_aggressive = 0.5
        bluffing = 0.0
        bluffing_only_raise = 0.0
        if len(self_long_term_agressiveness) > 0:
            agressiveness = numpy.mean(self_long_term_agressiveness)
        if len(self_tight_loose) > 0:
            tight_loose = numpy.mean(self_tight_loose)
        if len(self_passive_aggressive) > 0:
            passive_aggressive = numpy.mean(self_passive_aggressive)
        if len(self_bluffing) > 0:
            bluffing = numpy.mean(self_bluffing)
        if len(self_bluffing_only_raise) > 0:
            bluffing_only_raise = numpy.mean(self_bluffing_only_raise)

        team.extra_metrics_['agressiveness'] = agressiveness
        team.extra_metrics_['tight_loose'] = tight_loose
        team.extra_metrics_['passive_aggressive'] = passive_aggressive
        team.extra_metrics_['bluffing'] = bluffing
        team.extra_metrics_['bluffing_only_raise'] = bluffing_only_raise

        team.opponent_model = {}
        team.chips = {}