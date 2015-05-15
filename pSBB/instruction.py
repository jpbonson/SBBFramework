import random
from config import CONFIG, RESTRICTIONS

class Instruction:
    def __init__(self, total_inputs, mode = None, target = None, op = None, source = None):
        self.total_inputs = total_inputs
        self.mode = mode
        self.target = target
        self.op = op
        self.source = source
        if mode is None:
            self.mode = random.choice(RESTRICTIONS['genotype_options']['modes'])
        if target is None:
            self.target = random.randrange(RESTRICTIONS['genotype_options']['total_registers'])
        if op is None:
            self.op = random.choice(CONFIG['advanced_training_parameters']['use_operations'])
        if source is None:
            if self.mode == 'read-register':
                self.source = random.randrange(RESTRICTIONS['genotype_options']['total_registers'])
            else:
                self.source = random.randrange(self.total_inputs)

    def mutate(self):
        instruction_parameter = random.randrange(RESTRICTIONS['genotype_options']['instruction_size'])
        if instruction_parameter == 0:
            if self.mode == RESTRICTIONS['genotype_options']['modes'][0]:
                self.mode = RESTRICTIONS['genotype_options']['modes'][1]
            else:
                self.mode = RESTRICTIONS['genotype_options']['modes'][0]
        if instruction_parameter == 1:
            self.target = random.randrange(RESTRICTIONS['genotype_options']['total_registers'])
        if instruction_parameter == 2:
            self.op = random.choice(CONFIG['advanced_training_parameters']['use_operations'])
        if instruction_parameter == 0 or instruction_parameter == 3:
            if self.mode == 'read-register':
                self.source = random.randrange(RESTRICTIONS['genotype_options']['total_registers'])
            else:
                self.source = random.randrange(self.total_inputs)

    def __repr__(self):
        if self.op in RESTRICTIONS['genotype_options']['one-operand-instructions']:
            text = self.one_op_instruction_to_str()
        elif self.op in RESTRICTIONS['genotype_options']['if-instructions']:
            text = self.if_op_instruction_to_str()
        else:
            text = self.two_ops_instruction_to_str()
        return text

    def one_op_instruction_to_str(self):
        return "r["+str(self.target)+"] = "+self.op+"(r["+str(self.target)+"])"

    def if_op_instruction_to_str(self):
        if self.mode == 'read-register':
            source = "r["+str(self.source)+"]:"
        else:
            source = "i["+str(self.source)+"]:"
        if self.op == 'if_lesser_than':
            return "if r["+str(self.target)+"] < "+source
        else:
            return "if r["+str(self.target)+"] >= "+source

    def two_ops_instruction_to_str(self):
        instruction_text = "r["+str(self.target)+"] = r["+str(self.target)+"] "+self.op+" "
        if self.mode == 'read-register':
            instruction_text += "r["+str(self.source)+"]"
        else:
            instruction_text += "i["+str(self.source)+"]"
        return instruction_text