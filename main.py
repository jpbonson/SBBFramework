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
from program import Program, reset_programs_ids
from team import Team, reset_teams_ids
from helpers import *
from config import *

class Algorithm:
    def __init__(self, data_name):
        self.data_name = data_name
        self.current_generation = 0

    def run(self):
        best_programs_per_run = []
        best_programs_per_run_per_generation = []
        runs_info = []
        print("\nReading inputs from data: "+self.data_name)
        train, test = read_inputs_already_partitioned(self.data_name)
        normalization_params = self.get_normalization_params(train, test)
        train = self.normalize(normalization_params, train)
        test = self.normalize(normalization_params, test)
        Y_test = get_Y(test)
        class_dist = get_class_distribution(Y_test)
        trainsubsets_per_class = self.get_data_per_class(train, class_dist)
        elapseds_per_run = []
        recall_per_generation_per_run = []
        avg_dr_per_generations = [0.0] * CONFIG['max_generation_total']

        for run_id in range(CONFIG['runs_total']):
            recall_per_generation = []
            best_programs_per_generation = []
            start_per_run = time.time()
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
            info += ("\ntotal_classes: "+str(output_size))
            info += ("\ntotal_registers: "+str(CONFIG['total_calculation_registers']+1))
            print(info)

            # random initialize population
            reset_programs_ids()
            reset_teams_ids()
            programs_population =[]
            sample = self.get_sample(train, trainsubsets_per_class)
            for i in range(CONFIG['program_population_size']):
                program = Program(generation=0, total_input_registers=features_size, total_classes=output_size, random_mode=True)
                programs_population.append(program)
            teams_population = []
            for t in range(CONFIG['team_population_size']):
                team = Team(generation=0, total_input_registers=features_size, total_classes=output_size, random_mode=True, sample_programs=programs_population)
                if not CONFIG['use_diversity']:
                    team.execute(sample)
                teams_population.append(team)
            self.current_generation = 0
            while not self.stop_criterion():
                self.current_generation += 1
                sample = self.get_sample(train, trainsubsets_per_class)
                print("\n>>>>> Executing generation: "+str(self.current_generation)+", run: "+str(run_id))
                teams_population, programs_population = self.selection(teams_population, programs_population, sample)
                fitness = [p.fitness for p in teams_population]
                best_program = teams_population[fitness.index(max(fitness))]
                best_program.execute(test, testset=True) # analisar o melhor individuo gerado com o test set
                print("Best program: "+best_program.print_metrics())
                best_programs_per_generation.append(best_program)
                recall_per_generation.append(best_program.recall)
                avg_dr_per_generations[self.current_generation-1] += best_program.macro_recall_testset
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
            print("\nFinished run execution, elapsed time: "+str(elapsed_per_run)+" secs")

        print("\n################# RESULT PER RUN ####################")
        dr_metric_per_run = []
        acc_metric_per_run = []
        avg_introns = []
        for run_id in range(CONFIG['runs_total']):
            best_program = best_programs_per_run[run_id]
            dr_metric_per_run.append(Operations.round_to_decimals(best_program.macro_recall_testset))
            acc_metric_per_run.append(Operations.round_to_decimals(best_program.accuracy_testset))
            print("\n"+str(run_id)+" Run best program: "+best_program.print_metrics())
            print("Acc per classes: "+str(best_program.accuracies_per_class))
            print("Acc per classes (counter): "+str(best_program.conts_per_class))
            print("Confusion Matrix:\n"+str(best_program.conf_matrix))
            avg_introns.append(best_program.avg_introns())
        
        best_result_metric = [p.macro_recall_testset for p in best_programs_per_run]
        best_run = best_result_metric.index(max(best_result_metric))
        overall_best_program = best_programs_per_run[best_run]
        msg = "\nCONFIG: "+str(CONFIG)+"\n"
        msg += "\n################# Overall Best:\n"+str(best_run)+" Run best program: "+overall_best_program.print_metrics()
        msg += "\n"+runs_info[best_run]

        msg += "\n\nAcc per classes: "+str(overall_best_program.accuracies_per_class)+"\nAcc per classes (counter): "+str(overall_best_program.conts_per_class)
        msg += "\nConfusion Matrix:\n"+str(overall_best_program.conf_matrix)

        # msg += "\n\nTest ACC per run: "+str(acc_metric_per_run)
        # msg += "\nTest ACC, mean: "+str(numpy.mean(acc_metric_per_run))+", std: "+str(numpy.std(acc_metric_per_run))

        msg += "\n\nTest DR per run: "+str(dr_metric_per_run)
        msg += "\nTest DR, mean: "+str(numpy.mean(dr_metric_per_run))+", std: "+str(numpy.std(dr_metric_per_run))
        # msg += "\n\nAvg Introns:, mean: "+str(numpy.mean(avg_introns))+", std: "+str(numpy.std(avg_introns))

        if CONFIG['print_recall_per_generation_for_best_run']:
            temp = [[Operations.round_to_decimals(x, round_decimals_to = 3) for x in a] for a in recall_per_generation_per_run[best_run]]
            msg += "\n\nrecall_per_generation: "+str(temp)
        
        avg_dr_per_generations = [Operations.round_to_decimals(x/float(CONFIG['runs_total']), round_decimals_to = 3) for x in avg_dr_per_generations]
        msg += "\n\navg_dr_per_generations: "+str(avg_dr_per_generations)

        print(msg)

        elapsed_msg = "\nFinished execution, total elapsed time: "+str(sum(elapseds_per_run))+" secs"
        elapsed_msg += "\nElapsed times, mean: "+str(numpy.mean(elapseds_per_run))+", std: "+str(numpy.std(elapseds_per_run))
        print(elapsed_msg)

        localtime = time.localtime()
        pretty_localtime = str(localtime.tm_year)+"-"+str(localtime.tm_mon)+"-"+str(localtime.tm_mday)+"-"+str(localtime.tm_hour)+str(localtime.tm_min)+str(localtime.tm_sec)
        text_file = open(CURRENT_DIR+"best_program_codes/"+str(self.data_name)+"_best_program_code-"+pretty_localtime+".txt",'w')
        text_file.write(msg+overall_best_program.to_str()+elapsed_msg)
        text_file.close()

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
        if self.current_generation == CONFIG['max_generation_total']:
            return True
        return False

    def selection(self, teams_population, programs_population, training_data):
        if CONFIG['use_diversity']:
            labels = get_Y(training_data)
            total_hits_per_sample = defaultdict(int)
            for t in teams_population: # execute teams to calculate the total_hits_per_sample and the correct_samples per team
                t.execute(training_data)
                for c in t.correct_samples:
                    total_hits_per_sample[c] += 1
            if CONFIG['diversity']['fitness_sharing']:
                for t in teams_population:
                    sum_per_sample = 0.0
                    for i, l in enumerate(labels):
                        if i in t.correct_samples:
                            sum_per_sample += 1.0/float(total_hits_per_sample[i])
                        else:
                            sum_per_sample += 0.0
                    t.fitness = float(sum_per_sample)/float(len(labels))
            elif CONFIG['diversity']['classwise_fitness_sharing']:
                for t in teams_population:
                    fitness_per_class = []
                    for label in set(labels):
                        sum_per_sample = 0.0
                        cont = 0
                        for i, l in enumerate(labels):
                            if l == label:
                                cont += 1
                                if i in t.correct_samples:
                                    sum_per_sample += 1.0/float(total_hits_per_sample[i])
                                else:
                                    sum_per_sample += 0.0
                        fitness = float(sum_per_sample)/float(cont)
                        fitness_per_class.append(fitness)
                    t.fitness = numpy.mean(fitness_per_class)

        # 1. Remove worst teams
        teams_to_be_replaced = int(CONFIG['replacement_rate']*float(len(teams_population)))
        new_teams_population_len = len(teams_population) - teams_to_be_replaced
        while len(teams_population) > new_teams_population_len:
            fitness = [t.fitness for t in teams_population]
            worst_program_index = fitness.index(min(fitness))
            teams_population[worst_program_index].remove_programs_link()
            teams_population.pop(worst_program_index)

        # 2. Remove programs are are not in a team
        to_remove = []
        for p in programs_population:
            if len(p.teams) == 0:
                to_remove.append(p)
        for p in programs_population:
            if p in to_remove:
                programs_population.remove(p)

        # 3. Create new mutated programs
        new_programs_to_create = CONFIG['program_population_size'] - len(programs_population)
        new_programs = []
        programs_to_clone = random.sample(programs_population, new_programs_to_create)
        for program in programs_to_clone:
            clone = Program(self.current_generation, program.total_input_registers, program.total_output_registers,
                random_mode=False, instructions=copy.deepcopy(program.instructions))
            
            mutations = randint(1, CONFIG['max_mutations_per_program'])
            for i in range(mutations):
                mutation_chance = random.random()
                if mutation_chance <= CONFIG['mutation_instruction_set_rate']:
                    clone.mutate_instruction_set()

            mutations = randint(1, CONFIG['max_mutations_per_program'])
            for i in range(mutations):
                mutation_chance = random.random()
                if mutation_chance <= CONFIG['mutation_single_instruction_rate']:
                    clone.mutate_single_instruction()
            
            new_programs.append(clone)

        # 4. Add new teams, cloning the old ones and adding or removing programs (if adding, can only add a new program)
        new_teams_to_create = CONFIG['team_population_size'] - len(teams_population)
        teams_to_clone = []
        while len(teams_to_clone) < new_teams_to_create:
            selected = self.weighted_random_choice(teams_population)
            if selected not in teams_to_clone:
                teams_to_clone.append(selected)
        for team in teams_to_clone:
            clone = Team(self.current_generation, team.total_input_registers, team.total_classes,
                random_mode=False, sample_programs=team.programs)
            mutation_chance = random.random()
            if mutation_chance <= CONFIG['mutation_team_rate']:
                clone.mutate(new_programs)
            if not CONFIG['use_diversity']:
                clone.execute(training_data)
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

if __name__ == "__main__":
    data = DATA_FILE
    Algorithm(data).run()