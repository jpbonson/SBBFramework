import os
import json
import random
import numpy
import time
from SBB.environments.tictactoe.tictactoe_opponents import TictactoeRandomOpponent, TictactoeSmartOpponent
from SBB.environments.tictactoe.tictactoe_environment import TictactoeEnvironment
from SBB.environments.default_environment import reset_points_ids
from SBB.utils.team_reader import read_team_from_json, initialize_actions_for_second_layer
from SBB.config import Config

class TTTAnalysis():

    """
    WARNING: Config.RESTRICTIONS in config.py should be exactly the same as the one used to train the teams
    """

    def run(self, matches, player1_file, player2_file_or_opponent_type, player2_is_sbb, 
        second_layer_enabled, print_matches, extra_registers, seed = None):
        print "Starting analysis tool"
        self._setup_config(second_layer_enabled, print_matches, extra_registers, seed)
        environment, points = self._setup_environment(matches)
        player1, player2 = self._setup_players(player1_file, player2_file_or_opponent_type, 
            player2_is_sbb, second_layer_enabled)

        print "Executing matches..."
        self._evaluate_teams(player1, player2, player2_is_sbb, points, environment)
        print "...finished executing matches.\n"
        
        final_message = "\nResult (normalized):"
        final_message += "\n- player1: "+str(player1.score_testset_)
        final_message += "\n- player2: "+str(abs(player1.score_testset_-1.0))
        print final_message

    def _setup_config(self, second_layer_enabled, print_matches, extra_registers, seed):
        print "Setup the configuration..."
        Config.USER['advanced_training_parameters']['extra_registers'] = extra_registers
        Config.USER['advanced_training_parameters']['second_layer']['enabled'] = second_layer_enabled
        Config.USER['reinforcement_parameters']['debug']['print'] = print_matches
        Config.RESTRICTIONS['genotype_options']['total_registers'] = Config.RESTRICTIONS['genotype_options']['output_registers'] + Config.USER['advanced_training_parameters']['extra_registers']
        if seed is None:
            seed = random.randint(0, Config.RESTRICTIONS['max_seed'])
        random.seed(seed)
        numpy.random.seed(seed)
        print "...seed = "+str(seed)
        print "...finished setup the configuration."

    def _setup_environment(self, matches):
        print "Initializing the environment..."
        environment = TictactoeEnvironment()
        reset_points_ids()
        points = environment._initialize_random_population_of_points(matches, ignore_cache = True)
        print "...created "+str(len(points))+" points."
        if len(points) == 0:
            raise ValueError("Error! Zero points created!")
        print "...initialized the environment."
        return environment, points

    def _setup_players(self, player1_file, player2_file_or_opponent_type, 
            player2_is_sbb, second_layer_enabled):
        print "Loading players..."
        player1 = self._create_player("sbb", second_layer_enabled, json_path=player1_file)
        if player2_is_sbb:
            player2 = self._create_player("sbb", second_layer_enabled, json_path=player2_file_or_opponent_type)
        else:
            player2 = self._create_player("static", second_layer_enabled, classname=player2_file_or_opponent_type)
        print "...finished loading players."
        return player1, player2

    def _create_player(self, player_type, second_layer_enabled, json_path=None, classname=None):
        """
        Create a player.
        - sbb player: read a .json file with the team structure
            - if it was built with second layer, then the actions.json used must be the same folder as the team file
        - static player: select one of the classes available in tictactoe_opponents.py
        """
        if player_type == "sbb":
            print "Loading 'sbb' player"
            if json_path is None:
                print "Error: 'json_path' is None"
            with open(json_path) as data_file:    
                data = json.load(data_file)
            player = read_team_from_json(data)

            print "...loaded 'sbb' player: "+str(player.__repr__())
            if second_layer_enabled:
                player.generation = 0 # workaround for second layer
                for program in player.programs:
                    program.generation = 0 # workaround for second layer

                folder_path = os.path.dirname(os.path.abspath(json_path))
                if os.path.isfile(folder_path+"/actions.json"):
                    initialize_actions_for_second_layer(folder_path+"/actions.json")
                    print "...loaded actions"
                else:
                    raise ValueError("Enabled second layer, but no actions.json file found!")
            return player
        elif player_type == "static":
            print "Loading 'static' player"
            if classname is None:
                print "Error: 'classname' is None"
            player = classname()
            print "...loaded 'static' player: "+str(player.__repr__())
            return player
        raise ValueError("Error: No 'player_type' = "+str(player_type)+" implemented.")

    def _evaluate_teams(self, player1, player2, player2_is_sbb, points, environment):
        results = []
        match_id = 0
        for point in points:
            match_id += 1
            print "...player: "+str(player1.__repr__())+", "+str(match_id)
            result = environment._play_match(player1, player2, point, Config.RESTRICTIONS['mode']['validation'], match_id)
            player1.reset_registers()
            if player2_is_sbb:
                player2.reset_registers()
            results.append(result)
        player1.score_testset_ = numpy.mean(results)


def run_config_for_sbb_vs_static():
    TTTAnalysis().run(
        matches=10, # obs.: 2 matches are played for each 'match' value, so both players play in positions 1 and 2

        player1_file="analysis_files/ttt/best_team.json", 
        player2_file_or_opponent_type=TictactoeSmartOpponent,
        player2_is_sbb = False,
        second_layer_enabled = False,

        print_matches=False,
        extra_registers=4, # must be the same value as the one used in training
        seed=1,
    )

def run_config_for_sbb_vs_sbb():
    TTTAnalysis().run(
        matches=10, # obs.: 2 matches are played for each 'match' value, so both players play in positions 1 and 2
        
        player1_file="analysis_files/ttt/best_team.json", 
        player2_file_or_opponent_type="analysis_files/ttt/best_team2.json",
        player2_is_sbb = True,
        second_layer_enabled = False,

        print_matches=False,
        extra_registers=4, # must be the same value as the one used in training
        seed=1,
    )

def run_config_for_sbb_vs_static_for_layer2():
    TTTAnalysis().run(
        matches=10, # obs.: 2 matches are played for each 'match' value, so both players play in positions 1 and 2
        
        player1_file="analysis_files/ttt/best_team_layer2.json", 
        player2_file_or_opponent_type=TictactoeSmartOpponent,
        player2_is_sbb = False,
        second_layer_enabled = True,

        print_matches=False,
        extra_registers=4, # must be the same value as the one used in training
        seed=1,
    )

if __name__ == "__main__":
    start_time = time.time()

    run_config_for_sbb_vs_static()
    # run_config_for_sbb_vs_sbb()
    # run_config_for_sbb_vs_static_for_layer2()
    
    elapsed_time = (time.time() - start_time)/60.0
    print("\nFinished, elapsed time: "+str(elapsed_time)+" mins")

# - executar um best_team.json da pasta config
# - run results for various runs in the configs folder
# - generate acc curve baseado no codigo de poker