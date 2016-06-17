import random
from instruction import Instruction
from operations import Operation
from ..config import Config

def reset_programs_ids():
    global next_program_id
    next_program_id = 0

def get_program_id():
    global next_program_id
    next_program_id += 1
    return next_program_id
 
class Program:
    def __init__(self, generation, instructions, action, program_id = None):
        self.generation = generation
        self.instructions = instructions
        self.action = action
        if program_id is None:
            self.program_id_ = get_program_id()
        else:
            self.program_id_ = program_id
        self.teams_ = []
        self.instructions_without_introns_ = []
        self.inputs_list_ = []
        self.general_registers = [0] * Config.RESTRICTIONS['genotype_options']['total_registers']

    def reset_registers(self):
        self.general_registers = [0] * Config.RESTRICTIONS['genotype_options']['total_registers']

    def execute(self, input_registers, force_reset = False):
        """
        Execute code for each input
        """
        if len(self.instructions_without_introns_) == 0:
            self.instructions_without_introns_ = Program.remove_introns(self.instructions)
            self.inputs_list_ = self._inputs_list()
        instructions = self.instructions_without_introns_
        if Config.USER['task'] == 'classification' or force_reset:
            self.reset_registers()
        if_instruction = None
        skip_next = False
        for instruction in instructions:
            if if_instruction and not Operation.execute_if(if_instruction.op, if_instruction.target, if_instruction.source):
                if_instruction = None
                if instruction.op in Config.RESTRICTIONS['genotype_options']['if-instructions']:
                    skip_next = True
            elif skip_next:
                if instruction.op in Config.RESTRICTIONS['genotype_options']['if-instructions']:
                    skip_next = True
                else:
                    skip_next = False
            elif instruction.op in Config.RESTRICTIONS['genotype_options']['if-instructions']:
                if_instruction = instruction
            elif instruction.op in Config.RESTRICTIONS['genotype_options']['one-operand-instructions']:
                self.general_registers[instruction.target] = Operation.execute(instruction.op, self.general_registers[instruction.target])
            else:
                if instruction.mode == 'read-register':
                    source =  self.general_registers[instruction.source]
                else:
                    source =  input_registers[instruction.source]
                self.general_registers[instruction.target] = Operation.execute(instruction.op, self.general_registers[instruction.target], source)

        return self.general_registers[0] # get bid output

    def _inputs_list(self):
        inputs = []
        for instruction in self.instructions_without_introns_:
            if instruction.mode == 'read-input' and instruction.op not in Config.RESTRICTIONS['genotype_options']['one-operand-instructions']:
                if instruction.source not in inputs:
                    inputs.append(instruction.source)
        return inputs

    def _get_action_result(self, point_id, inputs, valid_actions, is_training):
        if self.is_atomic_action():
            return self.action
        else:
            team = Config.RESTRICTIONS['second_layer']['action_mapping'][self.action]
            return team.execute(point_id, inputs, valid_actions, is_training, update_profile = False)

    def is_atomic_action(self):
        if not Config.USER['advanced_training_parameters']['second_layer']['enabled']:
            return True
        else:
            if self.generation == -1:
                return True # WARNING: Incompatible for more than 2 layers, also need to use gambiarra/workaround to load teams with 2 layers
            else:
                return False

    def get_raw_actions(self):
        if self.is_atomic_action():
            return [self.action]
        else:
            meta_action = self.action
            team = Config.RESTRICTIONS['second_layer']['action_mapping'][meta_action]
            actions = [p.action for p in team.programs]
            return actions

    def mutate(self):
        mutation_chance = random.random()
        if (mutation_chance <= Config.USER['training_parameters']['mutation']['program']['remove_instruction'] and 
                len(self.instructions) > Config.USER['training_parameters']['program_size']['min']):
            self.instructions.remove(random.choice(self.instructions))

        mutation_chance = random.random()
        if mutation_chance <= Config.USER['training_parameters']['mutation']['program']['change_instruction']:
            instruction = random.choice(self.instructions)
            instruction.mutate()
 
        mutation_chance = random.random()
        if (mutation_chance <= Config.USER['training_parameters']['mutation']['program']['add_instruction'] and 
                len(self.instructions) < Config.USER['training_parameters']['program_size']['max']):
            index = random.randrange(len(self.instructions))
            self.instructions.insert(index, Instruction())
        
        mutation_chance = random.random()
        if (mutation_chance <= Config.USER['training_parameters']['mutation']['program']['swap_instructions']and 
                len(self.instructions) > Config.USER['training_parameters']['program_size']['min']):
            available_indeces = range(len(self.instructions))
            index1 = random.choice(available_indeces)
            available_indeces.remove(index1)
            index2 = random.choice(available_indeces)
            temp = self.instructions[index1]
            self.instructions[index1] = self.instructions[index2]
            self.instructions[index2] = temp

        mutation_chance = random.random()
        if mutation_chance <= Config.USER['training_parameters']['mutation']['program']['change_action']:
            self.action = random.randrange(Config.RESTRICTIONS['total_actions'])

    def add_team(self, team):
        self.teams_.append(team)

    def remove_team(self, team):
        self.teams_.remove(team)

    def dict(self):
        save = {}
        save['program_id'] = self.program_id_
        save['action'] = self.action
        if self.is_atomic_action():
            save['action_type'] = 'atomic'
        else:
            save['action_type'] = 'meta'
        save['instructions'] = []
        for instruction in self.instructions:
            save['instructions'].append(instruction.dict())
        return save

    def __repr__(self):
        return "("+str(self.program_id_)+":"+str(self.generation)+", "+str(self.action)+")"

    def __str__(self):
        text = "\n#### Program "+self.__repr__()
        teams_ids = [t.__repr__() for t in self.teams_]
        text += "\nParticipate in the teams ("+str(len(teams_ids))+"): "+str(teams_ids)
        if self.is_atomic_action():
            text += "\nAction Type: atomic"
        else:
            text += "\nAction Type: meta"
        text += "\n================\n"
        text += "\nTotal instructions (without introns): "+str(len(self.instructions_without_introns_))
        text += "\nInputs used: "+str(self.inputs_list_)
        text += "\n----------------\n"
        text += "\n"+Program.print_indented_instructions(self.instructions_without_introns_)
        text += "\n================\n"
        text += "\nTotal instructions: "+str(len(self.instructions))
        text += "\n----------------\n"
        text += "\n"+Program.print_indented_instructions(self.instructions)
        text += "\n################"
        return text

    @staticmethod
    def print_indented_instructions(instructions):
        text = ""
        indentation = 0
        spaces = 4
        for instruction in instructions:
            text += (" ")*spaces*indentation+str(instruction)+"\n"
            if instruction.op in Config.RESTRICTIONS['genotype_options']['if-instructions']:
                indentation += 1
            else:
                indentation = 0
        return text

    @staticmethod
    def remove_introns(instructions):
        """
        Remove introns (ie. instructions that don't affect the final output)
        """
        instructions_without_introns = []
        relevant_registers = [0]
        ignore_previous_if = True
        for instruction in reversed(instructions):
            if instruction.target in relevant_registers or instruction.op in Config.RESTRICTIONS['genotype_options']['if-instructions']:
                if ignore_previous_if and instruction.op in Config.RESTRICTIONS['genotype_options']['if-instructions']:
                    continue
                else:
                    ignore_previous_if = False
                    instructions_without_introns.insert(0, instruction)
                    if not instruction.op in Config.RESTRICTIONS['genotype_options']['one-operand-instructions']:
                        if instruction.mode == 'read-register' and instruction.source not in relevant_registers:
                            relevant_registers.append(instruction.source)
                    if instruction.op in Config.RESTRICTIONS['genotype_options']['if-instructions'] or instruction.op in Config.RESTRICTIONS['genotype_options']['if-instructions-for-signal']:
                        if instruction.target not in relevant_registers:
                            relevant_registers.append(instruction.target)
            else:
                ignore_previous_if = True
        return instructions_without_introns