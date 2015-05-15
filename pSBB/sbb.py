#!/usr/bin/env python
# encoding: utf-8
## vim:ts=4:et:nowrap

import random
import time
import copy
import numpy
import os
from collections import defaultdict, Counter
from program import Program, reset_programs_ids
from team import Team, reset_teams_ids
from environments.classification_environment import ClassificationEnvironment
from utils.helpers import round_value_to_decimals, round_array_to_decimals
from config import CONFIG, RESTRICTIONS

class SBB:
    def __init__(self):
        self.current_generation = 0
        self.environment = ClassificationEnvironment()

    def run(self):
        best_teams_per_run = []
        elapseds_per_run = []
        actions_per_generation_per_run = []
        # recall_per_generation_per_run = []
        score_per_generations = [0.0] * CONFIG['training_parameters']['generations_total']

        msg = "\nCONFIG: "+str(CONFIG)+"\n"
        msg = self.environment.print_metrics(msg)

        for run_id in range(1, CONFIG['training_parameters']['runs_total']+1):
            actions_counts = []
            # recall_per_generation = []
            best_programs_per_generation = []
            start_per_run = time.time()
            print("\nStarting run: "+str(run_id))       

            # random initialize population
            reset_programs_ids()
            reset_teams_ids()
            programs_population =[]
            for i in range(CONFIG['training_parameters']['populations']['programs']):
                program = Program(generation=0, environment=self.environment, initialization=True)
                programs_population.append(program)

            teams_population = []
            for t in range(CONFIG['training_parameters']['populations']['teams']):
                team = Team(generation=0,  environment=self.environment, programs=programs_population, initialization=True)
                teams_population.append(team)
            self.current_generation = 0
            sample = None
            while not self.stop_criterion():
                self.current_generation += 1
                sample = self.environment.get_sample(previous_samples=sample)
                print("\n>>>>> Executing generation: "+str(self.current_generation)+", run: "+str(run_id))
                teams_population, programs_population = self.selection(teams_population, programs_population, sample)

                fitness = [p.fitness for p in teams_population]
                best_program = teams_population[fitness.index(max(fitness))]
                score, extra_metrics = self.environment.evaluate(best_program, self.environment.test, testset=True)
                best_program.score_testset = score
                best_program.extra_metrics = extra_metrics
                print("Best team: "+best_program.print_metrics())

                best_programs_per_generation.append(best_program)
                # recall_per_generation.append(best_program.recall)
                score_per_generations[self.current_generation-1] += best_program.score_testset
                actions_count = Counter([p.action for p in programs_population])
                actions_counts.append(actions_count.values())
                print "Actions Counter: "+str(actions_count)

            print("\n"+str(run_id)+" Run's best team: "+best_program.print_metrics())
            elapsed_per_run = time.time() - start_per_run
            best_teams_per_run.append(best_program)
            elapseds_per_run.append(elapsed_per_run)
            actions_per_generation_per_run.append(actions_counts)
            # recall_per_generation_per_run.append(recall_per_generation)
            print("\nFinished run execution, elapsed time: "+str(elapsed_per_run)+" secs")

        # Get best run
        best_result_metric = [p.score_testset for p in best_teams_per_run]
        best_run = best_result_metric.index(max(best_result_metric))
        final_best_team = best_teams_per_run[best_run]

        # Generate final outputs
        msg += self.generate_output_messages_per_run(best_teams_per_run)
        msg += self.generate_output_messages_for_best_team(best_run, final_best_team, actions_per_generation_per_run)
        msg += "\n\nFinished execution, total elapsed time: "+str(round_value_to_decimals(sum(elapseds_per_run)))+" secs"
        msg += "\nElapsed times, mean: "+str(round_value_to_decimals(numpy.mean(elapseds_per_run)))+", std: "+str(round_value_to_decimals(numpy.std(elapseds_per_run)))+"\n"
        print msg
        self.write_output_file(final_best_team, msg)

    def stop_criterion(self):
        if self.current_generation == CONFIG['training_parameters']['generations_total']:
            return True
        return False

    def selection(self, teams_population, programs_population, training_data):
        # execute teams to calculate fitness
        for t in teams_population:
            score, extra_metrics = self.environment.evaluate(t, training_data)
            t.fitness = score
            t.score_trainingset = score

        if CONFIG['advanced_training_parameters']['diversity']['genotype_fitness_maintanance']:
            for t in teams_population:
                # create array of distances to other teams
                distances = []
                for other_t in teams_population:
                    if t != other_t:
                        num_programs_intersection = len(set(t.active_programs).intersection(other_t.active_programs))
                        num_programs_union = len(set(t.active_programs).union(other_t.active_programs))
                        if num_programs_union > 0:
                            distance = 1.0 - (float(num_programs_intersection)/float(num_programs_union))
                        else:
                            distance = 1.0
                        distances.append(distance)
                # get mean of the k nearest neighbours
                sorted_list = sorted(distances)
                k = CONFIG['advanced_training_parameters']['diversity']['genotype_fitness_maintanance_configs']['k']
                min_values = sorted_list[:k]
                diversity = numpy.mean(min_values)
                # calculate fitness
                p = CONFIG['advanced_training_parameters']['diversity']['genotype_fitness_maintanance_configs']['p_value']
                raw_fitness = t.fitness
                t.fitness = (1.0-p)*(raw_fitness) + p*diversity

        # 1. Remove worst teams
        teams_to_be_replaced = int(CONFIG['training_parameters']['replacement_rate']['teams']*float(len(teams_population)))
        new_teams_population_len = len(teams_population) - teams_to_be_replaced
        while len(teams_population) > new_teams_population_len:
            fitness = [t.fitness for t in teams_population]
            worst_program_index = fitness.index(min(fitness))
            teams_population[worst_program_index].remove_programs_link()
            teams_population.pop(worst_program_index)

        # 2. Remove programs are not in a team
        to_remove = []
        for p in programs_population:
            if len(p.teams) == 0:
                to_remove.append(p)
        for p in programs_population:
            if p in to_remove:
                programs_population.remove(p)

        # 3. Create new mutated programs
        new_programs_to_create = CONFIG['training_parameters']['populations']['programs'] - len(programs_population)
        new_programs = []
        programs_to_clone = random.sample(programs_population, new_programs_to_create)
        for program in programs_to_clone:
            clone = Program(self.current_generation, self.environment, initialization=False, 
                instructions=copy.deepcopy(program.instructions), action=program.action)
            clone.mutate()
            new_programs.append(clone)

        # 4. Add new teams, cloning the old ones and adding or removing programs (if adding, can only add a new program)
        new_teams_to_create = CONFIG['training_parameters']['populations']['teams'] - len(teams_population)
        teams_to_clone = []
        while len(teams_to_clone) < new_teams_to_create:
            selected = self.weighted_random_choice(teams_population)
            teams_to_clone.append(selected)

        for team in teams_to_clone:
            clone = Team(self.current_generation, self.environment, programs=team.programs, initialization=False)
            clone.mutate(new_programs)
            teams_population.append(clone)

        # 5. Add new programs to population, so it has the same size as before
        for p in new_programs:
            programs_population.append(p)

        return teams_population, programs_population

    def weighted_random_choice(self, chromosomes):
        fitness = [p.fitness for p in chromosomes]
        total = sum(chromosome.fitness for chromosome in chromosomes)
        pick = random.uniform(0, total)
        current = 0
        for chromosome in chromosomes:
            current += chromosome.fitness
            if current > pick:
                return chromosome

    def generate_output_messages_per_run(self, best_teams_per_run):
        msg = ""
        msg += "\n\n################# RESULT PER RUN ####################"
        score_per_run = []
        for run_id in range(CONFIG['training_parameters']['runs_total']):
            best_program = best_teams_per_run[run_id]
            score_per_run.append(round_value_to_decimals(best_program.score_testset))
            msg += "\n"+str(run_id)+" Run best team: "+best_program.print_metrics()+"\n"
        msg += "\n\nTest score per run: "+str(score_per_run)
        msg += "\nTest score, mean: "+str(numpy.mean(score_per_run))+", std: "+str(numpy.std(score_per_run))
        return msg

    def generate_output_messages_for_best_team(self, best_run, final_best_team, actions_per_generation_per_run):
        msg = ""
        msg += "\n\n#################### OVERALL BEST TEAM ####################"
        msg += "\n"+str(best_run)+" Run best team: "+final_best_team.print_metrics()

        # if CONFIG['task'] == 'classification':
        #     msg += "\n\nAcc per classes: "+str(round_array_to_decimals(final_best_team.accuracies_per_class))
        #     msg += "\nConfusion Matrix:\n"+str(final_best_team.conf_matrix)
        #     if CONFIG['verbose']['show_recall_per_action_per_generation']:
        #         temp = [[round_value_to_decimals(x, round_decimals_to = 3) for x in a] for a in recall_per_generation_per_run[best_run]]
        #         msg += "\n\nrecall_per_action_per_generation: "+str(temp)
            
        if CONFIG['verbose']['show_avg_dr_per_generations']:
            score_per_generations = [round_value_to_decimals(x/float(CONFIG['training_parameters']['runs_total']), round_decimals_to = 3) for x in score_per_generations]
            msg += "\n\navg_dr_per_generations: "+str(score_per_generations)

        if CONFIG['verbose']['show_actions_distribution_per_generation']:
            msg += "\n\nActions Distribution (per gen.): "+str(actions_per_generation_per_run[best_run])
        msg += "\n\nActions Distribution (last gen.): "+str(actions_per_generation_per_run[best_run][-1])
        return msg

    def write_output_file(self, final_best_team, msg):
        if not os.path.exists(RESTRICTIONS['working_path']+"outputs/"):
            os.makedirs(RESTRICTIONS['working_path']+"outputs/")
        localtime = time.localtime()
        pretty_localtime = str(localtime.tm_year)+"-"+str(localtime.tm_mon)+"-"+str(localtime.tm_mday)+"-"+str(localtime.tm_hour)+str(localtime.tm_min)+str(localtime.tm_sec)
        text_file = open(RESTRICTIONS['working_path']+"outputs/"+str(CONFIG['classification_parameters']['dataset'])+"_output-"+pretty_localtime+".txt",'w')
        text_file.write(msg+str(final_best_team))
        text_file.close()