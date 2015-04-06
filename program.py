#!/usr/bin/env python
# encoding: utf-8
## vim:ts=4:et:nowrap

import random
import math
import time
import numpy
import copy
from random import randint
from collections import defaultdict
from scipy.special import expit
from sklearn.metrics import confusion_matrix, accuracy_score, recall_score
from helpers import *
from config import *

def reset_programs_ids():
    global next_program_id
    next_program_id = 0

if CONFIG['use_complex_functions']:
    GENOTYPE_OPTIONS = {
        'modes': ['read-register', 'read-input'],
        'op': ['+', '-', '*', '/', 'ln', 'exp', 'cos', 'if_lesser_than', 'if_equal_or_higher_than'],
        'one-operand-instructions': ['ln', 'exp', 'cos'],
        'if-instructions': ['if_lesser_than', 'if_equal_or_higher_than'],
    }
else:
    GENOTYPE_OPTIONS = {
        'modes': ['read-register', 'read-input'],
        'op': ['+', '-', '*', '/'],
        'one-operand-instructions': [],
        'if-instructions': [],
    }

class Program:
    def __init__(self, generation, total_input_registers, total_classes, random_mode=True, instructions=[], action=-1):
        global next_program_id
        next_program_id += 1
        self.program_id = next_program_id
        self.generation = generation
        self.total_input_registers = total_input_registers
        self.total_output_registers = 1
        self.total_general_registers = CONFIG['total_calculation_registers']+self.total_output_registers
        self.total_classes = total_classes
        if random_mode:
            self.action = randint(0, self.total_classes-1)
            self.instructions = []
            for i in range(CONFIG['initial_program_size']):
                self.instructions.append(self.generate_random_instruction())
        else:
            self.action = action
            self.instructions = instructions
        self.teams = []
        self.instructions_without_introns = []

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
        if CONFIG['remove_introns']:
            if len(self.instructions_without_introns) == 0:
                self.remove_introns()
            instructions = self.instructions_without_introns
        else:
            instructions = self.instructions
        
        # execute code for each input
        general_registers = [0] * self.total_general_registers
        if_conditional = None
        skip_next = False
        for i in instructions:
            if if_conditional:
                if if_conditional['op'] == 'if_lesser_than':
                    if not (if_conditional['target'] < if_conditional['source']):
                        if_conditional = None
                        if i['op'] in GENOTYPE_OPTIONS['if-instructions']:
                            skip_next = True
                        continue
                if if_conditional['op'] == 'if_equal_or_higher_than':
                    if not (if_conditional['target'] >= if_conditional['source']):
                        if_conditional = None
                        if i['op'] in GENOTYPE_OPTIONS['if-instructions']:
                            skip_next = True
                        continue
                if_conditional = None
            if skip_next:
                if i['op'] in GENOTYPE_OPTIONS['if-instructions']:
                    skip_next = True
                else:
                    skip_next = False
                continue
            if i['op'] == '+':
                op = Operations.sum
            elif i['op'] == '-':
                op = Operations.minus
            elif i['op'] == '*':
                op = Operations.multi
            elif i['op'] == '/':
                op = Operations.div
            elif i['op'] == 'ln':
                op = Operations.ln
            elif i['op'] == 'exp':
                op = Operations.exp
            elif i['op'] == 'cos':
                op = Operations.cos
            elif i['op'] in GENOTYPE_OPTIONS['if-instructions']:
                if_conditional = i
                continue
            if i['op'] in GENOTYPE_OPTIONS['one-operand-instructions']:
                general_registers[i['target']] = op(general_registers[i['target']])
            else:
                if i['mode'] == 'read-register':
                    source =  general_registers[i['source']]
                else:
                    source =  sample[i['source']]
                general_registers[i['target']] = op(general_registers[i['target']], source)
        # get class output
        output = general_registers[0]
        membership_outputs = expit(output) # apply sigmoid function before getting the output class
        return membership_outputs

    def remove_introns(self):
        self.instructions_without_introns = []
        relevant_registers = [0]
        ignore_if = False
        for i, instruction in enumerate(reversed(self.instructions)):
            if instruction['target'] in relevant_registers:
                if instruction['op'] in GENOTYPE_OPTIONS['one-operand-instructions']:
                    if ignore_if or i == 0:
                        continue
                else:
                    ignore_if = False
                    self.instructions_without_introns.insert(0, instruction)
                    if instruction['mode'] == 'read-register' and instruction['source'] not in relevant_registers:
                        relevant_registers.append(instruction['source'])
            else:
                ignore_if = True

    def mutate(self):
        mutation_chance = random.random()
        if mutation_chance <= CONFIG['mutation_program_remove_instruction_rate'] and len(self.instructions) > CONFIG['minimum_program_size']:
            index = randint(0, len(self.instructions)-1)
            self.instructions.pop(index)
        mutation_chance = random.random()
        if mutation_chance <= CONFIG['mutation_program_add_instruction_rate'] and len(self.instructions) < CONFIG['max_program_size']:
            index = randint(0, len(self.instructions))
            self.instructions.insert(index, self.generate_random_instruction())
        mutation_chance = random.random()
        if mutation_chance <= CONFIG['mutation_program_single_instruction_rate']:
            self.mutate_single_instruction()
        mutation_chance = random.random()
        if mutation_chance <= CONFIG['mutation_program_action_rate']:
            self.action = randint(0, self.total_classes-1)

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

    def add_team(self, team):
        self.teams.append(team)

    def remove_team(self, team):
        self.teams.remove(team)

    def to_str(self):
        text = "\nCode for program "+str(self.program_id)+" from generation "+str(self.generation)+" for action "+str(self.action)
        teams_ids = ["("+str(t.team_id)+":"+str(t.generation)+")" for t in self.teams]
        text += "\nParticipate in the teams ("+str(len(teams_ids))+"): "+str(teams_ids)
        text += "\nTotal instructions: "+str(len(self.instructions))+", total introns: "+str(len(self.instructions)-len(self.instructions_without_introns))
        text += "\n----------------"
        for i in self.instructions:
            if i['op'] in GENOTYPE_OPTIONS['one-operand-instructions']:
                text += "\n"+self.one_op_instruction_to_str(i)
            elif i['op'] in GENOTYPE_OPTIONS['if-instructions']:
                text += "\n"+self.if_op_instruction_to_str(i)
            else:
                text += "\n"+self.two_ops_instruction_to_str(i)
        text += "\n----------------"
        text += "\nTotal instructions (without introns): "+str(len(self.instructions_without_introns))
        text += "\n----------------"
        for i in self.instructions_without_introns:
            if i['op'] in GENOTYPE_OPTIONS['one-operand-instructions']:
                text += "\n"+self.one_op_instruction_to_str(i)
            elif i['op'] in GENOTYPE_OPTIONS['if-instructions']:
                text += "\n"+self.if_op_instruction_to_str(i)
            else:
                text += "\n"+self.two_ops_instruction_to_str(i)
        text += "\n----------------"
        return text

    def one_op_instruction_to_str(self, i):
        return "r["+str(i['target'])+"] = "+i['op']+"(r["+str(i['target'])+"])"

    def if_op_instruction_to_str(self, i):
        if i['op'] == 'if_lesser_than':
            return "if r["+str(i['target'])+"] < r["+str(i['source'])+"]:"
        else:
            return "if r["+str(i['target'])+"] >= r["+str(i['source'])+"]:"

    def two_ops_instruction_to_str(self, i):
        instruction_text = "r["+str(i['target'])+"] = r["+str(i['target'])+"] "+i['op']+" "
        if i['mode'] == 'read-register':
            instruction_text += "r["+str(i['source'])+"]"
        else:
            instruction_text += "i["+str(i['source'])+"]"
        return instruction_text