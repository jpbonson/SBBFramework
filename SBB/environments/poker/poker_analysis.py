import json
import random
import linecache
import numpy
from collections import defaultdict
from poker_environment import PokerEnvironment
from poker_point import PokerPoint
from poker_config import PokerConfig
from opponent_model import OpponentModel
from poker_opponents import PokerAlwaysCallOpponent, PokerAlwaysRaiseOpponent, PokerLooseAgressiveOpponent, PokerLoosePassiveOpponent, PokerTightAgressiveOpponent, PokerTightPassiveOpponent
from ..default_environment import reset_points_ids
from ...utils.team_reader import read_team_from_json
from ...utils.helpers import round_value, flatten
from ...config import Config

class PokerAnalysis():

    PARAMETERS = {
        'matches': 100,
        'balanced': True,
        # +players
    }

    def __init__(self):
        pass

    # TODO: testar se da para seedar?
    # TODO: permitir args do run_poker_analysis (goal: esconder codigo do Andrew)
    #  cofnerir lgos gerados por 'debug_matches'
    # conferir se eh comaptivel com o tipo de log o Andrew quer
    # conferir os outros stats que era legal um team ter
        # - adicionar na info do team todos os atributos 'self' do oponent model
        # - adicionar input 'self' (e 'opp'?) para bleff? (eg.: agressividade/hand_str)

    def run(self):
        print "Starting poker analysis tool"

        print "Setup the configuration..."
        # WARNING: Config.RESTRICTIONS should be exactly the same as the one used to train these teams
        Config.USER['task'] = 'reinforcement'
        Config.USER['reinforcement_parameters']['environment'] = 'poker'
        Config.USER['advanced_training_parameters']['extra_registers'] = 3 # TODO: fazer isso ser definido automaticamente de acordo com o input em .json?
        Config.USER['advanced_training_parameters']['second_layer']['enabled'] = False
        Config.USER['advanced_training_parameters']['second_layer']['use_atomic_actions'] = False
        Config.USER['reinforcement_parameters']['debug_matches'] = False # !!!!!!!!!!!!!!
        # TODO: conferir se mais algo precisar ser setado aqui
        Config.RESTRICTIONS['genotype_options']['total_registers'] = Config.RESTRICTIONS['genotype_options']['output_registers'] + Config.USER['advanced_training_parameters']['extra_registers']
        print "...finished setup the configuration"

        print "Initializing the environment..."
        environment = PokerEnvironment()
        reset_points_ids()
        if PokerAnalysis.PARAMETERS['balanced']:
            points = environment._initialize_random_population_of_points(PokerAnalysis.PARAMETERS['matches'], ignore_cache = True)
        else:
            points = self._create_unbalanced_points(PokerAnalysis.PARAMETERS['matches'])
        for point in points:
            point.teams_results_ = []
        print "...created "+str(len(points))+" points."
        print "...initialized the environment"

        print "Loading players..."
        # WARNING: The stats are only processed for player1
        # WARNING: Roght now, only works for player1 = 'sbb' and player2 = 'static'
        player1 = self._create_player("sbb", json_path="poker_analysis_files/(3902-94).json")
        player2 = self._create_player("static", classname=PokerLooseAgressiveOpponent)
        self._setup_attributes(player1)
        # self._setup_attributes(player2)
        print "...finished loading players..."

        print "Executing matches..."
        self._evaluate_teams(player1, player2, points, environment)
        print "...finished executing matches..."

        print
        print "Result: "+str(player1.metrics(full_version=True))
        print "\n\nFinal Result: "+str(player1.score_testset_)

    def _create_unbalanced_points(self, total_points):
        num_lines_per_file = sum([1 for line in open("SBB/environments/poker/hand_types/hands_type_all.json")])
        idxs = random.sample(range(1, num_lines_per_file+1), total_points)
        result = [linecache.getline("SBB/environments/poker/hand_types/hands_type_all.json", i) for i in idxs]
        data = [PokerPoint(0, json.loads(r)) for r in result]
        mapping = {'00': 0, '01': 1, '02': 2, '10': 3, '11': 4, '12': 5, '20': 6, '21': 7, '22': 8}
        for point in data:
            label0_player = PokerConfig.get_hand_strength_label(point.hand_strength_[3])
            label0_opp = PokerConfig.get_hand_strength_label(point.opp_hand_strength_[3])
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
            print "Loaded 'sbb' player: "+str(player.__repr__()) 
            return player
        elif player_type == "static":
            print "Loading 'static' player"
            if classname is None:
                print "Error: 'classname' is None"
            player = classname()
            print "Loaded 'static' player: "+str(player.__repr__())
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
        for point in points:
            # opponent team
            result = environment._play_match(team, player2, point, Config.RESTRICTIONS['mode']['validation'])
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
        for key, item in team.opponent_model.iteritems():
            self_long_term_agressiveness += item.self_agressiveness
            self_agressiveness_preflop += item.self_agressiveness_preflop
            self_agressiveness_postflop += item.self_agressiveness_postflop
        agressiveness = 0.5
        volatility = 0.5
        if len(self_long_term_agressiveness) > 0:
            agressiveness = numpy.mean(self_long_term_agressiveness)
        if len(self_agressiveness_preflop) > 0 and len(self_agressiveness_postflop) > 0:
            volatility = OpponentModel.calculate_volatility(self_agressiveness_postflop, self_agressiveness_preflop)
        team.extra_metrics_['agressiveness'] = agressiveness
        team.extra_metrics_['volatility'] = volatility

        team.opponent_model = {}
        team.chips = {}