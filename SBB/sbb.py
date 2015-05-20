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

        # prepare metrics
        elapseds_per_run = []
        best_teams_per_run = []
        avg_score_per_generations_across_runs = [0.0] * (CONFIG['training_parameters']['generations_total']+1)
        recall_per_generation_per_run = [] # only for classification task

        # initialize environment and selection algorithm
        environment = self._initialize_environment()
        selection = Selection(environment)

        msg = ""
        if CONFIG['advanced_training_parameters']['verbose'] > 0:
            msg += "\n### CONFIG: "+str(CONFIG)+"\n"
            msg += environment.metrics()
            print msg

        for run_id in range(1, CONFIG['training_parameters']['runs_total']+1):
            print("\nStarting run: "+str(run_id))

            start_time = time.time()
            best_teams_per_generation = []
            recall_per_generation = [] # only for classification task

            # 1. Randomly initialize populations
            self.current_generation_ = 0
            programs_population = self._initialize_program_population()
            teams_population = self._initialize_team_population(programs_population)
            
            environment.reset()
            while not self._stop_criterion():
                self.current_generation_ += 1
                print("\n>>>>> Executing generation: "+str(self.current_generation_)+", run: "+str(run_id))
                
                # 2. Selection
                environment.setup()
                teams_population, programs_population = selection.run(self.current_generation_, teams_population, programs_population)

                # prepare and print metrics (per generation)
                best_team = self._best_team(teams_population)
                environment.evaluate(best_team)
                print("best team: "+best_team.metrics())

                if CONFIG['advanced_training_parameters']['verbose'] > 0:
                    print "actions distribution: "+str(Counter([p.action for p in programs_population]))

                best_teams_per_generation.append(best_team)
                avg_score_per_generations_across_runs[self.current_generation_] += best_team.score_testset_
                if CONFIG['task'] == 'classification':
                    recall_per_generation.append(best_team.extra_metrics_['recall_per_action'])

            # prepare and print metrics (per run)
            print("\n"+str(run_id)+" Run's best team: "+best_team.metrics())
            elapsed_time = time.time() - start_time
            elapseds_per_run.append(elapsed_time)
            best_teams_per_run.append(best_team)
            if CONFIG['task'] == 'classification':
                recall_per_generation_per_run.append(recall_per_generation)
            print("\nFinished run "+str(run_id)+", elapsed time: "+str(elapsed_time)+" secs")

        # 3. Finalize execution (get final metrics, print to output, print to file)
        best_team_overall, best_run = self._best_team_overall(best_teams_per_run)
        msg += self._generate_output_messages_for_best_team_per_run(best_teams_per_run)
        msg += self._generate_output_messages_for_best_team_overall(best_run, best_team_overall, recall_per_generation_per_run[best_run], avg_score_per_generations_across_runs)
        msg += "\n\nFinished execution, total elapsed time: "+str(round_value_to_decimals(sum(elapseds_per_run)))+" secs "
        msg += "(mean: "+str(round_value_to_decimals(numpy.mean(elapseds_per_run)))+", std: "+str(round_value_to_decimals(numpy.std(elapseds_per_run)))+")"
        print msg
        self._write_output_file(best_team_overall, msg)

    def _initialize_environment(self):
        if CONFIG['task'] == 'classification':
            return ClassificationEnvironment()
        raise ValueError("No environment exists for "+str(CONFIG['task']))

    def _initialize_program_population(self):
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
                raise StandardError("_get_programs_per_action() wasn't able to get programs for the action "+str(class_index)+". You got a bug.")
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

    def _best_team_overall(self, best_teams_per_run):
        best_result_metric = [p.score_testset_ for p in best_teams_per_run]
        best_run = best_result_metric.index(max(best_result_metric))
        best_team_overall = best_teams_per_run[best_run]
        return best_team_overall, best_run

    def _generate_output_messages_for_best_team_per_run(self, best_teams_per_run):
        msg = "\n\n################# RESULT PER RUN ####################"
        score_per_run = []
        for run_id in range(CONFIG['training_parameters']['runs_total']):
            best_team = best_teams_per_run[run_id]
            score_per_run.append(round_value_to_decimals(best_team.score_testset_))
            msg += "\n"+str(run_id)+" Run best team: "+best_team.metrics()+"\n"
        msg += "\n\nTest score per run: "+str(score_per_run)
        msg += "\nTest score, mean: "+str(numpy.mean(score_per_run))+", std: "+str(numpy.std(score_per_run))
        return msg

    def _generate_output_messages_for_best_team_overall(self, best_run, best_team_overall, recall_per_generation, avg_score_per_generations_across_runs):
        msg = "\n\n#################### OVERALL BEST TEAM ####################"
        msg += "\n"+str(best_run)+" Run best team: "+best_team_overall.metrics()

        if CONFIG['advanced_training_parameters']['verbose'] == 2 and CONFIG['task'] == 'classification':
            msg += "\n\nrecall_per_action_per_generation: "+str(recall_per_generation)
            msg += "\n\naccuracy: "+str(best_team_overall.extra_metrics_['accuracy'])
            msg += "\n\nconfusion matrix:\n"+str(best_team_overall.extra_metrics_['confusion_matrix'])
            
        if CONFIG['advanced_training_parameters']['verbose'] == 2:
            avg_score_per_generations_across_runs = [round_value_to_decimals(x/float(CONFIG['training_parameters']['runs_total'])) for x in avg_score_per_generations_across_runs]
            msg += "\n\navg_avg_score_per_generations_across_runs: "+str(avg_score_per_generations_across_runs)
        return msg

    def _write_output_file(self, best_team_overall, msg):
        if not os.path.exists(RESTRICTIONS['working_path']+"outputs/"):
            os.makedirs(RESTRICTIONS['working_path']+"outputs/")
        localtime = time.localtime()
        pretty_localtime = str(localtime.tm_year)+"-"+str(localtime.tm_mon)+"-"+str(localtime.tm_mday)+"-"+str(localtime.tm_hour)+str(localtime.tm_min)+str(localtime.tm_sec)
        text_file = open(RESTRICTIONS['working_path']+"outputs/"+str(CONFIG['classification_parameters']['dataset'])+"_output-"+pretty_localtime+".txt",'w')
        text_file.write(msg+str(best_team_overall))
        text_file.close()