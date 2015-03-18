#!/usr/bin/env python
# encoding: utf-8
## vim:ts=4:et:nowrap

import random
import math
import time
import numpy
from random import randint
from collections import defaultdict
from scipy.special import expit
from sklearn.metrics import confusion_matrix, accuracy_score, recall_score
from helpers import *
from config import *

GENOTYPE_OPTIONS = {
    'modes': ['read-register', 'read-input'],
    'op': ['+', '-', '*', '/'],
}

def reset_ids():
    global next_program_id
    next_program_id = 0

class Program:
    def __init__(self, generation, total_input_registers, total_output_registers, random=True, instructions=[]):
        global next_program_id
        next_program_id += 1
        self.program_id = next_program_id
        self.generation = generation
        self.accuracies_per_class = []
        self.conts_per_class = []
        self.conf_matrix = []
        self.fitness = -1
        self.accuracy_trainingset = 0
        self.accuracy_testset = 0
        self.recall = 0
        self.total_general_registers = CONFIG['total_calculation_registers']+total_output_registers
        self.total_input_registers = total_input_registers
        self.total_output_registers = total_output_registers
        if random:
            self.instructions = []
            for i in range(CONFIG['initial_program_size']):
                self.instructions.append(self.generate_random_instruction())
        else:
            self.instructions = instructions

    def generate_random_instruction(self):
        instruction = {}
        mode = GENOTYPE_OPTIONS['modes'][randint(0, len(GENOTYPE_OPTIONS['modes'])-1)]
        instruction['mode'] = mode
        instruction['target'] = randint(0, self.total_general_registers-1)
        instruction['op'] = GENOTYPE_OPTIONS['op'][randint(0, len(GENOTYPE_OPTIONS['op'])-1)]
        if mode == 'read-register':
            instruction['source'] = randint(0, self.total_general_registers-1)
        else:
            instruction['source'] = randint(0, self.total_input_registers-1)
        return instruction

    def execute(self, data, testset=False):
        # execute code for each input
        outputs = []
        membership_outputs_array = []
        X = get_X(data)
        Y = get_Y(data)
        for x in X:
            # execute
            if DEBUG_PROGRAM_EXECUTION: print(self.to_str())
            if DEBUG_PROGRAM_EXECUTION: print("inputs: "+str(x))
            general_registers = [0] * self.total_general_registers
            for i in self.instructions:
                if i['op'] == '+':
                    op = Operations.sum
                elif i['op'] == '-':
                    op = Operations.minus
                elif i['op'] == '*':
                    op = Operations.multi
                elif i['op'] == '/':
                    op = Operations.div
                if i['mode'] == 'read-register':
                    source =  general_registers[i['source']]
                else:
                    source =  x[i['source']]
                general_registers[i['target']] = op(general_registers[i['target']], source)
            if DEBUG_PROGRAM_EXECUTION: print("partial outputs: "+str(general_registers))
            # get class output
            partial_outputs = general_registers[0:self.total_output_registers] # tinha um +1 aqui antes, why?
            membership_outputs = [expit(k) for k in partial_outputs] # apply sigmoid function before getting the output class
            output_class = membership_outputs.index(max(membership_outputs))
            if DEBUG_PROGRAM_EXECUTION: print("output_class: "+str(output_class)+", output membership values: "+str(membership_outputs))
            membership_outputs_array.append(membership_outputs)
            outputs.append(output_class)
        # calculate fitness and accuracy
        accuracy, macro_recall = self.calculate_performance_metrics(outputs, Y, testset)
        if USE_MSE3:
            fitness = self.calculate_fitness(accuracy, macro_recall, membership_outputs_array)
        elif USE_ACC_MR:
            fitness = self.calculate_fitness_3(accuracy, macro_recall)
        else:
            fitness = accuracy
        if testset:
            self.accuracy_testset = accuracy
            self.macro_recall_testset = macro_recall
        else:
            self.fitness = fitness
            self.accuracy_trainingset = accuracy
            self.macro_recall_trainingset = macro_recall

    def print_metrics(self):
        r = Operations.round_to_decimals
        m = str(self.program_id)+":"+str(self.generation)+", f: "+str(r(self.fitness))+", len: "+str(len(self.instructions))
        m += "\nTRAIN: acc: "+str(r(self.accuracy_trainingset))+", mrecall: "+str(r(self.macro_recall_trainingset))
        m += "\nTEST: acc: "+str(r(self.accuracy_testset))+", mrecall: "+str(r(self.macro_recall_testset))+", final: "+str(r(numpy.mean([self.accuracy_testset, self.macro_recall_testset])))+", recall: "+str(self.recall)
        return m

    def calculate_performance_metrics(self, predicted_outputs, desired_outputs, testset=False):
        conf_matrix = confusion_matrix(desired_outputs, predicted_outputs)
        accuracy = accuracy_score(desired_outputs, predicted_outputs)
        macro_recall = recall_score(desired_outputs, predicted_outputs, average='macro')
        if testset:
            self.conf_matrix = conf_matrix
            self.conts_per_class = [0] * self.total_output_registers
            self.recall = recall_score(desired_outputs, predicted_outputs, average=None)
            for p, d in zip(predicted_outputs, desired_outputs):
                if p == d:
                    self.conts_per_class[d] += 1.0
            self.accuracies_per_class = [x/float(len(predicted_outputs)) for x in self.conts_per_class]
        return accuracy, macro_recall

    def calculate_MSE(self, membership_outputs_array):
        results = []
        for m in membership_outputs_array:
            first_best_membership_result = max(m)
            m.pop(m.index(first_best_membership_result))
            sum_wrong_classes_errors = 0.0
            for item in m:
                sum_wrong_classes_errors += (Operations.minus(item, 0.0)**2)
            wrong_classes_errors = sum_wrong_classes_errors/float(len(m))
            result = ((Operations.minus(first_best_membership_result, 1.0)**2) + wrong_classes_errors)/2.0
            results.append(result)
        MSE = sum(results)/float(len(membership_outputs_array))
        return MSE

    def calculate_fitness(self, accuracy, macro_recall, membership_outputs_array):
        MSE = self.calculate_MSE(membership_outputs_array)
        MCE = accuracy
        fitness = (MSE + 2.0*MCE)/3.0
        return fitness

    def calculate_fitness_3(self, accuracy, macro_recall):
        MCE = accuracy
        fitness = (MCE + macro_recall)/2.0
        return fitness

    def crossover(self, other_program, generation):
        slice_start_point = randint(0, len(self.instructions)-2)
        slice_end_point = randint(slice_start_point+1, len(self.instructions)-1)

        slice_start_point_other = randint(0, len(other_program.instructions)-2)
        slice_end_point_other = randint(slice_start_point_other+1, len(other_program.instructions)-1)
        if DEBUG_PROGRAM_CROSSOVER: print("PROGRAM 1:"+self.to_str())
        if DEBUG_PROGRAM_CROSSOVER: print("PROGRAM 2:"+other_program.to_str())
        if DEBUG_PROGRAM_CROSSOVER: print("Slicing points: ["+str(slice_start_point)+":"+str(slice_end_point)+"] and ["+str(slice_start_point_other)+":"+str(slice_end_point_other)+"]")
        instructions_slice1 = self.instructions[slice_start_point:slice_end_point]
        instructions_slice2 = other_program.instructions[slice_start_point_other:slice_end_point_other]
        if DEBUG_PROGRAM_CROSSOVER: print("SLICE 1:"+str([self.instruction_to_str(x) for x in instructions_slice1]))
        if DEBUG_PROGRAM_CROSSOVER: print("SLICE 2:"+str([self.instruction_to_str(x) for x in instructions_slice2]))
        new_instrutions1 = self.instructions[0:slice_start_point] + instructions_slice2 + self.instructions[slice_end_point:]
        new_instrutions2 = other_program.instructions[0:slice_start_point_other] + instructions_slice1 + other_program.instructions[slice_end_point_other:]
        
        new_instrutions1 = new_instrutions1[0:CONFIG['max_program_size']]
        new_instrutions2 = new_instrutions2[0:CONFIG['max_program_size']]
        if DEBUG_PROGRAM_CROSSOVER: print("new_instrutions 1:"+str([self.instruction_to_str(x) for x in new_instrutions1]))
        if DEBUG_PROGRAM_CROSSOVER: print("new_instrutions 2:"+str([self.instruction_to_str(x) for x in new_instrutions2]))

        offspring1 = Program(generation, self.total_input_registers, self.total_output_registers, random=False, instructions=new_instrutions1)
        offspring2 = Program(generation, self.total_input_registers, self.total_output_registers, random=False, instructions=new_instrutions2)

        if DEBUG_PROGRAM_CROSSOVER: print("PROGRAM 1:"+self.to_str())
        if DEBUG_PROGRAM_CROSSOVER: print("PROGRAM 2:"+other_program.to_str())
        if DEBUG_PROGRAM_CROSSOVER: print("OFFSPRING 1:"+offspring1.to_str())
        if DEBUG_PROGRAM_CROSSOVER: print("OFFSPRING 2:"+offspring2.to_str())
        return offspring1, offspring2

    def mutate(self):
        if DEBUG_PROGRAM_MUTATION: print("PROGRAM BEFORE "+self.to_str())
        index = randint(0, len(self.instructions)-1)
        instruction = self.instructions[index]
        instruction_parameter = randint(0,4)
        if DEBUG_PROGRAM_MUTATION: print("Instruction index "+str(index))
        if DEBUG_PROGRAM_MUTATION: print("Instruction parameter "+str(instruction_parameter))
        if DEBUG_PROGRAM_MUTATION: print("Instruction before: "+str(instruction))
        if instruction_parameter == 0:
            if instruction['mode'] == GENOTYPE_OPTIONS['modes'][0]:
                instruction['mode'] = GENOTYPE_OPTIONS['modes'][1]
            else:
                instruction['mode'] = GENOTYPE_OPTIONS['modes'][0]
        if instruction_parameter == 1:
            instruction['target'] = randint(0, self.total_general_registers-1)
        if instruction_parameter == 2:
            instruction['op'] = GENOTYPE_OPTIONS['op'][randint(0, len(GENOTYPE_OPTIONS['op'])-1)]
        if instruction_parameter == 0 or instruction_parameter == 3:
            if instruction['mode'] == 'read-register':
                instruction['source'] = randint(0, self.total_general_registers-1)
            else:
                instruction['source'] = randint(0, self.total_input_registers-1)
        if DEBUG_PROGRAM_MUTATION: print("Instruction after: "+str(instruction))
        if DEBUG_PROGRAM_MUTATION: print("PROGRAM AFTER "+self.to_str())

    def to_str(self):
        text = "\nCode for program "+str(self.program_id)+" from generation "+str(self.generation)
        text += "\n----------------"
        for i in self.instructions:
            text += "\n"+self.instruction_to_str(i)
        text += "\n----------------"
        return text

    def instruction_to_str(self, i):
        instruction_text = "r["+str(i['target'])+"] = r["+str(i['target'])+"] "+i['op']+" "
        if i['mode'] == 'read-register':
            instruction_text += "r["+str(i['source'])+"]"
        else:
            instruction_text += "i["+str(i['source'])+"]"
        return instruction_text

    def __str__(self):
        return str(self.program_id)+":"+str(self.generation)