import random
from scipy.special import expit
from instruction import Instruction
from utils.helpers import remove_introns
from utils.operations import Operation
from config import CONFIG, RESTRICTIONS

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

    def execute(self, input_registers): # move code to C or Cython?
        """ Execute code for each input """
        if not self.instructions_without_introns_:
            self.instructions_without_introns_ = remove_introns(self.instructions)
        instructions = self.instructions_without_introns_
        
        general_registers = [0] * RESTRICTIONS['genotype_options']['total_registers']
        if_conditional = None
        skip_next = False

        for i in instructions:
            if if_conditional:
                if if_conditional.op == 'if_lesser_than' and not (if_conditional.target < if_conditional.source):
                    if_conditional = None
                    if i.op in RESTRICTIONS['genotype_options']['if-instructions']:
                        skip_next = True
                    continue
                if if_conditional.op == 'if_equal_or_higher_than' and not (if_conditional.target >= if_conditional.source):
                    if_conditional = None
                    if i.op in RESTRICTIONS['genotype_options']['if-instructions']:
                        skip_next = True
                    continue
                if_conditional = None
            if skip_next:
                if i.op in RESTRICTIONS['genotype_options']['if-instructions']:
                    skip_next = True
                else:
                    skip_next = False
                continue
            
            if i.op in RESTRICTIONS['genotype_options']['if-instructions']:
                if_conditional = i
                continue
            elif i.op in RESTRICTIONS['genotype_options']['one-operand-instructions']:
                general_registers[i.target] = Operation.execute(i.op, general_registers[i.target])
            else:
                if i.mode == 'read-register':
                    source =  general_registers[i.source]
                else:
                    source =  input_registers[i.source]
                general_registers[i.target] = Operation.execute(i.op, general_registers[i.target], source)
        # get class output
        output = general_registers[0]
        # apply sigmoid function before getting the output class
        membership_outputs = expit(output)
        return membership_outputs

    def mutate(self):
        mutation_chance = random.random()
        if (mutation_chance <= CONFIG['training_parameters']['mutation']['program']['remove_instruction'] and 
                len(self.instructions) > CONFIG['training_parameters']['program_size']['min']):
            self.instructions.remove(random.choice(self.instructions))

        mutation_chance = random.random()
        if mutation_chance <= CONFIG['training_parameters']['mutation']['program']['change_instruction']:
            instruction = random.choice(self.instructions)
            instruction.mutate()
 
        mutation_chance = random.random()
        if (mutation_chance <= CONFIG['training_parameters']['mutation']['program']['add_instruction'] and 
                len(self.instructions) < CONFIG['training_parameters']['program_size']['max']):
            index = random.randrange(len(self.instructions))
            self.instructions.insert(index, Instruction())
        
        mutation_chance = random.random()
        if mutation_chance <= CONFIG['training_parameters']['mutation']['program']['change_action']:
            self.action = random.randrange(RESTRICTIONS['total_actions'])

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
        text += "\n".join([str(i) for i in self.instructions])
        text += "\n++++++++++++++++"
        text += "\nTotal instructions (without introns): "+str(len(self.instructions_without_introns_))
        text += "\n----------------\n"
        text += "\n".join([str(i) for i in self.instructions_without_introns_])
        text += "\n----------------"
        return text