#!/usr/bin/env python
# encoding: utf-8
## vim:ts=4:et:nowrap

import random
import math
import time
from random import randint
from collections import defaultdict
from scipy.special import expit
from program import Program, reset_ids
from helpers import *
from config import *

class Algorithm:
    def __init__(self, population_size = 5000, max_generation_total = 250, use_proportional_selection = True,
            crossover_rate = 0.9, mutation_rate = 0.9, runs_total = 30, initial_program_size = 128, max_program_size = 256,
            total_calculation_registers = 2, use_preselected_train_test_partitions=False):
        self.population_size = population_size
        self.max_generation_total = max_generation_total
        self.use_proportional_selection = use_proportional_selection # if False, use steady tournament
        self.crossover_rate = crossover_rate # report: used only by the proportional selection
        self.mutation_rate = mutation_rate # report: a bit lower than in the paper, since very few individuals are changed per generation
        self.runs_total = runs_total
        self.initial_program_size = initial_program_size # instructions
        self.max_program_size = max_program_size # instructions
        self.total_calculation_registers = total_calculation_registers
        self.use_preselected_train_test_partitions = use_preselected_train_test_partitions
        self.current_generation = 0

    def run(self, data_file):
        start = time.time()
        best_programs_per_run = []
        runs_info = []
        for run_id in range(self.runs_total):
            print("\nStarting run: "+str(run_id))
            print("\nReading inputs from file "+data_file)
            if self.use_preselected_train_test_partitions: # thyroid and shuttle data
                X_train, Y_train, X_test, Y_test = read_inputs_already_partitioned(data_file)
            else: # iris and tic-tac-toe data
                X, Y, input_mapping, output_mapping = read_inputs(data_file)
                features_size = len(X[0])
                output_size = len(output_mapping)
                info = "\nAlgorithm info:"
                info += ("\ntotal_input_registers: "+str(features_size))
                info += ("\ntotal_output_registers: "+str(output_size))
                info += ("\ntotal_general_registers: "+str(self.total_calculation_registers+output_size))
                info += ("\nInput Mapping: "+str(input_mapping))
                info += ("\nOutput Mapping: "+str(output_mapping))
                if self.use_proportional_selection:
                    info += ("\nSelection: Proportional Selection")
                else:
                    info += ("\nSelection: Steady Tournament Selection")
                print(info)

                X_train, Y_train, X_test, Y_test = split_for_crossvalidation(X, Y, 0.2)

            # random initialize population
            reset_ids()
            population =[]
            for i in range(self.population_size):
                program = Program(generation=1, total_input_registers=features_size, total_output_registers=output_size, 
                    total_general_registers = self.total_calculation_registers+output_size, max_program_size=self.max_program_size,
                    initial_program_size = self.initial_program_size)
                program.execute(X_train, Y_train)
                population.append(program)
            self.current_generation = 0
            training_fitness = []
            training_accuracy = []
            test_accuracy = []
            while not self.stop_criterion():
                self.current_generation += 1
                print("\n>>>>> Executing generation: "+str(self.current_generation)+", run: "+str(run_id))
                population = self.selection(population, X_train, Y_train)
                fitness = [p.fitness for p in population]
                best_program = population[fitness.index(max(fitness))]
                training_fitness.append(best_program.fitness)
                training_accuracy.append(best_program.accuracy_trainingset)
                best_program.execute(X_test, Y_test, testset=True) # analisar o melhor individuo gerado com o test set
                test_accuracy.append(best_program.accuracy_testset)
                print("Best program: "+str(best_program.program_id)+":"+str(best_program.generation)+", fitness: "+str(round_to_decimals(best_program.fitness))+", accuracy-trainingset: "+str(round_to_decimals(best_program.accuracy_trainingset))+", accuracy-testset: "+str(round_to_decimals(best_program.accuracy_testset))+", len: "+str(len(best_program.instructions)))
            # info += ("\nTraining fitness: "+str(training_fitness))
            # info += ("\nTraining accuracy: "+str(training_accuracy))
            # info += ("\nTest accuracy: "+str(test_accuracy))
            print(info)

            print("\nRun's best program: "+str(best_program.program_id)+":"+str(best_program.generation)+", fitness: "+str(best_program.fitness)+", accuracy-trainingset: "+str(best_program.accuracy_trainingset)+", accuracy-testset: "+str(best_program.accuracy_testset)+", len: "+str(len(best_program.instructions)))
            best_programs_per_run.append(best_program)
            print("\nFinishing run: "+str(run_id))
            runs_info.append(info)

        print("\n################# RESULT PER RUN ####################")
        test_accuracy_per_run = []
        for run_id in range(self.runs_total):
            best_program = best_programs_per_run[run_id]
            test_accuracy_per_run.append(round_to_decimals(best_program.accuracy_testset))
            print("\n"+str(run_id)+" Run best program: "+str(best_program.program_id)+":"+str(best_program.generation)+", fitness: "+str(best_program.fitness)+", accuracy-trainingset: "+str(best_program.accuracy_trainingset)+", accuracy-testset: "+str(best_program.accuracy_testset)+", len: "+str(len(best_program.instructions)))
        
        accuracy_testset = [p.accuracy_testset for p in best_programs_per_run]
        best_run = accuracy_testset.index(max(accuracy_testset))
        overall_best_program = best_programs_per_run[best_run]
        msg = "\n################# Overall Best:\n"+str(best_run)+" Run best program: "+str(overall_best_program.program_id)+":"+str(overall_best_program.generation)+", fitness: "+str(overall_best_program.fitness)+", accuracy-trainingset: "+str(overall_best_program.accuracy_trainingset)+", accuracy-testset: "+str(overall_best_program.accuracy_testset)+", len: "+str(len(overall_best_program.instructions))
        msg += "\n"+runs_info[best_run]
        msg += "\nAcc per classes: "+str(overall_best_program.accuracies_per_class_0)+", "+str(overall_best_program.accuracies_per_class_1)+", "+str(overall_best_program.accuracies_per_class_2)
        msg += "\n\nTest Accuracies per run solution: "+str(test_accuracy_per_run)
        print(msg)

        localtime = time.localtime()
        pretty_localtime = str(localtime.tm_year)+"-"+str(localtime.tm_mon)+"-"+str(localtime.tm_mday)+"-"+str(localtime.tm_hour)+str(localtime.tm_min)
        text_file = open(CURRENT_DIR+"best_program_codes/best_program_code-"+pretty_localtime+".txt",'w')
        text_file.write(msg+overall_best_program.to_str())
        text_file.close()

        end = time.time()
        elapsed = end - start
        print("\nFinished execution, elapsed time: "+str(elapsed)+" secs")

    def stop_criterion(self):
        if self.current_generation == self.max_generation_total:
            return True
        return False

    def selection(self, population, X_train, Y_train):
        if self.use_proportional_selection:
            return self.proportional_selection(population, X_train, Y_train)
        else:
            return self.steady_tournament_selection(population, X_train, Y_train)

    def proportional_selection(self, population, X_train, Y_train): #TODO
        # 1. get individuals based on the crossover rate with proportional probability
        participants_num = int(self.crossover_rate*float(len(population)))
        if participants_num%2 != 0:
            participants_num += 1
        if DEBUG_PROGRAM_PROPORTIONAL_SELECTION: print("participants_num: "+str(participants_num))
        participants = []
        while len(participants) < participants_num:
            if DEBUG_PROGRAM_PROPORTIONAL_SELECTION: print("participants_len: "+str(len(participants)))
            selected = self.weighted_random_choice(population)
            if DEBUG_PROGRAM_PROPORTIONAL_SELECTION: print("selected: "+str(selected.program_id))
            if selected not in participants:
                participants.append(selected)
        if DEBUG_PROGRAM_PROPORTIONAL_SELECTION: print("participants: "+str([p.program_id for p in participants]))

        # 2. apply crossover and mutation to each pair
        iterable = iter(participants)
        pairs = zip(iterable, iterable)
        offsprings = []
        for p1, p2 in pairs:
            if DEBUG_PROGRAM_PROPORTIONAL_SELECTION: print("pairs: "+str(p1.program_id)+", "+str(p2.program_id))
            offspring1, offspring2 = self.apply_operators(p1, p2, X_train, Y_train)
            offsprings.append(offspring1)
            offsprings.append(offspring2)
        if DEBUG_PROGRAM_PROPORTIONAL_SELECTION: print("offsprings: "+str([p.program_id for p in offsprings]))

        # 3. replace worst individuals by offspring(REPORT: the replacement occur consiring population+offspring)
        if DEBUG_PROGRAM_PROPORTIONAL_SELECTION: print("population_len: "+str(len(population)))
        population += offsprings
        if DEBUG_PROGRAM_PROPORTIONAL_SELECTION: print("population_len: "+str(len(population)))
        removed = 0
        while removed < participants_num:
            fitness = [p.fitness for p in population]
            worst_index = fitness.index(min(fitness))
            if DEBUG_PROGRAM_PROPORTIONAL_SELECTION: print("removed: "+str(population[worst_index].program_id))
            population.pop(worst_index)
            removed += 1
        if DEBUG_PROGRAM_PROPORTIONAL_SELECTION: print("population_len: "+str(len(population)))

        return population

    def weighted_random_choice(self, chromosomes):
        fitness = [p.fitness for p in chromosomes]
        if DEBUG_PROGRAM_PROPORTIONAL_SELECTION: print("fitness: "+str(fitness))
        total = sum(chromosome.fitness for chromosome in chromosomes)
        if DEBUG_PROGRAM_PROPORTIONAL_SELECTION: print("total: "+str(total))
        pick = random.uniform(0, total)
        if DEBUG_PROGRAM_PROPORTIONAL_SELECTION: print("pick: "+str(pick))
        current = 0
        for chromosome in chromosomes:
            current += chromosome.fitness
            if current > pick:
                return chromosome

    def steady_tournament_selection(self, population, X_train, Y_train):
        # 1. Choose FOUR individuals with uniform probability from the population (these are the members of the tournament).
        if DEBUG_PROGRAM_STEADY_TOURNAMENT: print("Choosing programs participants")
        participants = []
        while len(participants) < 4:
            candidate = population[randint(0,len(population)-1)]
            if candidate not in participants:
                participants.append(candidate)
        if DEBUG_PROGRAM_STEADY_TOURNAMENT: print("Choosen programs: "+str([x.program_id for x in participants]))

        # 2. Get the fitness of each individual participating in the tournament.
        if DEBUG_PROGRAM_STEADY_TOURNAMENT: print("Executing programs")
        fitness = [p.fitness for p in participants]
        for p in participants:
            if DEBUG_PROGRAM_STEADY_TOURNAMENT:  print("Fitness "+str(p.program_id)+":"+str(p.generation)+" = "+str(p.fitness))

        # 3. Select the two best ones.
        winner1_index = fitness.index(max(fitness))
        fitness[winner1_index] = -1
        winner2_index = fitness.index(max(fitness))
        winner1 = participants[winner1_index]
        winner2 = participants[winner2_index]
        if DEBUG_PROGRAM_STEADY_TOURNAMENT:  print("Winners: "+str(winner1.program_id)+":"+str(winner1.generation)+" and "+str(winner2.program_id)+":"+str(winner2.generation))

        # 4. Apply the variation operators to the best individuals from the tournament.
        offspring1, offspring2 = self.apply_operators(winner1, winner2, X_train, Y_train)

        # 5. Replace the worst TWO individuals from the tournament with the children from step 3 (thus updating the population).
        participants.remove(winner1)
        participants.remove(winner2)
        if DEBUG_PROGRAM_STEADY_TOURNAMENT:  print("Losers: "+str(participants[0].program_id)+":"+str(participants[0].generation)+" and "+str(participants[1].program_id)+":"+str(participants[1].generation))
        population.remove(participants[0])
        population.remove(participants[1])
        population.append(offspring1)
        population.append(offspring2)
        return population

    def apply_operators(self, winner1, winner2, X_train, Y_train):
        offspring1, offspring2 = winner1.crossover(winner2, self.current_generation)
        mutation_chance = random.random()
        if mutation_chance <= self.mutation_rate:
            if DEBUG_PROGRAM_STEADY_TOURNAMENT:  print("Mutating first offspring")
            offspring1.mutate()
        mutation_chance = random.random()
        if mutation_chance <= self.mutation_rate:
            if DEBUG_PROGRAM_STEADY_TOURNAMENT:  print("Mutating second offspring")
            offspring2.mutate()
        offspring1.execute(X_train, Y_train) # calculate fitness
        offspring2.execute(X_train, Y_train) # calculate fitness
        return offspring1, offspring2

# REPORT: testar com e sem o MDE
if __name__ == "__main__":
    a = Algorithm(population_size = 200, max_generation_total = 20, use_proportional_selection = True,
            crossover_rate = 0.1, mutation_rate = 0.9, runs_total = 10, initial_program_size = 32, 
            max_program_size = 64, total_calculation_registers=2, use_preselected_train_test_partitions=False)
    a.run(CURRENT_DIR+"data/iris.data")
