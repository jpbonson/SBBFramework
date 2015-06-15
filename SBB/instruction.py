import random
from config import Config

class Instruction:
    """
    The class that represents an instruction of a program, eg.: r[1] = r[1] / r[0]
    """

    def __init__(self, mode = None, target = None, op = None, source = None):
        self.mode = mode
        self.target = target
        self.op = op
        self.source = source
        if mode is None:
            self.mode = random.choice(Config.RESTRICTIONS['genotype_options']['modes'])
        if target is None:
            self.target = random.randrange(Config.RESTRICTIONS['genotype_options']['total_registers'])
        if op is None:
            self.op = random.choice(Config.USER['advanced_training_parameters']['use_operations'])
        if source is None:
            if self.mode == 'read-register':
                self.source = random.randrange(Config.RESTRICTIONS['genotype_options']['total_registers'])
            else:
                self.source = random.randrange(Config.RESTRICTIONS['total_inputs'])

    def mutate(self):
        instruction_parameter = random.randrange(Config.RESTRICTIONS['genotype_options']['instruction_size'])
        if instruction_parameter == 0:
            if self.mode == Config.RESTRICTIONS['genotype_options']['modes'][0]:
                self.mode = Config.RESTRICTIONS['genotype_options']['modes'][1]
            else:
                self.mode = Config.RESTRICTIONS['genotype_options']['modes'][0]
        if instruction_parameter == 1:
            self.target = random.randrange(Config.RESTRICTIONS['genotype_options']['total_registers'])
        if instruction_parameter == 2:
            self.op = random.choice(Config.USER['advanced_training_parameters']['use_operations'])
        if instruction_parameter == 0 or instruction_parameter == 3:
            if self.mode == 'read-register':
                self.source = random.randrange(Config.RESTRICTIONS['genotype_options']['total_registers'])
            else:
                self.source = random.randrange(Config.RESTRICTIONS['total_inputs'])

    def dict(self):
        return {'mode': self.mode, 'target': self.target, 'op': self.op, 'source': self.source}

    def __repr__(self):
        if self.op in Config.RESTRICTIONS['genotype_options']['one-operand-instructions']:
            text = self._one_op_instruction_to_str()
        elif self.op in Config.RESTRICTIONS['genotype_options']['if-instructions']:
            text = self._if_op_instruction_to_str()
        else:
            text = self._two_ops_instruction_to_str()
        return text

    def _one_op_instruction_to_str(self):
        return "r["+str(self.target)+"] = "+self.op+"(r["+str(self.target)+"])"

    def _if_op_instruction_to_str(self):
        if self.mode == 'read-register':
            source = "r["+str(self.source)+"]:"
        else:
            source = "i["+str(self.source)+"]:"
        if self.op == 'if_lesser_than':
            return "if r["+str(self.target)+"] < "+source
        else:
            return "if r["+str(self.target)+"] >= "+source

    def _two_ops_instruction_to_str(self):
        instruction_text = "r["+str(self.target)+"] = r["+str(self.target)+"] "+self.op+" "
        if self.mode == 'read-register':
            instruction_text += "r["+str(self.source)+"]"
        else:
            instruction_text += "i["+str(self.source)+"]"
        return instruction_text