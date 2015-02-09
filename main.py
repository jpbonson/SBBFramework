#!/usr/bin/env python
# encoding: utf-8
## vim:ts=4:et:nowrap

import random
import math
import time
import copy
import numpy
from random import randint
from collections import defaultdict
from scipy.special import expit
from program import Program, reset_ids
from team import Team
from helpers import *
from config import *

class Algorithm:
    def __init__(self, data_name):
        self.data_name = data_name
        self.current_generation = 0

    def run(self):
        start = time.time()
        best_programs_per_run = []
        runs_info = []
        print("\nReading inputs from data: "+self.data_name)
        train, test = read_inputs_already_partitioned(self.data_name)
        normalization_params = self.get_normalization_params(train, test)
        train = self.normalize(normalization_params, train)
        test = self.normalize(normalization_params, test)
        Y_test = get_Y(test)
        class_dist = get_class_distribution(Y_test)
        trainsubsets_per_class = self.get_data_per_class(train, class_dist)

        for run_id in range(CONFIG['runs_total']):
            print("\nStarting run: "+str(run_id))
            info = "\nAlgorithm info:"          
            random.shuffle(train)
            random.shuffle(test)
            features_size = len(train[0])-1
            info += "Class Distributions: "+str(class_dist)+", for a total of "+str(len(Y_test))+" samples"
            output_size = len(class_dist)
            info += ("\ntotal samples (train): "+str(len(train)))
            info += ("\ntotal samples (test): "+str(len(test)))
            info += ("\ntotal_input_registers: "+str(features_size))
            info += ("\ntotal_output_registers: "+str(output_size))
            info += ("\ntotal_general_registers: "+str(CONFIG['total_calculation_registers']+output_size))
            print(info)

            # random initialize population
            reset_ids()
            population =[]
            sample = self.get_sample(train, trainsubsets_per_class)
            for i in range(CONFIG['population_size']):
                program = Program(generation=1, total_input_registers=features_size, total_classes=output_size)
                population.append(program)
            teams = []
            for t in range(CONFIG['team_population_size']):
                team = Team(generation=1, total_input_registers=features_size, total_classes=output_size, sample_programs=population)
                team.execute(sample)
                teams.append(team)
            self.current_generation = 0
            while not self.stop_criterion():
                self.current_generation += 1
                sample = self.get_sample(train, trainsubsets_per_class)
                print("\n>>>>> Executing generation: "+str(self.current_generation)+", run: "+str(run_id))
                teams, population = self.selection(teams, population, sample)
                fitness = [p.fitness for p in teams]
                best_program = teams[fitness.index(max(fitness))]
                best_program.execute(test, testset=True) # analisar o melhor individuo gerado com o test set
                print("Best program: "+best_program.print_metrics())
            print(info)

            print("\nRun's best program: "+best_program.print_metrics())
            best_programs_per_run.append(best_program)
            print("\nFinishing run: "+str(run_id))
            runs_info.append(info)

        print("\n################# RESULT PER RUN ####################")
        test_metrics_per_run = []
        test_accuracy_per_run = []
        for run_id in range(CONFIG['runs_total']):
            best_program = best_programs_per_run[run_id]
            test_accuracy_per_run.append(Operations.round_to_decimals(best_program.accuracy_testset))
            test_metrics_per_run.append(Operations.round_to_decimals(numpy.mean([best_program.accuracy_testset, best_program.macro_recall_testset])))
            print("\n"+str(run_id)+" Run best program: "+best_program.print_metrics())
            print("Acc per classes: "+str(best_program.accuracies_per_class))
            print("Acc per classes (counter): "+str(best_program.conts_per_class))
            print("Confusion Matrix:\n"+str(best_program.conf_matrix))
        
        best_result_metric = [numpy.mean([p.accuracy_testset, p.macro_recall_testset]) for p in best_programs_per_run]
        best_run = best_result_metric.index(max(best_result_metric))
        overall_best_program = best_programs_per_run[best_run]
        msg = "\n################# Overall Best:\n"+str(best_run)+" Run best program: "+overall_best_program.print_metrics()
        msg += "\n"+runs_info[best_run]

        msg += "\n\nAcc per classes: "+str(overall_best_program.accuracies_per_class)+"\nAcc per classes (counter): "+str(overall_best_program.conts_per_class)
        msg += "\nConfusion Matrix:\n"+str(overall_best_program.conf_matrix)

        msg += "\n\nTest Solution Metric per run solution: "+str(test_metrics_per_run)
        print(msg)

        localtime = time.localtime()
        pretty_localtime = str(localtime.tm_year)+"-"+str(localtime.tm_mon)+"-"+str(localtime.tm_mday)+"-"+str(localtime.tm_hour)+str(localtime.tm_min)
        text_file = open(CURRENT_DIR+"best_program_codes/"+str(self.data_name)+"_best_program_code-"+pretty_localtime+".txt",'w')
        text_file.write(msg+overall_best_program.to_str())
        text_file.close()

        end = time.time()
        elapsed = end - start
        print("\nFinished execution, elapsed time: "+str(elapsed)+" secs")

    def get_data_per_class(self, data, class_dist):
        subsets_per_class = []
        for class_index in range(len(class_dist)):
            values = [line for line in data if line[-1]-1 == class_index] # added -1 due to class labels starting at 1
            subsets_per_class.append(values)
        return subsets_per_class

    def get_sample(self, data, subsets_per_class):
        if CONFIG['sampling']['use_sampling']:
            print("Sampling")
            num_samples_per_class = CONFIG['sampling']['sampling_size']/len(subsets_per_class)
            samples_per_class = []
            for subset in subsets_per_class:
                if len(subset) <= num_samples_per_class:
                    sample = subset
                else:
                    sample = random.sample(subset, num_samples_per_class)
                samples_per_class.append(sample)
            sample = sum(samples_per_class, [])
            random.shuffle(sample)
        else:
            sample = data[:100] # just to test the program
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
        normalized_data = [[(cell-normalization_params[i]['mean'])/normalization_params[i]['range'] for i, cell in enumerate(line)] for line in data]
        return normalized_data

    def stop_criterion(self):
        if self.current_generation == CONFIG['max_generation_total']:
            return True
        return False

    def selection(self, teams, population, train): # TODO
        # individuals_to_be_replaced = int(CONFIG['removal_rate']*float(len(population)))
        # new_population_len = len(population) - individuals_to_be_replaced
        # while len(population) > new_population_len:
        #     fitness = [p.fitness for p in population]
        #     worst_program_index = fitness.index(min(fitness))
        #     population.pop(worst_program_index)

        # individuals_to_clone = random.sample(population, individuals_to_be_replaced)
        # for individual in individuals_to_clone:
        #     program = Program(self.current_generation, individual.total_input_registers, individual.total_output_registers,
        #         random=False, instructions=copy.deepcopy(individual.instructions))
        #     mutation_chance = random.random()
        #     if mutation_chance <= CONFIG['mutation_single_instruction_rate']:
        #         program.mutate_single_instruction()
        #     mutation_chance = random.random()
        #     if mutation_chance <= CONFIG['mutation_instruction_set_rate']:
        #         program.mutate_instruction_set()
        #     program.execute(train)
        #     population.append(program)
        return teams, population

if __name__ == "__main__":
    data = "thyroid"
    Algorithm(data).run()