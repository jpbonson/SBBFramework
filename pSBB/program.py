import random
import math
import time
import numpy
import copy
from collections import defaultdict
from scipy.special import expit
from sklearn.metrics import confusion_matrix, accuracy_score, recall_score
from utils.helpers import *
from utils.operations import Operation
from config import *

def reset_programs_ids():
    global next_program_id
    next_program_id = 0

def get_program_id():
    global next_program_id
    next_program_id += 1
    return next_program_id

class Program:
    def __init__(self, generation, total_input_registers, total_actions, initialization=True, instructions=[], action=0):
        self.program_id = get_program_id()
        self.generation = generation
        self.total_input_registers = total_input_registers
        self.total_output_registers = 1
        self.total_general_registers = CONFIG['advanced_training_parameters']['extra_registers']+self.total_output_registers
        self.total_actions = total_actions
        if initialization:
            self.action = random.randrange(self.total_actions)
            self.instructions = []
            for i in range(CONFIG['training_parameters']['program_size']['initial']):
                self.instructions.append(self.generate_random_instruction())
        else:
            self.action = action
            self.instructions = instructions
        self.teams = []
        self.instructions_without_introns = None

    def generate_random_instruction(self):
        instruction = {}
        mode = random.choice(RESTRICTIONS['genotype_options']['modes'])
        instruction['mode'] = mode
        instruction['target'] = random.randrange(self.total_general_registers)
        instruction['op'] = random.choice(CONFIG['advanced_training_parameters']['use_operations'])
        if mode == 'read-register':
            instruction['source'] = random.randrange(self.total_general_registers)
        else:
            instruction['source'] = random.randrange(self.total_input_registers)
        return instruction

    def execute(self, sample, testset=False):
        """ Execute code for each input """
        if not self.instructions_without_introns:
            self.instructions_without_introns = self.remove_introns()
        instructions = self.instructions_without_introns
        
        general_registers = [0] * self.total_general_registers
        if_conditional = None
        skip_next = False

        for i in instructions:
            if if_conditional:
                if if_conditional['op'] == 'if_lesser_than':
                    if not (if_conditional['target'] < if_conditional['source']):
                        if_conditional = None
                        if i['op'] in RESTRICTIONS['genotype_options']['if-instructions']:
                            skip_next = True
                        continue
                if if_conditional['op'] == 'if_equal_or_higher_than':
                    if not (if_conditional['target'] >= if_conditional['source']):
                        if_conditional = None
                        if i['op'] in RESTRICTIONS['genotype_options']['if-instructions']:
                            skip_next = True
                        continue
                if_conditional = None
            if skip_next:
                if i['op'] in RESTRICTIONS['genotype_options']['if-instructions']:
                    skip_next = True
                else:
                    skip_next = False
                continue
            
            if i['op'] in RESTRICTIONS['genotype_options']['if-instructions']:
                if_conditional = i
                continue
            elif i['op'] in RESTRICTIONS['genotype_options']['one-operand-instructions']:
                general_registers[i['target']] = Operation.execute(i['op'], general_registers[i['target']])
            else:
                if i['mode'] == 'read-register':
                    source =  general_registers[i['source']]
                else:
                    source =  sample[i['source']]
                general_registers[i['target']] = Operation.execute(i['op'], general_registers[i['target']], source)
        # get class output
        output = general_registers[0]
        membership_outputs = expit(output) # apply sigmoid function before getting the output class # conferir!
        return membership_outputs

    def remove_introns(self): # fazer unit test!
        """ Remove introns (ie. instructions that don't affect the final output) """
        instructions_without_introns = []
        relevant_registers = [0]
        ignore_previous_if = False
        # Run throught the instructions from the last to the first one
        for instruction in reversed(self.instructions):
            if instruction['target'] in relevant_registers:
                if instruction['op'] in RESTRICTIONS['genotype_options']['if-instructions']:
                    if ignore_previous_if:
                        continue
                else:
                    ignore_previous_if = False
                    instructions_without_introns.insert(0, instruction)
                    if instruction['mode'] == 'read-register' and instruction['source'] not in relevant_registers:
                        relevant_registers.append(instruction['source'])
            else:
                ignore_previous_if = True
        return instructions_without_introns

    def mutate(self):
        mutation_chance = random.random()
        if (mutation_chance <= CONFIG['training_parameters']['mutation']['program']['remove_instruction'] and 
                len(self.instructions) > CONFIG['training_parameters']['program_size']['min']):
            self.instructions.remove(random.choice(self.instructions))

        mutation_chance = random.random()
        if (mutation_chance <= CONFIG['training_parameters']['mutation']['program']['add_instruction'] and 
                len(self.instructions) < CONFIG['training_parameters']['program_size']['max']):
            index = random.randrange(len(self.instructions))
            self.instructions.insert(index, self.generate_random_instruction())

        mutation_chance = random.random()
        if mutation_chance <= CONFIG['training_parameters']['mutation']['program']['change_instruction']:
            self.mutate_single_instruction()
        
        mutation_chance = random.random()
        if mutation_chance <= CONFIG['training_parameters']['mutation']['program']['change_action']:
            self.action = random.randrange(self.total_actions)

    def mutate_single_instruction(self):
        instruction = random.choice(self.instructions)
        instruction_parameter = random.randrange(RESTRICTIONS['genotype_options']['instruction_size'])
        if instruction_parameter == 0:
            if instruction['mode'] == RESTRICTIONS['genotype_options']['modes'][0]:
                instruction['mode'] = RESTRICTIONS['genotype_options']['modes'][1]
            else:
                instruction['mode'] = RESTRICTIONS['genotype_options']['modes'][0]
        if instruction_parameter == 1:
            instruction['target'] = random.randrange(self.total_general_registers)
        if instruction_parameter == 2:
            instruction['op'] = random.choice(CONFIG['advanced_training_parameters']['use_operations'])
        if instruction_parameter == 0 or instruction_parameter == 3:
            if instruction['mode'] == 'read-register':
                instruction['source'] = random.randrange(self.total_general_registers)
            else:
                instruction['source'] = random.randrange(self.total_input_registers)

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
            if i['op'] in RESTRICTIONS['genotype_options']['one-operand-instructions']:
                text += "\n"+self.one_op_instruction_to_str(i)
            elif i['op'] in RESTRICTIONS['genotype_options']['if-instructions']:
                text += "\n"+self.if_op_instruction_to_str(i)
            else:
                text += "\n"+self.two_ops_instruction_to_str(i)
        text += "\n----------------"
        text += "\nTotal instructions (without introns): "+str(len(self.instructions_without_introns))
        text += "\n----------------"
        for i in self.instructions_without_introns:
            if i['op'] in RESTRICTIONS['genotype_options']['one-operand-instructions']:
                text += "\n"+self.one_op_instruction_to_str(i)
            elif i['op'] in RESTRICTIONS['genotype_options']['if-instructions']:
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