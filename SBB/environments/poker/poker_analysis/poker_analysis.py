import json
import random
import linecache
import numpy
import glob
import re
import shutil
from collections import defaultdict
from ..poker_environment import PokerEnvironment
from ..poker_point import PokerPoint
from ..poker_config import PokerConfig
from ..opponent_model import OpponentModel
from ..poker_opponents import PokerAlwaysCallOpponent, PokerAlwaysRaiseOpponent, PokerLooseAgressiveOpponent, PokerLoosePassiveOpponent, PokerTightAgressiveOpponent, PokerTightPassiveOpponent
from ...default_environment import reset_points_ids
from ....utils.team_reader import read_team_from_json
from ....utils.helpers import round_value, flatten
from ....config import Config

class PokerAnalysis():

    def __init__(self):
        pass

    def run_for_all_opponents(self, matches, balanced, team_file, generate_debug_files_per_match, generate_debug_files_per_players, debug_folder, seed = None):
        opponents = [PokerLooseAgressiveOpponent, PokerLoosePassiveOpponent, PokerTightAgressiveOpponent, PokerTightPassiveOpponent]
        results = []
        for opponent in opponents:
            result = self.run(matches, balanced, team_file, opponent, generate_debug_files_per_match, generate_debug_files_per_players, debug_folder, seed)
            results.append(result)
        player1 = self._create_player("sbb", json_path=team_file)
        print "\n\nPLAYER: "+str(player1.__repr__())
        for o, r in zip(opponents, results):
            with open(debug_folder+str(player1.__repr__())+"/team_summary_overall.log", 'w') as f:
                m = "###### "+o.OPPONENT_ID+"\n"
                for key, value in r.iteritems():
                    m += key+": "+str(value)+"\n"
                print m
                f.write(m)

    def run(self, matches, balanced, team_file, opponent_type, generate_debug_files_per_match, generate_debug_files_per_players, debug_folder, seed = None):
        print "Starting poker analysis tool"

        print "Setup the configuration..."
        # WARNING: Config.RESTRICTIONS should be exactly the same as the one used to train these teams
        Config.USER['task'] = 'reinforcement'
        Config.USER['reinforcement_parameters']['environment'] = 'poker'
        Config.USER['advanced_training_parameters']['extra_registers'] = 3
        Config.USER['advanced_training_parameters']['second_layer']['enabled'] = False
        Config.USER['advanced_training_parameters']['second_layer']['use_atomic_actions'] = False
        Config.USER['reinforcement_parameters']['debug']['matches'] = generate_debug_files_per_match
        Config.USER['reinforcement_parameters']['debug']['print'] = False
        Config.USER['reinforcement_parameters']['debug']['players'] = generate_debug_files_per_players
        Config.RESTRICTIONS['genotype_options']['total_registers'] = Config.RESTRICTIONS['genotype_options']['output_registers'] + Config.USER['advanced_training_parameters']['extra_registers']
        if seed is None:
            seed = random.randint(0, Config.RESTRICTIONS['max_seed'])
        random.seed(seed)
        numpy.random.seed(seed)
        print "...seed = "+str(seed)
        print "...finished setup the configuration."

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

        print "Loading players..."
        # WARNING: The stats are only processed for player1
        # WARNING: Right now, only works for player1 = 'sbb' and player2 = 'static'
        player1 = self._create_player("sbb", json_path=team_file)
        player2 = self._create_player("static", classname=opponent_type)
        self._setup_attributes(player1)
        # self._setup_attributes(player2)
        Config.USER['reinforcement_parameters']['debug']['output_path'] = debug_folder+str(player1.__repr__())+"/"+str(opponent_type.OPPONENT_ID)+"/"
        print "...finished loading players."

        print "Executing matches..."
        self._evaluate_teams(player1, player2, points, environment)
        print "...finished executing matches."

        print "Processing logs..."
        path = Config.USER['reinforcement_parameters']['debug']['output_path']+"match_output"
        files = glob.glob(path+"/*")
        data = {}
        for name in files:
            temp = None
            with open(name) as f:
                for line in f:
                    if "STATE" in line:
                        temp = line.replace("\n", "")
                        temp = temp.replace("STATE:", "")
            name = name.replace(".log", "")
            name = name.replace(path+"/", "")
            data[int(name)] = temp
        states = data.values()
        with open(Config.USER['reinforcement_parameters']['debug']['output_path']+"matches_summary.log", 'w') as f:
            for i, s in enumerate(states):
                m = "match #"+str(i+1)+": "+s
                f.write(m+"\n")
                print m
        shutil.rmtree(path)
        messages = []
        for i, s in enumerate(states):
            message = self._decode_message(s)
            messages.append(message)
        print "...finished processing logs."

        print

        sum1 = sum([int(r['score'][0]) for r in messages if r['players'][0] == 'sbb'])
        sum2 = sum([int(r['score'][1]) for r in messages if r['players'][1] == 'sbb'])
        final_message = "\nResult (team stats): "+str(player1.metrics(full_version=True))
        final_message += "\n--- Results for matches:"
        final_message += "\nResult (total chips): "+str(sum1+sum2)+" out of [-"+str(self.maximum_winning()*matches)+",+"+str(self.maximum_winning()*matches)+"]"
        final_message += "\nResult (normalized): "+str(player1.score_testset_)
        print final_message
        with open(Config.USER['reinforcement_parameters']['debug']['output_path']+"team_summary.log", 'w') as f:
            f.write(final_message)
        result = player1.get_behaviors_metrics()
        result['total_chips'] = sum1+sum2
        result['normalized_chips'] = player1.score_testset_
        return result

    def maximum_winning(self):
        max_small_bet_turn_winning = PokerConfig.CONFIG['small_bet']*4
        max_big_bet_turn_winning = PokerConfig.CONFIG['big_bet']*4
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

    def _create_player(self, player_type, json_path=None, classname=None):
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
            print "...loaded 'sbb' player: "+str(player.__repr__()) 
            return player
        elif player_type == "static":
            print "Loading 'static' player"
            if classname is None:
                print "Error: 'classname' is None"
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

        team.action_sequence_['coding1'] = []
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

    def _evaluate_teams(self, player1, player2, points, environment):
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
            results.append(result)
        for key in extra_metrics_opponents:
            extra_metrics_opponents[key] = round_value(numpy.mean(extra_metrics_opponents[key]))
        team.extra_metrics_['opponents'] = extra_metrics_opponents
        for key in extra_metrics_points:
            for subkey in extra_metrics_points[key]:
                extra_metrics_points[key][subkey] = round_value(numpy.mean(extra_metrics_points[key][subkey]))
        team.extra_metrics_['points'] = extra_metrics_points
        team.score_testset_ = numpy.mean(results)

        self_long_term_agressiveness = []
        self_agressiveness_preflop = []
        self_agressiveness_postflop = []
        self_tight_loose = []
        self_passive_aggressive = []
        self_bluffing = []
        for key, item in team.opponent_model.iteritems():
            self_long_term_agressiveness += item.self_agressiveness
            self_agressiveness_preflop += item.self_agressiveness_preflop
            self_agressiveness_postflop += item.self_agressiveness_postflop
            self_tight_loose += item.self_tight_loose
            self_passive_aggressive += item.self_passive_aggressive
            self_bluffing += item.self_bluffing
        agressiveness = 0.5
        volatility = 0.5
        tight_loose = 0.5
        passive_aggressive = 0.5
        bluffing = 0.0
        if len(self_long_term_agressiveness) > 0:
            agressiveness = numpy.mean(self_long_term_agressiveness)
        if len(self_agressiveness_preflop) > 0 and len(self_agressiveness_postflop) > 0:
            volatility = OpponentModel.calculate_volatility(self_agressiveness_postflop, self_agressiveness_preflop)
        if len(self_tight_loose) > 0:
            tight_loose = numpy.mean(self_tight_loose)
        if len(self_passive_aggressive) > 0:
            passive_aggressive = numpy.mean(self_passive_aggressive)
        if len(self_bluffing) > 0:
            bluffing = numpy.mean(self_bluffing)

        team.extra_metrics_['agressiveness'] = agressiveness
        team.extra_metrics_['volatility'] = volatility
        team.extra_metrics_['tight_loose'] = tight_loose
        team.extra_metrics_['passive_aggressive'] = passive_aggressive
        team.extra_metrics_['bluffing'] = bluffing

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