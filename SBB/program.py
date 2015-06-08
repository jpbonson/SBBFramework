import random
from scipy.special import expit
from instruction import Instruction
from utils.operations import Operation
from config import Config

def reset_programs_ids():
    global next_program_id
    next_program_id = 0

def get_program_id():
    global next_program_id
    next_program_id += 1
    return next_program_id

class Program:
    def __init__(self, generation, instructions, action):
        self.generation = generation
        self.instructions = instructions
        self.action = action
        self.program_id_ = get_program_id()     
        self.teams_ = []
        self.instructions_without_introns_ = None

    def execute(self, input_registers):
        """
        Execute code for each input
        """
        if not self.instructions_without_introns_:
            self.instructions_without_introns_ = Program.remove_introns(self.instructions)
        instructions = self.instructions_without_introns_
        
        general_registers = [0] * Config.RESTRICTIONS['genotype_options']['total_registers']
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
                general_registers[instruction.target] = Operation.execute(instruction.op, general_registers[instruction.target])
            else:
                if instruction.mode == 'read-register':
                    source =  general_registers[instruction.source]
                else:
                    source =  input_registers[instruction.source]
                general_registers[instruction.target] = Operation.execute(instruction.op, general_registers[instruction.target], source)

        output = general_registers[0] # get action output
        membership_outputs = expit(output) # apply sigmoid function before getting the output action
        return membership_outputs

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
        if mutation_chance <= Config.USER['training_parameters']['mutation']['program']['change_action']:
            self.action = random.randrange(Config.RESTRICTIONS['total_actions'])

    def add_team(self, team):
        self.teams_.append(team)

    def remove_team(self, team):
        self.teams_.remove(team)

    def __repr__(self):
        return "("+str(self.program_id_)+":"+str(self.generation)+", "+str(self.action)+")"

    def __str__(self):
        text = "\nCode for program "+self.__repr__()
        teams_ids = [t.__repr__() for t in self.teams_]
        text += "\nParticipate in the teams ("+str(len(teams_ids))+"): "+str(teams_ids)
        text += "\nTotal instructions: "+str(len(self.instructions))
        text += "\n----------------\n"
        text += "\n"+Program.print_indented_instructions(self.instructions)
        text += "\n++++++++++++++++"
        text += "\nTotal instructions (without introns): "+str(len(self.instructions_without_introns_))
        text += "\n----------------\n"
        text += "\n"+Program.print_indented_instructions(self.instructions_without_introns_)
        text += "\n----------------"
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
    def remove_introns(instructions): # move code to C or Cython?
        """
        Remove introns (ie. instructions that don't affect the final output)
        """
        instructions_without_introns = []
        relevant_registers = [0]
        ignore_previous_if = False
        # Run throught the instructions from the last to the first one
        for instruction in reversed(instructions):
            if instruction.target in relevant_registers or instruction.op in Config.RESTRICTIONS['genotype_options']['if-instructions']:
                if ignore_previous_if and instruction.op in Config.RESTRICTIONS['genotype_options']['if-instructions']:
                    continue
                else:
                    ignore_previous_if = False
                    instructions_without_introns.insert(0, instruction)
                    if instruction.mode == 'read-register' and instruction.source not in relevant_registers:
                        relevant_registers.append(instruction.source)
                    if instruction.op in Config.RESTRICTIONS['genotype_options']['if-instructions']:
                        if instruction.target not in relevant_registers:
                            relevant_registers.append(instruction.target)
            else:
                ignore_previous_if = True
        return instructions_without_introns