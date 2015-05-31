#!/usr/bin/env python
# encoding: utf-8
## vim:ts=4:et:nowrap

import random
import time
import numpy
import os
import sys
from collections import Counter
from program import Program, reset_programs_ids
from team import Team, reset_teams_ids
from instruction import Instruction
from environments.classification_environment import ClassificationEnvironment
from environments.tictactoe.tictactoe_environment import TictactoeEnvironment
from selection import Selection
from utils.helpers import round_value, round_array
from config import Config

class SBB:
    def __init__(self):
        self.current_generation_ = 0
        self.best_scores_per_runs_ = [] # used by tests
        if not Config.USER['advanced_training_parameters']['seed']:
            Config.USER['advanced_training_parameters']['seed'] = random.randint(0, sys.maxint) # based on the system time
        random.seed(Config.USER['advanced_training_parameters']['seed'])

    def run(self):
        print "\n### Starting pSBB"

        # initialize metrics (per run)
        elapseds_per_run = []
        best_teams_per_run = []
        score_per_generations_per_runs = []
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
            score_per_generation = []
            diversity_per_generation = []

            # 2. Randomly initialize populations
            self.current_generation_ = 0
            programs_population = self._initialize_program_population()
            teams_population = self._initialize_team_population(programs_population)
            
            environment.reset_point_population()
            while not self._stop_criterion():
                self.current_generation_ += 1
                
                # 3. Selection
                teams_population, programs_population, diversity_means = selection.run(self.current_generation_, teams_population, programs_population)

                # Validate and print metrics
                if self.current_generation_ == 1 or self.current_generation_ % Config.USER['training_parameters']['validate_after_each_generation'] == 0:
                    print "\n\n>>>>> Executing generation: "+str(self.current_generation_)+", run: "+str(run_id)
                    best_team = self._validate(environment, teams_population, score_per_generation, recall_per_generation)
                    for key in best_team.diversity_:
                        print str(key)+": "+str(best_team.diversity_[key])+" (global mean: "+str(diversity_means[key])+")"
                    print "actions distribution: "+str(Counter([p.action for p in programs_population]))+"\n"
                    diversity_per_generation.append(diversity_means)
                else:
                    print str(self.current_generation_),

            # store and print metrics (per run)
            print("\n########## "+str(run_id)+" Run's best team: "+best_team.metrics())
            elapsed_time = time.time() - start_time
            elapseds_per_run.append(elapsed_time)
            best_teams_per_run.append(best_team)
            score_per_generations_per_runs.append(score_per_generation)
            diversity_per_generations_per_runs.append(diversity_per_generation)
            if Config.USER['task'] == 'classification':
                recall_per_generation_per_run.append(recall_per_generation)
            print("\nFinished run "+str(run_id)+", elapsed time: "+str(elapsed_time)+" secs")

        # 4. Finalize execution (get final metrics, print to output, print to file)
        output_messages_for_runs = self._generate_output_messages_for_runs(best_teams_per_run, score_per_generations_per_runs, diversity_per_generations_per_runs, recall_per_generation_per_run)
        print output_messages_for_runs
        msg += self._generate_output_messages_overall(best_teams_per_run, score_per_generations_per_runs, diversity_per_generations_per_runs)
        msg += "\n\nFinished execution, total elapsed time: "+str(round_value(sum(elapseds_per_run)))+" secs "
        msg += "(mean: "+str(round_value(numpy.mean(elapseds_per_run)))+", std: "+str(round_value(numpy.std(elapseds_per_run)))+")"
        print msg
        if Config.RESTRICTIONS['write_output_files']:
            self._write_output_files(best_teams_per_run, msg, output_messages_for_runs)

    def _validate(self, environment, teams_population, score_per_generation, recall_per_generation):
        best_team = environment.validate(teams_population)
        score_per_generation.append(best_team.score_testset_)
        if Config.USER['task'] == 'classification':
            recall_per_generation.append(best_team.extra_metrics_['recall_per_action'])
        print("\nbest team: "+best_team.metrics())
        return best_team

    def _initialize_environment(self):
        if Config.USER['task'] == 'classification':
            return ClassificationEnvironment()
        if Config.USER['task'] == 'reinforcement':
            if Config.USER['reinforcement_parameters']['environment'] == 'tictactoe':
                return TictactoeEnvironment()
        raise ValueError("No environment exists for "+str(Config.USER['task']))

    def _initialize_program_population(self):
        """
        Initialize a population of programs with a random action and random instructions.
        """
        reset_programs_ids()
        programs_population =[]
        for i in range(Config.USER['training_parameters']['populations']['programs']):
            action = random.randrange(Config.RESTRICTIONS['total_actions'])
            instructions = []
            for i in range(Config.USER['training_parameters']['program_size']['initial']):
                instructions.append(Instruction(Config.RESTRICTIONS['total_inputs']))
            program = Program(self.current_generation_, instructions, action)
            programs_population.append(program)
        return programs_population

    def _initialize_team_population(self, programs_population):
        """
        Initialize a population of teams randomly selection programs, one of each action.
        """
        reset_teams_ids()
        teams_population = []
        for t in range(Config.USER['training_parameters']['populations']['teams']):
            selected_programs = []
            programs_per_action = self._get_programs_per_action(programs_population)
            for programs in programs_per_action:
                selected_programs.append(random.choice(programs))
            team = Team(self.current_generation_, selected_programs)
            teams_population.append(team)
        return teams_population

    def _get_programs_per_action(self, programs):
        programs_per_action = []
        for class_index in range(Config.RESTRICTIONS['total_actions']):
            values = [p for p in programs if p.action == class_index]
            if len(values) == 0:
                raise StandardError("_get_programs_per_action() wasn't able to get programs for the action "+str(class_index)+". " \
                    "You got a bug, or the program population size is too small.")
            programs_per_action.append(values)
        return programs_per_action

    def _stop_criterion(self):
        if self.current_generation_ == Config.USER['training_parameters']['generations_total']:
            return True
        return False

    def _generate_output_messages_for_runs(self, best_teams_per_run, score_per_generations_per_runs, diversity_per_generations_per_runs, 
            recall_per_generation_per_run):
        msg = "\n\n#################### BEST RUN ####################"
        scores = [t.score_testset_ for t in best_teams_per_run]
        best_run = scores.index(max(scores))
        if Config.USER['task'] == 'classification':
            recall_per_generation = recall_per_generation_per_run[best_run]
        else:
            recall_per_generation = None
        msg += self._print_run(best_run, best_teams_per_run[best_run], score_per_generations_per_runs[best_run], 
            diversity_per_generations_per_runs[best_run], recall_per_generation)
        msg += "\n\n\n\n################# RESULT PER RUN ####################"
        for run_id in range(Config.USER['training_parameters']['runs_total']):
            if Config.USER['task'] == 'classification':
                recall_per_generation = recall_per_generation_per_run[run_id]
            else:
                recall_per_generation = None
            msg += self._print_run(run_id, best_teams_per_run[run_id], score_per_generations_per_runs[run_id], 
                diversity_per_generations_per_runs[run_id], recall_per_generation)
        return msg

    def _print_run(self, run_id, team, score_per_generation, diversity_per_generation, recall_per_generation):
        msg = "\n\n\n############### "+str(run_id+1)+" Run Best Team: "+team.metrics(full_version = True)
        for key, value in team.diversity_.iteritems():
            msg +=  "\n\n"+str(key)+": "+str(value)
        msg += "\n\n##### Metrics per Generation"
        msg += "\n\nScore per Generation: "+str(round_array(score_per_generation))
        for key in diversity_per_generation[0]:
            array = [item[key] for item in diversity_per_generation]
            msg += "\n\nDiversity per Generation ("+str(key)+"): "+str(array)
        if Config.USER['task'] == 'classification':
            msg += "\n\nRecall per Action per Generation: "+str(recall_per_generation)
        return msg

    def _generate_output_messages_overall(self, best_teams_per_run, score_per_generations_per_runs, diversity_per_generations_per_runs):
        msg = "\n\n\n#################### OVERALL RESULTS ####################"
        score_per_run = []
        for run_id in range(Config.USER['training_parameters']['runs_total']):
            score_per_run.append(round_value(best_teams_per_run[run_id].score_testset_))
        self.best_scores_per_runs_ = score_per_run
        msg += "\n\nTest Score per Run: "+str(score_per_run)
        msg += "\nmean: "+str(numpy.mean(score_per_run))+", std: "+str(numpy.std(score_per_run))

        score_means = []
        score_stds = []
        for index in range(len(score_per_generations_per_runs[0])):
            column = [row[index] for row in score_per_generations_per_runs]
            score_means.append(round_value(numpy.mean(column)))
            score_stds.append(round_value(numpy.std(column)))
        msg += "\n\nMean Score per Generation across Runs: "+str(score_means)
        msg += "\nStd. Deviation Score per Generation across Runs: "+str(score_stds)

        for key in diversity_per_generations_per_runs[0][0]:
            score_means = []
            score_stds = []
            for index in range(len(diversity_per_generations_per_runs[0])):
                column = [row[index] for row in diversity_per_generations_per_runs]
                column = [item[key] for item in column]
                score_means.append(round_value(numpy.mean(column)))
                score_stds.append(round_value(numpy.std(column)))
            msg += "\n\nMean Diversity per Generation across Runs ("+str(key)+"): "+str(score_means)
            msg += "\nStd. Deviation Diversity per Generation across Runs ("+str(key)+"): "+str(score_stds)
        return msg

    def _write_output_files(self, best_teams_per_run, msg, output_messages_for_runs):
        if not os.path.exists(Config.RESTRICTIONS['working_path']+"outputs/"):
            os.makedirs(Config.RESTRICTIONS['working_path']+"outputs/")
        localtime = time.localtime()
        pretty_localtime = str(localtime.tm_year)+"-"+str(localtime.tm_mon)+"-"+str(localtime.tm_mday)+"-"+str(localtime.tm_hour)+str(localtime.tm_min)+str(localtime.tm_sec)
        if Config.USER['task'] == 'classification':
            filename = Config.USER['classification_parameters']['dataset']
        else:
            filename = Config.USER['reinforcement_parameters']['environment']
        filepath = Config.RESTRICTIONS['working_path']+"outputs/"+str(filename)+"_"+pretty_localtime
        os.makedirs(filepath)
        with open(filepath+"/metrics_overall.txt", "w") as text_file:
            text_file.write(msg)
        with open(filepath+"/metrics_per_run.txt", "w") as text_file:
            text_file.write(output_messages_for_runs)
        for run_id in range(Config.USER['training_parameters']['runs_total']):
            with open(filepath+"/best_team_run_"+str(run_id+1)+".txt", "w") as text_file:
                text_file.write(str(best_teams_per_run[run_id]))