#!/usr/bin/env python
# encoding: utf-8
## vim:ts=4:et:nowrap

import random
import time
import copy
import numpy
import os
from collections import Counter
from program import Program, reset_programs_ids
from team import Team, reset_teams_ids
from instruction import Instruction
from environments.classification_environment import ClassificationEnvironment
from utils.helpers import round_value_to_decimals, weighted_choice
from config import CONFIG, RESTRICTIONS

class SBB:
    def __init__(self):
        self.current_generation_ = 0

    def run(self):
        print "\n### Starting pSBB"

        elapseds_per_run = []
        best_teams_per_run = []
        avg_score_per_generations_across_runs = [0.0] * (CONFIG['training_parameters']['generations_total']+1)
        recall_per_generation_per_run = [] # only for classification task

        environment = self._initialize_environment()

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
                teams_population, programs_population = self._selection(environment, teams_population, programs_population)

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

    def _selection(self, environment, teams_population, programs_population):
        # execute teams to calculate fitness
        for t in teams_population:
            environment.evaluate(t, training=True)

        if CONFIG['advanced_training_parameters']['diversity']['genotype_fitness_maintanance']:
            for t in teams_population:
                # create array of distances to other teams
                distances = []
                for other_t in teams_population:
                    if t != other_t:
                        num_programs_intersection = len(set(t.active_programs_).intersection(other_t.active_programs_))
                        num_programs_union = len(set(t.active_programs_).union(other_t.active_programs_))
                        if num_programs_union > 0:
                            distance = 1.0 - (float(num_programs_intersection)/float(num_programs_union))
                        else:
                            distance = 1.0
                        distances.append(distance)
                # get mean of the k nearest neighbours
                sorted_list = sorted(distances)
                k = CONFIG['advanced_training_parameters']['diversity_configs']['genotype_fitness_maintanance']['k']
                min_values = sorted_list[:k]
                diversity = numpy.mean(min_values)
                # calculate fitness
                p = CONFIG['advanced_training_parameters']['diversity_configs']['genotype_fitness_maintanance']['p_value']
                raw_fitness = t.fitness_
                t.fitness = (1.0-p)*(raw_fitness) + p*diversity

        # 1. Remove worst teams
        teams_to_be_replaced = int(CONFIG['training_parameters']['replacement_rate']['teams']*float(len(teams_population)))
        new_teams_population_len = len(teams_population) - teams_to_be_replaced
        while len(teams_population) > new_teams_population_len:
            fitness = [t.fitness_ for t in teams_population]
            worst_team_index = fitness.index(min(fitness))
            worst_team = teams_population[worst_team_index]
            worst_team.remove_references()
            teams_population.remove(worst_team)

        # 2. Remove programs are not in a team
        to_remove = []
        for p in programs_population:
            if len(p.teams_) == 0:
                to_remove.append(p)
        for p in programs_population:
            if p in to_remove:
                programs_population.remove(p)

        # 3. Create new mutated programs
        new_programs_to_create = CONFIG['training_parameters']['populations']['programs'] - len(programs_population)
        new_programs = []
        programs_to_clone = random.sample(programs_population, new_programs_to_create)
        for program in programs_to_clone:
            clone = Program(self.current_generation_, copy.deepcopy(program.instructions), program.action)
            clone.mutate()
            new_programs.append(clone)

        # 4. Add new teams, cloning the old ones and adding or removing programs (if adding, can only add a new program)
        new_teams_to_create = CONFIG['training_parameters']['populations']['teams'] - len(teams_population)
        teams_to_clone = []
        while len(teams_to_clone) < new_teams_to_create:
            fitness = [team.fitness_ for team in teams_population]
            index = weighted_choice(fitness)
            teams_to_clone.append(teams_population[index])

        for team in teams_to_clone:
            clone = Team(self.current_generation_, team.programs)
            clone.mutate(new_programs)
            teams_population.append(clone)

        # 5. Add new programs to population, so it has the same size as before
        for p in new_programs:
            programs_population.append(p)

        return teams_population, programs_population

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