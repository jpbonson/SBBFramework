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
from utils.helpers import round_value_to_decimals
from config import CONFIG, RESTRICTIONS

class SBB:
    def __init__(self):
        self.current_generation_ = 0
        if not CONFIG['advanced_training_parameters']['seed']:
            CONFIG['advanced_training_parameters']['seed'] = random.randint(0, sys.maxint) # based on the system time
        random.seed(CONFIG['advanced_training_parameters']['seed'])

    def run(self):
        print "\n### Starting pSBB"

        # initialize metrics (per run)
        elapseds_per_run = []
        best_teams_per_run = []
        fronts_per_run = [] # only used with using pareto
        avg_score_per_generations_across_runs = [0.0] * (CONFIG['training_parameters']['generations_total']+1)
        recall_per_generation_per_run = [] # only for classification task

        # 1. Initialize environment and thw selection algorithm
        environment = self._initialize_environment()
        selection = Selection(environment)

        msg = ""
        if CONFIG['advanced_training_parameters']['verbose'] > 0:
            msg += "\n### CONFIG: "+str(CONFIG)+"\n"
            msg += environment.metrics()
            print msg

        for run_id in range(1, CONFIG['training_parameters']['runs_total']+1):
            print("\nStarting run: "+str(run_id))

            # initialize metrics (per generation)
            start_time = time.time()
            best_teams_per_generation = []
            recall_per_generation = [] # only used for the classification task

            # 2. Randomly initialize populations
            self.current_generation_ = 0
            programs_population = self._initialize_program_population()
            teams_population = self._initialize_team_population(programs_population)
            
            environment.reset_point_population()
            while not self._stop_criterion():
                self.current_generation_ += 1
                print("\n>>>>> Executing generation: "+str(self.current_generation_)+", run: "+str(run_id))
                
                # 3. Selection
                teams_population, programs_population = selection.run(self.current_generation_, teams_population, programs_population)

                # print metrics for each team in the pareto front
                if CONFIG['advanced_training_parameters']['use_pareto_for_team_population_selection']:
                    print "pareto front:"
                    front = [t for t in teams_population if t.participated_in_front_ == self.current_generation_]
                    for team in front:
                        if team.score_testset_ == -1:
                            environment.evaluate_team(team)
                        print(team.metrics(short_print=True))
                    print "\n"

                # test for best team
                best_team = self._best_team(teams_population)
                environment.evaluate_team(best_team)
                print("best team: "+best_team.metrics())

                # store and print metrics for the best team (per generation)
                best_teams_per_generation.append(best_team)
                avg_score_per_generations_across_runs[self.current_generation_] += best_team.score_testset_
                if CONFIG['task'] == 'classification':
                    recall_per_generation.append(best_team.extra_metrics_['recall_per_action'])
                if CONFIG['advanced_training_parameters']['verbose'] > 0:
                    print "\nactions distribution: "+str(Counter([p.action for p in programs_population]))

            # store and print metrics (per run)
            print("\n"+str(run_id)+" Run's best team: "+best_team.metrics())
            elapsed_time = time.time() - start_time
            elapseds_per_run.append(elapsed_time)
            best_teams_per_run.append(best_team)
            if CONFIG['advanced_training_parameters']['use_pareto_for_team_population_selection']:
                fronts_per_run.append(front)
            if CONFIG['task'] == 'classification':
                recall_per_generation_per_run.append(recall_per_generation)
            print("\nFinished run "+str(run_id)+", elapsed time: "+str(elapsed_time)+" secs")

        # 4. Finalize execution (get final metrics, print to output, print to file)
        best_run = self._select_best_run(best_teams_per_run, fronts_per_run)
        msg += self._generate_output_messages_for_best_per_run(best_teams_per_run, fronts_per_run)
        msg += self._generate_output_messages_for_best_overall(best_run, best_teams_per_run, recall_per_generation_per_run, 
            avg_score_per_generations_across_runs, fronts_per_run)
        msg += "\nFinished execution, total elapsed time: "+str(round_value_to_decimals(sum(elapseds_per_run)))+" secs "
        msg += "(mean: "+str(round_value_to_decimals(numpy.mean(elapseds_per_run)))+", std: "+str(round_value_to_decimals(numpy.std(elapseds_per_run)))+")"
        print msg
        self._write_output_files(best_run, best_teams_per_run, fronts_per_run, msg)

    def _initialize_environment(self):
        if CONFIG['task'] == 'classification':
            return ClassificationEnvironment()
        if CONFIG['task'] == 'reinforcement':
            if CONFIG['reinforcement_parameters']['environment'] == 'tictactoe':
                return TictactoeEnvironment()
        raise ValueError("No environment exists for "+str(CONFIG['task']))

    def _initialize_program_population(self):
        """
        Initialize a population of programs with a random action and random instructions.
        """
        reset_programs_ids()
        programs_population =[]
        for i in range(CONFIG['training_parameters']['populations']['programs']):
            action = random.randrange(RESTRICTIONS['total_actions'])
            instructions = []
            for i in range(CONFIG['training_parameters']['program_size']['initial']):
                instructions.append(Instruction(RESTRICTIONS['total_inputs']))
            program = Program(self.current_generation_, instructions, action)
            programs_population.append(program)
        return programs_population

    def _initialize_team_population(self, programs_population):
        """
        Initialize a population of teams randomly selection programs, one of each action.
        """
        reset_teams_ids()
        teams_population = []
        for t in range(CONFIG['training_parameters']['populations']['teams']):
            selected_programs = []
            programs_per_action = self._get_programs_per_action(programs_population)
            for programs in programs_per_action:
                selected_programs.append(random.choice(programs))
            team = Team(self.current_generation_, selected_programs)
            teams_population.append(team)
        return teams_population

    def _get_programs_per_action(self, programs):
        programs_per_action = []
        for class_index in range(RESTRICTIONS['total_actions']):
            values = [p for p in programs if p.action == class_index]
            if len(values) == 0:
                raise StandardError("_get_programs_per_action() wasn't able to get programs for the action "+str(class_index)+". " \
                    "You got a bug, or the program population size is too small.")
            programs_per_action.append(values)
        return programs_per_action

    def _stop_criterion(self):
        if self.current_generation_ == CONFIG['training_parameters']['generations_total']:
            return True
        return False

    def _best_team(self, teams_population):
        fitness = [p.fitness_ for p in teams_population]
        best_team = teams_population[fitness.index(max(fitness))]
        return best_team

    def _select_best_run(self, best_teams_per_run, fronts_per_run):
        if CONFIG['advanced_training_parameters']['use_pareto_for_team_population_selection']:
            # select the run with the best mean of score_testset_ for the teams in the front
            best_run = -1
            best_mean = -1
            for run_id, front in enumerate(fronts_per_run):
                scores = [t.score_testset_ for t in front]
                mean = numpy.mean(scores)
                if mean > best_mean:
                    best_run = run_id
                    best_mean = mean
        else:
            # select the run with the best score_testset_
            scores = [t.score_testset_ for t in best_teams_per_run]
            best_run = scores.index(max(scores))
        return best_run

    def _generate_output_messages_for_best_per_run(self, best_teams_per_run, fronts_per_run):
        msg = "\n\n################# RESULT PER RUN ####################"
        score_per_run = []
        for run_id in range(CONFIG['training_parameters']['runs_total']):
            best_team = best_teams_per_run[run_id]
            score_per_run.append(round_value_to_decimals(best_team.score_testset_))
            msg += "\n##### "+str(run_id)+" Run best team: "+best_team.metrics()+"\n"
            if CONFIG['advanced_training_parameters']['use_pareto_for_team_population_selection']:
                msg +=  "\npareto front:"
                for team in fronts_per_run[run_id]:
                    msg += team.metrics()+"\n"
                msg += "\n"
        msg += "\n\nTest score per run: "+str(score_per_run)
        msg += "\nTest score, mean: "+str(numpy.mean(score_per_run))+", std: "+str(numpy.std(score_per_run))
        return msg

    def _generate_output_messages_for_best_overall(self, best_run, best_teams_per_run, recall_per_generation_per_run, avg_score_per_generations_across_runs, fronts_per_run):
        best_team_overall = best_teams_per_run[best_run]
        
        msg = "\n\n#################### OVERALL BEST TEAM ####################"
        msg += "\n"+str(best_run)+" Run best team: "+best_team_overall.metrics()

        if CONFIG['advanced_training_parameters']['verbose'] == 2 and CONFIG['task'] == 'classification':
            recall_per_generation = recall_per_generation_per_run[best_run]
            msg += "\n\nrecall_per_action_per_generation: "+str(recall_per_generation)
            msg += "\n\naccuracy: "+str(best_team_overall.extra_metrics_['accuracy'])
            msg += "\n\nconfusion matrix:\n"+str(best_team_overall.extra_metrics_['confusion_matrix'])
            
        if CONFIG['advanced_training_parameters']['verbose'] == 2:
            temp = [round_value_to_decimals(x/float(CONFIG['training_parameters']['runs_total'])) for x in avg_score_per_generations_across_runs]
            msg += "\n\navg_avg_score_per_generations_across_runs: "+str(temp)

        if CONFIG['advanced_training_parameters']['use_pareto_for_team_population_selection']:
            msg += "\n\n#################### OVERALL BEST FRONT ####################"
            for team in fronts_per_run[best_run]:
                msg += team.metrics()+"\n\n"
            msg += "\n"
        return msg

    def _write_output_files(self, best_run, best_teams_per_run, fronts_per_run, msg):
        best_team_overall = best_teams_per_run[best_run]
        if not os.path.exists(RESTRICTIONS['working_path']+"outputs/"):
            os.makedirs(RESTRICTIONS['working_path']+"outputs/")
        localtime = time.localtime()
        pretty_localtime = str(localtime.tm_year)+"-"+str(localtime.tm_mon)+"-"+str(localtime.tm_mday)+"-"+str(localtime.tm_hour)+str(localtime.tm_min)+str(localtime.tm_sec)
        filepath = RESTRICTIONS['working_path']+"outputs/"+str(CONFIG['classification_parameters']['dataset'])+"_output-"+pretty_localtime
        os.makedirs(filepath)
        with open(filepath+"/metrics.txt", "w") as text_file:
            text_file.write(msg)
        with open(filepath+"/best_team_"+best_team_overall.__repr__()+".txt", "w") as text_file:
            text_file.write(str(best_team_overall))
        if CONFIG['advanced_training_parameters']['use_pareto_for_team_population_selection']:
            for team in fronts_per_run[best_run]:
                with open(filepath+"/best_front_"+team.__repr__()+".txt", "w") as text_file:
                    text_file.write(str(team))