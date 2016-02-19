import json
import random
import linecache
import numpy
import glob
import os
import re
import glob
import shutil
from collections import defaultdict
from ..poker_environment import PokerEnvironment
from ..poker_point import PokerPoint
from ..poker_config import PokerConfig
from ..poker_opponents import (PokerAlwaysCallOpponent, PokerAlwaysRaiseOpponent, PokerLooseAgressiveOpponent, 
    PokerLoosePassiveOpponent, PokerTightAgressiveOpponent, PokerTightPassiveOpponent, PokerBayesianTesterOpponent, 
    PokerBayesianOpponent)
from ...default_environment import reset_points_ids
from ....utils.team_reader import read_team_from_json, initialize_actions_for_second_layer
from ....utils.helpers import round_value, flatten, accumulative_performances
from ....config import Config

class PokerAnalysis():

    def __init__(self):
        pass

    def run_folder_for_acc_curve(self, folder_path, matches, balanced, player2_file_or_opponent_type, 
            player2_is_sbb, generate_debug_files_per_match, debug_folder, river_round_only, 
            second_layer_enabled, seed = None):
        self._setup_config(second_layer_enabled, generate_debug_files_per_match, river_round_only, seed)
        environment, points = self._setup_environment(balanced, matches)

        player1_is_sbb = True
        if player2_is_sbb and not player2_file_or_opponent_type == PokerBayesianTesterOpponent and not player2_file_or_opponent_type == PokerBayesianOpponent:
            player2 = self._create_player("sbb", balanced, second_layer_enabled, json_path=player2_file_or_opponent_type)
            self._setup_attributes(player2)
        else:
            if player2_file_or_opponent_type == PokerBayesianTesterOpponent or player2_file_or_opponent_type == PokerBayesianOpponent:
                player2 = self._create_player("static", balanced, second_layer_enabled, json_path=None, classname=player2_file_or_opponent_type, test_bayesian_alfa=None, test_bayesian_beta=None)
                self._setup_attributes(player2)
            else:
                player2 = self._create_player("static", balanced, second_layer_enabled, classname=player2_file_or_opponent_type)

        teams_population = []
        for filename in glob.glob(folder_path+"*"):
            player1 = self._create_player("sbb", balanced, second_layer_enabled, json_path=filename)
            self._setup_attributes(player1)
            self._execute_matches(player1, player2, player1_is_sbb, player2_is_sbb, points, environment)
            teams_population.append(player1)
      
        sorting_criteria = lambda x: x.score_testset_
        get_results_per_points = lambda x: x.results_per_points_for_validation_
        point_ids = [point.point_id_ for point in points]
        r = accumulative_performances(teams_population, point_ids, sorting_criteria, get_results_per_points)
        individual_performance, accumulative_performance, teams_ids = r

        msg = ""
        msg += "\n\nindividual_values = "+str(individual_performance)
        msg += "\n\nacc_values = "+str(accumulative_performance)
        msg += "\n\nteams_ids = "+str(teams_ids)
        print msg
        with open(debug_folder+"acc_curves.log", 'w') as f:
            f.write(msg)

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
            second_layer_enabled, seed = None, test_bayesian_alfa = None, test_bayesian_beta = None):
        print "Starting poker analysis tool"

        self._setup_config(second_layer_enabled, generate_debug_files_per_match, river_round_only, seed)
        environment, points = self._setup_environment(balanced, matches)
        player1, player2 = self._setup_players(player1_is_sbb, player1_file_or_opponent_type, player2_is_sbb, 
            player2_file_or_opponent_type, balanced, second_layer_enabled, test_bayesian_alfa, test_bayesian_beta, debug_folder)
        self._execute_matches(player1, player2, player1_is_sbb, player2_is_sbb, points, environment)
        
        # WARNING: The stats are only support one sbb player
        metrics_player = None
        if player1_is_sbb:
            metrics_player = player1
        if player2_is_sbb:
            metrics_player = player2
        if metrics_player is not None:
            # sum1 = sum([int(r['score'][0]) for r in messages if r['players'][0] == 'sbb'])
            # sum2 = sum([int(r['score'][1]) for r in messages if r['players'][1] == 'sbb'])
            final_message = "\nResult (team stats): "+str(metrics_player.metrics(full_version=True))
            final_message += "\n--- Results for matches:"
            # final_message += "\nResult (total chips): "+str(sum1+sum2)+" out of [-"+str(self._maximum_winning()*matches)+",+"+str(self._maximum_winning()*matches)+"]"
            final_message += "\nResult (normalized): "+str(metrics_player.score_testset_)
            print final_message
            with open(Config.USER['reinforcement_parameters']['debug']['output_path']+"team_summary.log", 'w') as f:
                f.write(final_message)
            result = metrics_player.get_behaviors_metrics()
            # result['total_chips'] = sum1+sum2
            return result
            # return metrics_player.score_testset_

    def _setup_config(self, second_layer_enabled, generate_debug_files_per_match, river_round_only, seed):
        print "Setup the configuration..."
        # WARNING: Config.RESTRICTIONS should be exactly the same as the one used to train these teams
        Config.USER['task'] = 'reinforcement'
        Config.USER['reinforcement_parameters']['environment'] = 'poker'
        # Config.USER['advanced_training_parameters']['extra_registers'] = 4
        Config.USER['advanced_training_parameters']['second_layer']['enabled'] = second_layer_enabled
        Config.USER['advanced_training_parameters']['second_layer']['use_atomic_actions'] = False
        Config.USER['reinforcement_parameters']['debug']['matches'] = generate_debug_files_per_match
        Config.USER['reinforcement_parameters']['debug']['print'] = True
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
            player2_file_or_opponent_type, balanced, second_layer_enabled, test_bayesian_alfa, test_bayesian_beta, debug_folder):
        print "Loading players..."

        if player1_is_sbb and not player1_file_or_opponent_type == PokerBayesianTesterOpponent and not player1_file_or_opponent_type == PokerBayesianOpponent:
            player1 = self._create_player("sbb", balanced, second_layer_enabled, json_path=player1_file_or_opponent_type)
            self._setup_attributes(player1)
        else:
            if player1_file_or_opponent_type == PokerBayesianTesterOpponent or player1_file_or_opponent_type == PokerBayesianOpponent:
                player1 = self._create_player("static", balanced, second_layer_enabled, json_path=None, classname=player1_file_or_opponent_type, test_bayesian_alfa=test_bayesian_alfa, test_bayesian_beta=test_bayesian_beta)
                self._setup_attributes(player1)
            else:
                player1 = self._create_player("static", balanced, second_layer_enabled, classname=player1_file_or_opponent_type)

        if player2_is_sbb and not player2_file_or_opponent_type == PokerBayesianTesterOpponent and not player2_file_or_opponent_type == PokerBayesianOpponent:
            player2 = self._create_player("sbb", balanced, second_layer_enabled, json_path=player2_file_or_opponent_type)
            self._setup_attributes(player2)
        else:
            if player2_file_or_opponent_type == PokerBayesianTesterOpponent or player2_file_or_opponent_type == PokerBayesianOpponent:
                player2 = self._create_player("static", balanced, second_layer_enabled, json_path=None, classname=player2_file_or_opponent_type, test_bayesian_alfa=test_bayesian_alfa, test_bayesian_beta=test_bayesian_beta)
                self._setup_attributes(player2)
            else:
                player2 = self._create_player("static", balanced, second_layer_enabled, classname=player2_file_or_opponent_type)
        
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

    def _create_player(self, player_type, balanced, second_layer_enabled, json_path=None, classname=None, test_bayesian_alfa=None, test_bayesian_beta=None):
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
            folder_path = os.path.dirname(os.path.abspath(json_path))
            if second_layer_enabled:
                if os.path.isfile(folder_path+"/actions.json"):
                    initialize_actions_for_second_layer(folder_path+"/actions.json")
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
            team.reset_registers()
            # player2.reset_registers() # !
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

    def _decode_message(self, message):
        """
        message: 0:f:5s8h|7s4c:5|-5:opponent|sbb
        result: {'hole_cards': ['5s8h', '7s4c'], 'board_cards': [], 'players': ['opponent', 'sbb'], 'score': ['5', '-5'], 'position': '0', 'rounds': ['f']}

        message: 0:rrrc/rrrrc/rrrrc/rrrrc:Js2c|5cTh/4c3hTs/4h/Qs:-240|240:sbb|opponent
        result: {'hole_cards': ['Js2c', '5cTh'], 'board_cards': ['4c3hTs', '4h', 'Qs'], 'players': ['sbb', 'opponent'], 'score': ['-240', '240'], 'position': '0', 'rounds': ['rrrc', 'rrrrc', 'rrrrc', 'rrrrc']}
        """
        result = {}
        splitted = message.split(":")
        result['position'] = splitted[0]
        result['rounds'] = splitted[1].split("/")
        cards = splitted[2].split("/")
        result['hole_cards'] = cards[0].split("|")
        result['board_cards'] = cards[1:]
        if len(result['board_cards']) > 0:
            result['board_cards_temp'] = result['board_cards'][0][0:2]+" "+result['board_cards'][0][2:4]+" "+result['board_cards'][0][4:5]
        result['score'] = splitted[3].split("|")
        result['players'] = splitted[4].split("|")
        return result