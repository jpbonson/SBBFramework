#!/usr/bin/env python
# encoding: utf-8
## vim:ts=4:et:nowrap

import random
import math
import time
import copy
import numpy
import os
from random import randint
from collections import defaultdict
from collections import Counter
from program import Program, reset_programs_ids
from team import Team, reset_teams_ids
from utils.helpers import *
from config import *

class SBB:
    def __init__(self):
        self.current_generation = 0
        self.output_size = -1

    def run(self):
        best_programs_per_run = []
        best_programs_per_run_per_generation = []
        runs_info = []
        print("\nReading inputs from data: "+CONFIG['classification_parameters']['dataset'])
        train, test = read_inputs_already_partitioned(CONFIG['classification_parameters']['dataset'])
        normalization_params = self.get_normalization_params(train, test)
        train = self.normalize(normalization_params, train)
        test = self.normalize(normalization_params, test)
        Y_test = get_Y(test)
        class_dist = get_class_distribution(Y_test)
        self.output_size = len(class_dist)
        trainsubsets_per_class = self.get_data_per_class(train)
        elapseds_per_run = []
        actions_counts_per_run = []
        actions_counts_per_generation_per_run = []
        recall_per_generation_per_run = []
        avg_dr_per_generations = [0.0] * CONFIG['training_parameters']['generations_total']

        for run_id in range(1, CONFIG['training_parameters']['runs_total']+1):
            actions_counts = []
            recall_per_generation = []
            best_programs_per_generation = []
            start_per_run = time.time()
            print("\nStarting run: "+str(run_id))
            info = "\nAlgorithm info:"          
            random.shuffle(train)
            random.shuffle(test)
            features_size = len(train[0])-1
            info += "\nClass Distributions (test dataset): "+str(class_dist)+", for a total of "+str(len(Y_test))+" samples"
            info += ("\ntotal samples (train): "+str(len(train)))
            info += ("\ntotal samples (test): "+str(len(test)))
            info += ("\ntotal_input_registers: "+str(features_size))
            info += ("\ntotal_classes: "+str(self.output_size))
            print(info)

            # random initialize population
            reset_programs_ids()
            reset_teams_ids()
            programs_population =[]
            for i in range(CONFIG['training_parameters']['populations']['programs']):
                program = Program(generation=0, total_input_registers=features_size, total_classes=self.output_size, 
                    initialization=True)
                programs_population.append(program)

            programs_per_class = self.get_programs_per_class(programs_population)

            teams_population = []
            for t in range(CONFIG['training_parameters']['populations']['teams']):
                team = Team(generation=0, total_input_registers=features_size, total_classes=self.output_size, 
                    programs=programs_per_class, initialization=True)
                teams_population.append(team)
            self.current_generation = 0
            sample = None
            while not self.stop_criterion():
                self.current_generation += 1
                sample = self.get_sample(trainsubsets_per_class, previous_samples=sample)
                print("\n>>>>> Executing generation: "+str(self.current_generation)+", run: "+str(run_id))
                teams_population, programs_population = self.selection(teams_population, programs_population, sample)
                fitness = [p.fitness for p in teams_population]
                best_program = teams_population[fitness.index(max(fitness))]
                best_program.execute(test, testset=True) # analisar o melhor individuo gerado com o test set
                print("Best program: "+best_program.print_metrics())
                best_programs_per_generation.append(best_program)
                recall_per_generation.append(best_program.recall)
                avg_dr_per_generations[self.current_generation-1] += best_program.macro_recall_testset
                actions_count = Counter([p.action for p in programs_population])
                actions_counts.append(actions_count.values())
                print "Actions Counter: "+str(actions_count)
            print(info)

            print("\nRun's best program: "+best_program.print_metrics())
            best_programs_per_run.append(best_program)
            print("\nFinishing run: "+str(run_id))
            runs_info.append(info)
            end_per_run = time.time()
            elapsed_per_run = end_per_run - start_per_run
            elapseds_per_run.append(elapsed_per_run)
            best_programs_per_run_per_generation.append(best_programs_per_generation)
            recall_per_generation_per_run.append(recall_per_generation)
            actions_counts_per_run.append(actions_count)
            actions_counts_per_generation_per_run.append(actions_counts)
            print("\nFinished run execution, elapsed time: "+str(elapsed_per_run)+" secs")

        print("\n################# RESULT PER RUN ####################")
        dr_metric_per_run = []
        for run_id in range(CONFIG['training_parameters']['runs_total']):
            best_program = best_programs_per_run[run_id]
            dr_metric_per_run.append(Operations.round_to_decimals(best_program.macro_recall_testset))
            print("\n"+str(run_id)+" Run best program: "+best_program.print_metrics())
        
        best_result_metric = [p.macro_recall_testset for p in best_programs_per_run]
        best_run = best_result_metric.index(max(best_result_metric))
        overall_best_program = best_programs_per_run[best_run]
        msg = "\nCONFIG: "+str(CONFIG)+"\n"
        msg += "\n################# Overall Best:\n"+str(best_run)+" Run best program: "+overall_best_program.print_metrics()
        msg += "\n"+runs_info[best_run]

        msg += "\n\nAcc per classes: "+str(overall_best_program.accuracies_per_class)
        msg += "\nConfusion Matrix:\n"+str(overall_best_program.conf_matrix)

        msg += "\n\nTest DR per run: "+str(dr_metric_per_run)
        msg += "\nTest DR, mean: "+str(numpy.mean(dr_metric_per_run))+", std: "+str(numpy.std(dr_metric_per_run))

        temp = [[Operations.round_to_decimals(x, round_decimals_to = 3) for x in a] for a in recall_per_generation_per_run[best_run]]
        msg += "\n\nrecall_per_generation: "+str(temp)
        
        avg_dr_per_generations = [Operations.round_to_decimals(x/float(CONFIG['training_parameters']['runs_total']), round_decimals_to = 3) for x in avg_dr_per_generations]
        msg += "\n\navg_dr_per_generations: "+str(avg_dr_per_generations)

        if CONFIG['verbose']['show_actions_distribution_per_generation']:
            msg += "\n\nActions Distribution (per gen.): "+str(actions_counts_per_generation_per_run[best_run])
        msg += "\nActions Distribution (last gen.): "+str(actions_counts_per_run[best_run])

        print(msg)

        elapsed_msg = "\nFinished execution, total elapsed time: "+str(sum(elapseds_per_run))+" secs"
        elapsed_msg += "\nElapsed times, mean: "+str(numpy.mean(elapseds_per_run))+", std: "+str(numpy.std(elapseds_per_run))
        print(elapsed_msg)
        msg += elapsed_msg

        if not os.path.exists(WORKING_PATH+"outputs/"):
            os.makedirs(WORKING_PATH+"outputs/")
        localtime = time.localtime()
        pretty_localtime = str(localtime.tm_year)+"-"+str(localtime.tm_mon)+"-"+str(localtime.tm_mday)+"-"+str(localtime.tm_hour)+str(localtime.tm_min)+str(localtime.tm_sec)
        text_file = open(WORKING_PATH+"outputs/"+str(CONFIG['classification_parameters']['dataset'])+"_output-"+pretty_localtime+".txt",'w')
        text_file.write(msg+overall_best_program.to_str())
        text_file.close()

    def get_programs_per_class(self, programs):
        programs_per_class = []
        for class_index in range(self.output_size):
            values = [p for p in programs if p.action == class_index]
            if len(values) == 0:
                print "WARNING! No programs for class "+str(class_index)
                raise Exception
            programs_per_class.append(values)
        return programs_per_class

    def get_data_per_class(self, data):
        subsets_per_class = []
        for class_index in range(self.output_size):
            values = [line for line in data if line[-1]-1 == class_index] # added -1 due to class labels starting at 1 instead of 0
            subsets_per_class.append(values)
        return subsets_per_class

    def get_sample(self, new_subsets_per_class, previous_samples=None):
        print("Sampling")
        num_samples_per_class = CONFIG['training_parameters']['populations']['points']/len(new_subsets_per_class)

        if not previous_samples or CONFIG['training_parameters']['replacement_rate']['points'] == 1.0: # first sampling
            # get samples per class
            samples_per_class = []
            for subset in new_subsets_per_class:
                if len(subset) <= num_samples_per_class:
                    sample = subset
                else:
                    sample = random.sample(subset, num_samples_per_class)
                samples_per_class.append(sample)
        else:
            current_subsets_per_class = self.get_data_per_class(previous_samples)
            num_samples_per_class_to_maintain = int(round(num_samples_per_class*(1.0-CONFIG['training_parameters']['replacement_rate']['points'])))
            num_samples_per_class_to_add = num_samples_per_class - num_samples_per_class_to_maintain

            # obtain the data points that will be maintained
            maintained_subsets_per_class = []
            for subset in current_subsets_per_class:
                maintained_subsets_per_class.append(random.sample(subset, num_samples_per_class_to_maintain))

            # add the new data points
            for i, subset in enumerate(maintained_subsets_per_class):
                if len(new_subsets_per_class[i]) <= num_samples_per_class_to_add:
                    subset += new_subsets_per_class[i]
                else:
                    subset += random.sample(new_subsets_per_class[i], num_samples_per_class_to_add)
            samples_per_class = maintained_subsets_per_class

        # ensure that the sampling is balanced for all classes, using oversampling for the unbalanced ones
        if CONFIG['classification_parameters']['use_oversampling']:
            for sample in samples_per_class:
                while len(sample) < num_samples_per_class:
                    to_sample = num_samples_per_class-len(sample)
                    if to_sample > len(sample):
                        to_sample = len(sample)
                    sample += random.sample(sample, to_sample)

        # join samples per class
        sample = sum(samples_per_class, [])

        random.shuffle(sample)
        return sample

    def get_normalization_params(self, train, test):
        normalization_params = []
        data = numpy.array(train+test)
        attributes_len = len(data[0])
        for index in range(attributes_len-1): # dont get the class' labels column
            column = data[:,index]
            normalization_params.append({'mean':numpy.mean(column), 'range':max(column)-min(column)})
        normalization_params.append({'mean': 0.0, 'range': 1.0}) # default values so the class labels will not change
        return normalization_params

    def normalize(self, normalization_params, data):
        # normalized_data = [[(cell-normalization_params[i]['mean'])/normalization_params[i]['range'] for i, cell in enumerate(line)] for line in data]
        normalized_data = []
        for line in data:
            new_line = []
            for i, cell in enumerate(line):
                if normalization_params[i]['range'] == 0.0:
                    cell = 0.0
                else:
                    cell = (cell-normalization_params[i]['mean'])/normalization_params[i]['range']
                new_line.append(cell)
            normalized_data.append(new_line)
        return normalized_data

    def stop_criterion(self):
        if self.current_generation == CONFIG['training_parameters']['generations_total']:
            return True
        return False

    def selection(self, teams_population, programs_population, training_data):
        labels = get_Y(training_data)
        total_hits_per_sample = defaultdict(int)
        # execute teams to calculate the total_hits_per_sample and the correct_samples per team
        for t in teams_population:
            t.execute(training_data)
            for c in t.correct_samples:
                total_hits_per_sample[c] += 1

        if CONFIG['advanced_training_parameters']['diversity']['fitness_sharing']:
            for t in teams_population:
                sum_per_sample = 0.0
                for i, l in enumerate(labels):
                    if i in t.correct_samples:
                        sum_per_sample += 1.0/float(total_hits_per_sample[i])
                    else:
                        sum_per_sample += 0.0
                t.fitness = float(sum_per_sample)/float(len(labels))
        elif CONFIG['advanced_training_parameters']['diversity']['genotype_fitness_maintanance']:
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
                k = CONFIG['advanced_training_parameters']['diversity']['genotype_configs']['k']
                min_values = sorted_list[:k]
                diversity = numpy.mean(min_values)
                # calculate fitness
                p = CONFIG['advanced_training_parameters']['diversity']['genotype_configs']['p_value']
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
            clone = Program(self.current_generation, program.total_input_registers, program.total_classes,
                initialization=False, instructions=copy.deepcopy(program.instructions), action=program.action)
            clone.mutate()
            new_programs.append(clone)

        # 4. Add new teams, cloning the old ones and adding or removing programs (if adding, can only add a new program)
        new_teams_to_create = CONFIG['training_parameters']['populations']['teams'] - len(teams_population)
        teams_to_clone = []
        while len(teams_to_clone) < new_teams_to_create:
            selected = self.weighted_random_choice(teams_population)
            teams_to_clone.append(selected)

        for team in teams_to_clone:
            clone = Team(self.current_generation, team.total_input_registers, team.total_classes, 
                programs=team.programs, initialization=False)
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