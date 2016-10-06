#!/usr/bin/env python
# encoding: utf-8
## vim:ts=4:et:nowrap

import random
import time
import os
import sys
import numpy
import json
from core.program import Program, reset_programs_ids
from core.team import Team, reset_teams_ids
from core.instruction import Instruction
from environments.classification.classification_environment import ClassificationEnvironment
from environments.reinforcement.tictactoe.tictactoe_environment import TictactoeEnvironment
from environments.reinforcement.poker.poker_environment import PokerEnvironment
from environments.reinforcement.sockets.reinforcement_with_sockets_environment import ReinforcementEnvironmentWithSockets
from core.selection import Selection
from utils.run_info import RunInfo
from utils.team_reader import initialize_actions_for_second_layer
from utils.helpers import round_value
from config import Config

class SBB:
    """
    The main algorithm of SBB:
    
    1. initialize the environment
    2. for each run
        1. initialize the populations
        2. while current_generation < final_generation
            1. selection
                1. evaluate
                2. keep the best teams / remove the others
                3. generate children via mutation
    """

    def __init__(self):
        self.current_generation_ = 0
        self.best_scores_per_runs_ = [] # used by tests
        total_registers = (Config.RESTRICTIONS['genotype_options']['output_registers'] 
            + Config.USER['advanced_training_parameters']['extra_registers'])
        Config.RESTRICTIONS['genotype_options']['total_registers'] = total_registers
        self._initialize_seeds()
        self.environment_ = self._initialize_environment()
        self.selection_ = Selection(self.environment_)
        self.run_infos_ = []

    def _initialize_seeds(self):
        if isinstance(Config.USER['advanced_training_parameters']['seed'], list):
            self.seeds_per_run_ = Config.USER['advanced_training_parameters']['seed']
        else:
            if not Config.USER['advanced_training_parameters']['seed']:
                Config.USER['advanced_training_parameters']['seed'] = random.randint(0, 
                    Config.RESTRICTIONS['max_seed'])
            random.seed(Config.USER['advanced_training_parameters']['seed'])
            self.seeds_per_run_ = []
            for index in range(Config.USER['training_parameters']['runs_total']):
                self.seeds_per_run_.append(random.randint(0, Config.RESTRICTIONS['max_seed']))

    def run(self):
        print "\n### Starting pSBB"

        initial_info = self._generate_initial_message_output()
        print initial_info

        for run_id in range(Config.USER['training_parameters']['runs_total']):
            
            run_info = RunInfo(run_id+1, self.environment_, self.seeds_per_run_[run_id])
            print "\nStarting run: "+str(run_info.run_id)

            self._set_seed(run_info.seed)

            if Config.USER['advanced_training_parameters']['second_layer']['enabled']:
                self._initialize_actions(run_info)

            self.current_generation_ = 0

            teams_population, programs_population = self._initialize_populations()
            
            self.environment_.reset()

            while not self._stop_criterion():
                self.current_generation_ += 1
                
                validation = False
                if self._is_validation():
                    validation = True

                teams_population, programs_population, pareto_front = self.selection_.run(
                    self.current_generation_, teams_population, programs_population)

                if self._stop_criterion():
                    older_teams = [team for team in teams_population if team.generation != self.current_generation_]
                    for team in older_teams:
                        team.prune_total()

                self.environment_.metrics_.store_per_generation_metrics(run_info, teams_population, 
                    self.current_generation_, self.selection_.previous_diversity_)

                if not validation:
                    print ".",
                    sys.stdout.flush()
                else:
                    best_team = self.environment_.validate(self.current_generation_, teams_population)
                    self.environment_.metrics_.store_per_validation_metrics(run_info, best_team, 
                        teams_population, programs_population, self.current_generation_)
                    print "\n\n>>>>> Generation: "+str(self.current_generation_)+", run: "+str(run_info.run_id)
                    self.environment_.metrics_.print_per_validation_metrics(run_info, best_team)
                    print "\n<<<<< Generation: "+str(self.current_generation_)+", run: "+str(run_info.run_id)

            self.environment_.metrics_.store_per_run_metrics(run_info, best_team, teams_population, pareto_front, 
                self.current_generation_)

            run_info.end()
            print("\nFinished run "+str(run_info.run_id)+", elapsed time: "+str(run_info.elapsed_time_)+" mins")
            self.run_infos_.append(run_info)
            sys.stdout.flush()
        
        # finalize execution (get final metrics, print to output, print to file)
        msg = self.environment_.metrics_.generate_overall_metrics_output(self.run_infos_)

        elapseds_per_run = [run.elapsed_time_ for run in self.run_infos_]
        msg += "\n\nFinished execution, total elapsed time: "+str(round_value(sum(elapseds_per_run)))+" mins "
        msg += "(mean: "+str(round_value(numpy.mean(elapseds_per_run)))+", std: "+str(round_value(numpy.std(elapseds_per_run)))+")"

        initial_info += msg
        self.best_scores_per_runs_ = [round_value(run.best_team_.score_champion_) for run in self.run_infos_]
        print initial_info
        sys.stdout.flush()
        if Config.RESTRICTIONS['write_output_files']:
            self._write_output_files(initial_info)
    
    def _initialize_environment(self):
        environment = None
        if Config.USER['task'] == 'classification':
            environment = ClassificationEnvironment()
        if Config.USER['task'] == 'reinforcement':
            if Config.USER['reinforcement_parameters']['environment'] == 'tictactoe':
                environment = TictactoeEnvironment()
            if Config.USER['reinforcement_parameters']['environment'] == 'poker':
                environment = PokerEnvironment()
            if Config.USER['reinforcement_parameters']['environment'] == 'sockets':
                environment = ReinforcementEnvironmentWithSockets()
        if environment is None:
            raise ValueError("No environment exists for "+str(Config.USER['task']))
        return environment

    def _generate_initial_message_output(self):
        initial_info = ""
        initial_info += "\n### CONFIG: "+str(Config.USER)+"\n"
        initial_info +=  "\n### RESTRICTIONS: "+str(Config.RESTRICTIONS)+"\n"
        initial_info += self.environment_.metrics_.quick_metrics()
        initial_info += "\nSeeds per run: "+str(self.seeds_per_run_)
        initial_info += "\nDiversities: "+str(Config.USER['advanced_training_parameters']['diversity']['metrics'])
        return initial_info

    def _set_seed(self, seed):
        random.seed(seed)
        numpy.random.seed(seed)

    def _initialize_actions(self, run_info):
        path = str(Config.USER['advanced_training_parameters']['second_layer']['path']).replace("[run_id]", 
            str(run_info.run_id))
        if not os.path.exists(path):
            raise ValueError("Path for second layer actions doesn't exist: "+str(path))
        initialize_actions_for_second_layer(path, self.environment_)
        total_team_actions = len(Config.RESTRICTIONS['second_layer']['action_mapping'])
        Config.RESTRICTIONS['total_actions'] = total_team_actions

    def _initialize_populations(self):
        """
        Initialize a population of teams with ['team_size']['min'] unique random programs with distinct actions.
        Then randomly add already created programs to the teams.
        """
        if Config.USER['training_parameters']['team_size']['min'] > Config.RESTRICTIONS['total_actions']:
            raise ValueError("The team minimum size is lower than the total number of actions, "
                "it is not possible to initialize a distinct set of actions per team!")
        
        reset_teams_ids()
        reset_programs_ids()
        teams_population = []
        programs_population = []
        for t in range(Config.USER['training_parameters']['populations']['teams']):
            available_actions = range(Config.RESTRICTIONS['total_actions'])
            programs = []
            for index in range(Config.USER['training_parameters']['team_size']['min']):
                program = self._initialize_random_program(available_actions)
                available_actions.remove(program.action)
                programs.append(program)
            team = Team(self.current_generation_, programs, self.environment_)
            teams_population.append(team)
            programs_population += programs

        return teams_population, programs_population

    def _initialize_random_program(self, available_actions):
        instructions = []
        total_instructions = random.randrange(Config.USER['training_parameters']['program_size']['min'], 
            Config.USER['training_parameters']['program_size']['max']+1)
        for i in range(total_instructions):
            instructions.append(Instruction())
        action = random.choice(available_actions)
        program = Program(self.current_generation_, instructions, action)
        return program

    def _stop_criterion(self):
        if self.current_generation_ == Config.USER['training_parameters']['generations_total']:
            return True
        return False

    def _is_validation(self):
        if self.current_generation_ == 1:
            return True
        mult = self.current_generation_ % Config.USER['training_parameters']['validate_after_each_generation']
        if mult == 0:
            return True
        return False

    def _write_output_files(self, initial_info):
        self.filepath_ = self._create_folder()
        with open(self.filepath_+"metrics_overall.txt", "w") as text_file:
            text_file.write(initial_info)
        for run in self.run_infos_:
            path = self.filepath_+"run"+str(run.run_id)+"/"
            os.makedirs(path)
            with open(path+"metrics.txt", "w") as text_file:
                text_file.write(str(run))
            with open(path+"best_team.txt", "w") as text_file:
                text_file.write(str(run.best_team_))
            with open(path+"best_team.json", "w") as text_file:
                text_file.write(run.best_team_.json())
            self._save_teams(run.teams_in_last_generation_, path+"last_generation_teams/")
            self._save_teams(run.pareto_front_in_last_generation_, path+"last_pareto_front/")
            self._save_teams(run.hall_of_fame_in_last_generation_, path+"last_hall_of_fame/")
            os.makedirs(path+"second_layer_files/")
            for key in run.second_layer_files_.keys():
                self._save_teams_in_actions_file(run.second_layer_files_[key], path+"second_layer_files/"+key+"_")
        print "\n### Files saved at "+self.filepath_+"\n"

    def _create_folder(self):
        if not os.path.exists("outputs/"):
            os.makedirs("outputs/")
        localtime = time.localtime()
        hours = "%02d%02d%02d" % (localtime.tm_hour,localtime.tm_min,localtime.tm_sec,)
        pretty_localtime = str(localtime.tm_year)+"-"+str(localtime.tm_mon)+"-"+str(localtime.tm_mday)+"-"+hours
        if Config.USER['task'] == 'classification':
            filename = Config.USER['classification_parameters']['dataset']
        else:
            filename = Config.USER['reinforcement_parameters']['environment']
        filepath = "outputs/"+str(filename)+"_"+pretty_localtime+"/"
        os.makedirs(filepath)
        return filepath

    def _save_teams(self, teams, path):
        if len(teams) > 0:
            os.makedirs(path)
            json_path = path+"json/"
            os.makedirs(json_path)
            for team in teams:
                with open(path+team.__repr__()+".txt", "w") as text_file:
                    text_file.write(str(team))
                with open(json_path+team.__repr__()+".json", "w") as text_file:
                    text_file.write(team.json())

    def _save_teams_in_actions_file(self, teams, path):
        if len(teams) > 0:
            actions = {}
            for index, team in enumerate(teams):
                actions[index] = team.dict()
            with open(path+"actions.json", "w") as text_file:
                text_file.write(json.dumps(actions))