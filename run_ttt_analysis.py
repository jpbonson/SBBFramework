import os
import json
import random
import numpy
import time
import glob
from SBB.environments.tictactoe.tictactoe_opponents import TictactoeRandomOpponent, TictactoeSmartOpponent
from SBB.environments.tictactoe.tictactoe_environment import TictactoeEnvironment
from SBB.environments.default_environment import reset_points_ids
from SBB.utils.team_reader import read_team_from_json, initialize_actions_for_second_layer
from SBB.utils.helpers import accumulative_performances
from SBB.config import Config

class TTTAnalysis():

    """
    WARNING: Config.RESTRICTIONS in config.py should be exactly the same as the one used to train the teams
    """

    def run_folder_for_acc_curve(self, matches, folder_path, output_file_name, player2_file_or_opponent_type, player2_is_sbb, 
        second_layer_enabled, second_layer_action_folder, print_matches, extra_registers, seed = None):
        self._setup_config(second_layer_enabled, print_matches, extra_registers, seed)
        environment, points = self._setup_environment(matches)

        print "Loading player 2..."
        if player2_is_sbb:
            player2 = self._create_player("sbb", second_layer_enabled, second_layer_action_folder, json_path=player2_file_or_opponent_type)
        else:
            player2 = self._create_player("static", second_layer_enabled, second_layer_action_folder, classname=player2_file_or_opponent_type)
        print "...finished loading player 2."

        individual_performances_summary = []
        accumulative_performances_summary = []
        debug_folder = "analysis_files/ttt/"
        for folder in glob.glob(folder_path+"run*"):
            print "Executing folder "+str(folder)+"..."
            teams_population = []
            for filename in glob.glob(folder+"/last_generation_teams/json/*"):
                if "actions.json" not in filename:
                    run_id = folder.split("\\")[-1]
                    run_id = run_id.split("/")[-1]
                    second_layer_action_folder_per_run = str(second_layer_action_folder).replace("[run_id]", run_id)
                    player1 = self._create_player("sbb", second_layer_enabled, second_layer_action_folder_per_run, json_path=filename)
                    self._evaluate_teams(player1, player2, player2_is_sbb, points, environment)
                    teams_population.append(player1)
          
            if len(teams_population) > 0:
                sorting_criteria = lambda x: x.score_testset_
                get_results_per_points = lambda x: x.results_per_points_for_validation_
                point_ids = [point.point_id_ for point in points]
                r = accumulative_performances(teams_population, point_ids, sorting_criteria, get_results_per_points)
                individual_performance, accumulative_performance, teams_ids = r
                individual_performances_summary.append(individual_performance)
                accumulative_performances_summary.append(accumulative_performance)

                msg = ""
                msg += "\n\nindividual_values = "+str(individual_performance)
                msg += "\n\nacc_values = "+str(accumulative_performance)
                msg += "\n\nteams_ids = "+str(teams_ids)
                print msg
                # with open(debug_folder+"acc_curves.log", 'w') as f:
                #     f.write(msg)
        msg = ""
        msg += "individual_values = "+str(individual_performances_summary)
        msg += "\nacc_values = "+str(accumulative_performances_summary)
        print msg

        with open(debug_folder+"acc_curves_summary_"+output_file_name+".log", 'w') as f:
            f.write(msg)

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

    def _create_player(self, player_type, second_layer_enabled, second_layer_action_folder, json_path=None, classname=None):
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
            player = classname()
            print "...loaded 'static' player: "+str(player.__repr__())
            return player
        raise ValueError("Error: No 'player_type' = "+str(player_type)+" implemented.")

    def _evaluate_teams(self, player1, player2, player2_is_sbb, points, environment):
        results = []
        match_id = 0
        for point in points:
            match_id += 1
            if match_id % 100 == 0:
                print "...player: "+str(player1.__repr__())+", "+str(match_id)
            result = environment._play_match(player1, player2, point, Config.RESTRICTIONS['mode']['validation'], match_id)
            player1.results_per_points_for_validation_[point.point_id_] = result
            player1.reset_registers()
            if player2_is_sbb:
                player2.reset_registers()
            results.append(result)
        player1.score_testset_ = numpy.mean(results)


def run_config_for_sbb_vs_static():
    TTTAnalysis().run(
        matches=10, # obs.: 2 matches are played for each 'match' value, so both players play in positions 1 and 2

        # player1_file="analysis_files/ttt/best_team.json", 
        player1_file="../outputs/outputs_for_paper_ttt_2/all_teams/config3/run1/last_generation_teams/json/(465-8).json", 

        player2_file_or_opponent_type=TictactoeTrueSmartOpponent,
        player2_is_sbb = False,
        second_layer_enabled = False,

        print_matches=True,
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

def run_config_for_sbb_vs_static_for_acc_curve():
    TTTAnalysis().run_folder_for_acc_curve(
        matches=1000, # obs.: 2 matches are played for each 'match' value, so both players play in positions 1 and 2

        # folder_path="../outputs/outputs_for_paper_ttt_2/all_teams/config3/", 
        folder_path="../outputs/outputs_for_paper_ttt_2/all_teams/second_layer_config2_val5/", 
        output_file_name="config2_val5_layer2_1000m_random",
        player2_file_or_opponent_type=TictactoeSmartOpponent,
        player2_is_sbb = False,
        second_layer_enabled = True,
        second_layer_action_folder = "../outputs/outputs_for_paper_ttt_2/all_teams/config2/partial_files_per_validation/val5/[run_id]_all_actions.json",

        print_matches=False,
        extra_registers=4, # must be the same value as the one used in training
        seed=1,
    )

if __name__ == "__main__":
    start_time = time.time()

    # run_config_for_sbb_vs_static()
    # run_config_for_sbb_vs_static_for_layer2()
    # run_config_for_sbb_vs_sbb()
    run_config_for_sbb_vs_static_for_acc_curve()

    elapsed_time = (time.time() - start_time)/60.0
    print("\nFinished, elapsed time: "+str(elapsed_time)+" mins")

# TODO:

# - poker: falar sobre o bayesian opponent + tipos de runs sendo rodados + river only? + qualo foco do paper?

# - implementar metrica para total complexity para os runs de second layer

# - mandar email para fayez

# - esperando gerar os ultimos charts de layer2 + definir se vai ser gen50 ou gen100 para ttt + ajeitar ttt_config