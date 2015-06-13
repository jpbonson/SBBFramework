import unittest
from pSBB.SBB.program import Program
from pSBB.SBB.instruction import Instruction

class IntronRemovalTests(unittest.TestCase):
    def test_dont_remove_nonintrons(self):
        """ Ensures the algorithm is not removing valid instructions """
        instructions = []
        instructions.append(Instruction(mode = 'read-input', target = 0, op = '+', source = 0))
        instructions.append(Instruction(mode = 'read-input', target = 0, op = '-', source = 0))
        instructions.append(Instruction(mode = 'read-input', target = 0, op = '/', source = 0))
        instructions.append(Instruction(mode = 'read-input', target = 0, op = 'cos', source = 0))
        instructions_without_introns = Program.remove_introns(instructions)
        self.assertEqual(instructions, instructions_without_introns)

    def test_remove_introns_after_output_register(self):
        """ Ensures the algorithm removes instructions after the final output register """
        instructions = []
        instructions.append(Instruction(mode = 'read-input', target = 1, op = '+', source = 0))
        instructions.append(Instruction(mode = 'read-register', target = 0, op = '-', source = 1))
        instructions.append(Instruction(mode = 'read-register', target = 1, op = '/', source = 0))
        instructions.append(Instruction(mode = 'read-register', target = 1, op = 'cos', source = 0))
        instructions_without_introns = Program.remove_introns(instructions)
        instructions.pop(-1)
        instructions.pop(-1)
        self.assertEqual(instructions, instructions_without_introns)

    def test_remove_introns_for_irrelevant_registers(self):
        """ Ensures the algorithm removes instructions for irrelevant registers """
        instructions = []
        instructions.append(Instruction(mode = 'read-register', target = 2, op = 'cos', source = 0))
        instructions.append(Instruction(mode = 'read-input', target = 1, op = '+', source = 0))
        instructions.append(Instruction(mode = 'read-register', target = 0, op = '-', source = 1))
        instructions_without_introns = Program.remove_introns(instructions)
        instructions.pop(0)
        self.assertEqual(instructions, instructions_without_introns)

    def test_remove_introns_for_ifs_at_the_end(self):
        """ Ensures the algorithm removes instructions for irrelevant registers """
        instructions = []
        instructions.append(Instruction(mode = 'read-register', target = 2, op = 'cos', source = 0))
        instructions.append(Instruction(mode = 'read-register', target = 0, op = '+', source = 2))
        instructions.append(Instruction(mode = 'read-register', target = 0, op = 'if_lesser_than', source = 1))
        instructions_without_introns = Program.remove_introns(instructions)
        instructions.pop(len(instructions)-1)
        self.assertEqual(instructions, instructions_without_introns)

    def test_remove_irrelevant_ifs(self):
        """ Ensures the algorithm removes irrelevant 'if' instructions """
        instructions = []
        instructions.append(Instruction(mode = 'read-register', target = 0, op = 'cos', source = 0))
        instructions.append(Instruction(mode = 'read-input', target = 1, op = 'if_lesser_than', source = 0))
        instructions.append(Instruction(mode = 'read-register', target = 1, op = '-', source = 1))
        instructions.append(Instruction(mode = 'read-register', target = 0, op = 'cos', source = 0))
        instructions_without_introns = Program.remove_introns(instructions)
        instructions.pop(1)
        instructions.pop(1)
        self.assertEqual(instructions, instructions_without_introns)

    def test_dont_remove_relevant_ifs(self):
        """ Ensures the algorithm don't removes relevant 'if' instructions """
        instructions = []
        instructions.append(Instruction(mode = 'read-register', target = 0, op = 'cos', source = 0))
        instructions.append(Instruction(mode = 'read-input', target = 1, op = 'if_lesser_than', source = 0))
        instructions.append(Instruction(mode = 'read-register', target = 0, op = '-', source = 1))
        instructions.append(Instruction(mode = 'read-register', target = 0, op = 'cos', source = 0))
        instructions_without_introns = Program.remove_introns(instructions)
        self.assertEqual(instructions, instructions_without_introns)

    def test_dont_remove_relevant_ifs2(self):
        """ Ensures the algorithm don't removes relevant 'if' instructions """
        instructions = []
        instructions.append(Instruction(mode = 'read-register', target = 0, op = 'cos', source = 0))
        instructions.append(Instruction(mode = 'read-input', target = 0, op = 'if_lesser_than', source = 0))
        instructions.append(Instruction(mode = 'read-register', target = 0, op = '-', source = 1))
        instructions.append(Instruction(mode = 'read-register', target = 0, op = 'cos', source = 0))
        instructions_without_introns = Program.remove_introns(instructions)
        self.assertEqual(instructions, instructions_without_introns)

    def test_dont_remove_relevant_ifs3(self):
        """
        Ensures the algorithm don't removes relevant 'if' instructions (when the 'target' is used in an 
        'if' that affects a relevant register)

        if r[0] >= i[3]:
            if r[0] < i[0]:
                r[1] = ln(r[1])
        if r[1] < i[19]:
            if r[1] < i[14]:
                r[0] = r[0] / r[0]

        """
        instructions = []
        instructions.append(Instruction(mode = 'read-input', target = 0, op = 'if_equal_or_higher_than', source = 3))
        instructions.append(Instruction(mode = 'read-input', target = 0, op = 'if_lesser_than', source = 0))
        instructions.append(Instruction(mode = 'read-register', target = 1, op = 'ln', source = 0))
        instructions.append(Instruction(mode = 'read-input', target = 1, op = 'if_lesser_than', source = 19))
        instructions.append(Instruction(mode = 'read-input', target = 1, op = 'if_lesser_than', source = 14))
        instructions.append(Instruction(mode = 'read-register', target = 0, op = '/', source = 0))
        instructions_without_introns = Program.remove_introns(instructions)
        self.assertEqual(instructions, instructions_without_introns)

if __name__ == '__main__':
    unittest.main()