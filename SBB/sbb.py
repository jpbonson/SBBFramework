#!/usr/bin/env python
# encoding: utf-8
## vim:ts=4:et:nowrap

import random
import time
import numpy
import os
from collections import Counter
from program import Program, reset_programs_ids
from team import Team, reset_teams_ids
from instruction import Instruction
from environments.classification_environment import ClassificationEnvironment
from environments.tictactoe.tictactoe_environment import TictactoeEnvironment
from diversity_maintenance import DiversityMaintenance
from selection import Selection
from utils.helpers import round_value, round_array
from config import Config

class SBB:
    def __init__(self):
        self.current_generation_ = 0
        self.best_scores_per_runs_ = [] # used by tests
        if not Config.USER['advanced_training_parameters']['seed']:
            Config.USER['advanced_training_parameters']['seed'] = random.randint(0, Config.RESTRICTIONS['max_seed'])
        random.seed(Config.USER['advanced_training_parameters']['seed'])
        numpy.random.seed(Config.USER['advanced_training_parameters']['seed'])

    def run(self):
        print "\n### Starting pSBB"

        # initialize metrics (per run)
        elapseds_per_run = []
        best_teams_per_run = []
        train_score_per_generations_per_runs = []
        test_score_per_generations_per_runs = []
        diversity_per_generations_per_runs = []
        recall_per_generation_per_run = [] # only for classification task

        # 1. Initialize environment and thw selection algorithm
        environment = self._initialize_environment()
        selection = Selection(environment)

        msg = ""
        msg += "\n### CONFIG: "+str(Config.USER)+"\n"
        msg += environment.metrics()
        print msg

        for run_id in range(1, Config.USER['training_parameters']['runs_total']+1):
            print("\nStarting run: "+str(run_id)+"\n")

            # initialize metrics (per generation)
            start_time = time.time()
            recall_per_generation = [] # only used for the classification task
            train_score_per_generation = []
            test_score_per_generation = []
            diversity_per_generation = []

            # 2. Randomly initialize populations
            self.current_generation_ = 0
            teams_population, programs_population = self._initialize_populations()
            
            environment.reset_point_population()
            while not self._stop_criterion():
                self.current_generation_ += 1
                
                if self.current_generation_ == 1 or self.current_generation_ % Config.USER['training_parameters']['validate_after_each_generation'] == 0:
                    validation = True
                else:
                    validation = False

                # 3. Selection
                teams_population, programs_population, diversity_means = selection.run(self.current_generation_, teams_population, programs_population, validation)

                # Validate
                if validation:
                    print "\n\n>>>>> Executing generation: "+str(self.current_generation_)+", run: "+str(run_id)
                    best_team = environment.validate(self.current_generation_, teams_population)

                    # store metrics
                    train_score_per_generation.append(best_team.score_trainingset_)
                    test_score_per_generation.append(best_team.score_testset_)
                    diversity_per_generation.append(diversity_means)
                    if Config.USER['task'] == 'classification':
                        recall_per_generation.append(best_team.extra_metrics_['recall_per_action'])

                    # print metrics
                    print("\nbest team: "+best_team.metrics()+"\n")
                    for key in best_team.diversity_:
                        print str(key)+": "+str(best_team.diversity_[key])+" (global mean: "+str(diversity_means[key])+")"
                    print "\nactions distribution: "+str(Counter([p.action for p in programs_population]))+"\n"
                else:
                    print ".",

            # store and print metrics (per run)
            print("\n########## "+str(run_id)+" Run's best team: "+best_team.metrics())
            elapsed_time = time.time() - start_time
            elapseds_per_run.append(elapsed_time)
            best_teams_per_run.append(best_team)
            train_score_per_generations_per_runs.append(train_score_per_generation)
            test_score_per_generations_per_runs.append(test_score_per_generation)
            diversity_per_generations_per_runs.append(diversity_per_generation)
            if Config.USER['task'] == 'classification':
                recall_per_generation_per_run.append(recall_per_generation)
            print("\nFinished run "+str(run_id)+", elapsed time: "+str(elapsed_time)+" secs")

        # 4. Finalize execution (get final metrics, print to output, print to file)
        output_messages_for_runs = self._generate_output_messages_for_runs(best_teams_per_run, train_score_per_generations_per_runs, 
            test_score_per_generations_per_runs, diversity_per_generations_per_runs, recall_per_generation_per_run)
        print output_messages_for_runs
        msg += self._generate_output_messages_overall(best_teams_per_run, train_score_per_generations_per_runs, test_score_per_generations_per_runs, 
            diversity_per_generations_per_runs)
        msg += "\n\nFinished execution, total elapsed time: "+str(round_value(sum(elapseds_per_run)))+" secs "
        msg += "(mean: "+str(round_value(numpy.mean(elapseds_per_run)))+", std: "+str(round_value(numpy.std(elapseds_per_run)))+")"
        print msg
        if Config.RESTRICTIONS['write_output_files']:
            self._write_output_files(best_teams_per_run, msg, output_messages_for_runs)

    def _initialize_environment(self):
        if Config.USER['task'] == 'classification':
            return ClassificationEnvironment()
        if Config.USER['task'] == 'reinforcement':
            if Config.USER['reinforcement_parameters']['environment'] == 'tictactoe':
                return TictactoeEnvironment()
        raise ValueError("No environment exists for "+str(Config.USER['task']))

    def _initialize_populations(self):
        """
        Initialize a population of teams with ['team_size']['min'] unique random programs with distinct actions.
        Then randomly add already created programs to the teams.
        """
        if Config.USER['training_parameters']['team_size']['min'] > Config.RESTRICTIONS['total_actions']:
            raise ValueError("The team minimum size is lower than the total number of actions, it is not possible to initialize a distinct set of actions per team!")
        
        # randomly initialize teams with the minimum size
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
            team = Team(self.current_generation_, programs)
            teams_population.append(team)
            programs_population += programs

        # randomly add more already created programs to the teams
        programs_range = Config.USER['training_parameters']['program_size']['max'] - Config.USER['training_parameters']['program_size']['min']
        for team in teams_population:
            programs_to_add = random.randrange(0, programs_range+1)
            for index in range(programs_to_add):
                program = random.choice(programs_population)
                if program not in team.programs:
                    team._add_program(program)

        return teams_population, programs_population

    def _initialize_random_program(self, available_actions):
        instructions = []
        total_instructions = random.randrange(Config.USER['training_parameters']['program_size']['min'], Config.USER['training_parameters']['program_size']['max']+1)
        for i in range(total_instructions):
            instructions.append(Instruction(Config.RESTRICTIONS['total_inputs']))
        action = random.choice(available_actions)
        program = Program(self.current_generation_, instructions, action)
        return program

    def _stop_criterion(self):
        if self.current_generation_ == Config.USER['training_parameters']['generations_total']:
            return True
        return False

    def _generate_output_messages_for_runs(self, best_teams_per_run, train_score_per_generations_per_runs, test_score_per_generations_per_runs, 
            diversity_per_generations_per_runs, recall_per_generation_per_run):
        msg = "\n\n#################### BEST RUN ####################"
        scores = [t.score_testset_ for t in best_teams_per_run]
        best_run = scores.index(max(scores))
        if Config.USER['task'] == 'classification':
            recall_per_generation = recall_per_generation_per_run[best_run]
        else:
            recall_per_generation = None
        msg += self._print_run(best_run, best_teams_per_run[best_run], train_score_per_generations_per_runs[best_run], 
            test_score_per_generations_per_runs[best_run], diversity_per_generations_per_runs[best_run], recall_per_generation)
        msg += "\n\n\n\n################# RESULT PER RUN ####################"
        for run_id in range(Config.USER['training_parameters']['runs_total']):
            if Config.USER['task'] == 'classification':
                recall_per_generation = recall_per_generation_per_run[run_id]
            else:
                recall_per_generation = None
            msg += self._print_run(run_id, best_teams_per_run[run_id], train_score_per_generations_per_runs[best_run], 
                test_score_per_generations_per_runs[run_id], diversity_per_generations_per_runs[run_id], recall_per_generation)
        return msg

    def _print_run(self, run_id, team, train_score_per_generation, test_score_per_generation, diversity_per_generation, recall_per_generation):
        msg = "\n\n\n############### "+str(run_id+1)+" Run Best Team: "+team.metrics(full_version = True)
        for key, value in team.diversity_.iteritems():
            msg +=  "\n"+str(key)+": "+str(value)
        msg += "\n\n##### Metrics per Generation"
        msg += "\n\nTrain Score per Generation: "+str(round_array(train_score_per_generation))
        msg += "\n\nTest Score per Generation: "+str(round_array(test_score_per_generation))
        for key in diversity_per_generation[0]:
            array = [item[key] for item in diversity_per_generation]
            msg += "\n\nDiversity per Generation ("+str(key)+"): "+str(array)
        if Config.USER['task'] == 'classification':
            msg += "\n\nRecall per Action per Generation: "+str(recall_per_generation)
        return msg

    def _generate_output_messages_overall(self, best_teams_per_run, train_score_per_generations_per_runs, test_score_per_generations_per_runs, 
            diversity_per_generations_per_runs):
        msg = "\n\n\n#################### OVERALL RESULTS ####################"
        score_per_run = []
        for run_id in range(Config.USER['training_parameters']['runs_total']):
            score_per_run.append(round_value(best_teams_per_run[run_id].score_testset_))
        self.best_scores_per_runs_ = score_per_run
        msg += "\n\nTest Score per Run: "+str(score_per_run)
        msg += "\nmean: "+str(round_value(numpy.mean(score_per_run)))
        msg += "\nstd. deviation: "+str(round_value(numpy.std(score_per_run)))

        score_means, score_stds = self._process_scores(train_score_per_generations_per_runs)
        msg += "\n\nTrain Score per Generation across Runs:"
        msg += "\nmean: "+str(score_means)
        msg += "\nstd. deviation: "+str(score_stds)

        score_means, score_stds = self._process_scores(test_score_per_generations_per_runs)
        msg += "\n\nTest Score per Generation across Runs:"
        msg += "\nmean: "+str(score_means)
        msg += "\nstd. deviation: "+str(score_stds)

        for key in diversity_per_generations_per_runs[0][0]:
            array = [[generation[key] for generation in run] for run in diversity_per_generations_per_runs]
            score_means, score_stds = self._process_scores(array)
            msg += "\n\nMean Diversity per Generation across Runs ("+str(key)+"):"
            msg += "\nmean: "+str(score_means)
            msg += "\nstd. deviation: "+str(score_stds)
        return msg

    def _process_scores(self, score_per_generation_per_run):
        score_means = []
        score_stds = []
        for index in range(len(score_per_generation_per_run[0])):
            column = [row[index] for row in score_per_generation_per_run]
            score_means.append(round_value(numpy.mean(column)))
            score_stds.append(round_value(numpy.std(column)))
        return score_means, score_stds

    def _write_output_files(self, best_teams_per_run, msg, output_messages_for_runs):
        if not os.path.exists("outputs/"):
            os.makedirs("outputs/")
        localtime = time.localtime()
        pretty_localtime = str(localtime.tm_year)+"-"+str(localtime.tm_mon)+"-"+str(localtime.tm_mday)+"-"+str(localtime.tm_hour)+str(localtime.tm_min)+str(localtime.tm_sec)
        if Config.USER['task'] == 'classification':
            filename = Config.USER['classification_parameters']['dataset']
        else:
            filename = Config.USER['reinforcement_parameters']['environment']
        filepath = "outputs/"+str(filename)+"_"+pretty_localtime
        os.makedirs(filepath)
        with open(filepath+"/metrics_overall.txt", "w") as text_file:
            text_file.write(msg)
        with open(filepath+"/metrics_per_run.txt", "w") as text_file:
            text_file.write(output_messages_for_runs)
        for run_id in range(Config.USER['training_parameters']['runs_total']):
            with open(filepath+"/best_team_run_"+str(run_id+1)+".txt", "w") as text_file:
                text_file.write(str(best_teams_per_run[run_id]))