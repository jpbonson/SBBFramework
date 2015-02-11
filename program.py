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

def reset_programs_ids():
    global next_program_id
    next_program_id = 0

class Program:
    def __init__(self, generation, total_input_registers, total_classes, random_mode=True, instructions=[]):
        global next_program_id
        next_program_id += 1
        self.program_id = next_program_id
        self.generation = generation
        self.total_input_registers = total_input_registers
        self.total_output_registers = 1
        self.total_general_registers = CONFIG['total_calculation_registers']+self.total_output_registers
        self.action = randint(0, total_classes-1)
        if random_mode:
            self.instructions = []
            for i in range(CONFIG['initial_program_size']):
                self.instructions.append(self.generate_random_instruction())
        else:
            self.instructions = instructions
        self.teams = []

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

    def execute(self, sample, testset=False):
        # execute code for each input
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
                source =  sample[i['source']]
            general_registers[i['target']] = op(general_registers[i['target']], source)
        # get class output
        output = general_registers[0]
        membership_outputs = expit(output) # apply sigmoid function before getting the output class
        return membership_outputs

    def mutate_single_instruction(self):
        index = randint(0, len(self.instructions)-1)
        instruction = self.instructions[index]
        instruction_parameter = randint(0,3)
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

    def mutate_instruction_set(self):
        mutation_type = randint(0,1)
        if len(self.instructions) == CONFIG['minimum_program_size']:
            mutation_type = 1
        if len(self.instructions) == CONFIG['max_program_size']:
            mutation_type = 0
        if mutation_type == 0: # remove random instruction
            index = randint(0, len(self.instructions)-1)
            self.instructions.pop(index)
        else: # add random instruction
            index = randint(0, len(self.instructions))
            self.instructions.insert(index, self.generate_random_instruction())

    def add_team(self, team):
        self.teams.append(team)

    def remove_team(self, team):
        self.teams.remove(team)

    def to_str(self):
        text = "\nCode for program "+str(self.program_id)+" from generation "+str(self.generation)+" for action "+str(self.action)
        teams_ids = ["("+str(t.team_id)+":"+str(t.generation)+")" for t in self.teams]
        text += "\nParticipate in the teams: "+str(teams_ids)
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