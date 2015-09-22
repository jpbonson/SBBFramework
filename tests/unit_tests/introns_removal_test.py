import unittest
from pSBB.SBB.core.program import Program
from pSBB.SBB.core.instruction import Instruction

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
        """
        Ensures the algorithm removes irrelevant 'if' instructions

        The 'if_lesser_than' don't modify relevant registers.
        """
        instructions = []
        instructions.append(Instruction(mode = 'read-register', target = 0, op = 'cos', source = 0))
        instructions.append(Instruction(mode = 'read-input', target = 1, op = 'if_lesser_than', source = 0))
        instructions.append(Instruction(mode = 'read-register', target = 1, op = '-', source = 1))
        instructions.append(Instruction(mode = 'read-register', target = 0, op = 'cos', source = 0))
        instructions_without_introns = Program.remove_introns(instructions)
        instructions.pop(1)
        instructions.pop(1)
        self.assertEqual(instructions, instructions_without_introns)

    def test_remove_introns_for_irrelevant_registers2(self):
        """
        Ensures the algorithm removes correctly.

        r[0] = r[0] + i[4]
        if r[0] >= i[2]: # HERE
            r[1] = r[1] - r[0] # HERE
        r[0] = r[0] - i[0]
        r[1] = r[1] + i[7] # HERE
        r[0] = exp(r[0]) # r[1] shouldn't be added to relevant registers
        r[0] = r[0] * i[6]
        """
        a = Instruction(mode = 'read-input', target = 0, op = '+', source = 4)
        b = Instruction(mode = 'read-input', target = 0, op = 'if_equal_or_higher_than', source = 2)
        c = Instruction(mode = 'read-register', target = 1, op = '-', source = 0)
        d = Instruction(mode = 'read-input', target = 0, op = '-', source = 0)
        e = Instruction(mode = 'read-input', target = 1, op = '+', source = 7)
        f = Instruction(mode = 'read-register', target = 0, op = 'exp', source = 1)
        g = Instruction(mode = 'read-input', target = 0, op = '*', source = 6)
        instructions = [a,b,c,d,e,f,g]
        instructions_without_introns = Program.remove_introns(instructions)
        instructions.remove(b)
        instructions.remove(c)
        instructions.remove(e)
        self.assertEqual(instructions, instructions_without_introns)

    def test_remove_introns_for_irrelevant_registers3(self):
        """
        Ensures the algorithm removes correctly.

        r[0] = r[0] + i[4]
        r[0] = r[0] - i[0]
        r[1] = r[1] + i[7] # HERE
        if r[0] >= r[1]: # HERE: r[1] shouldn't be added to relevant registers
            r[1] = r[1] - r[0] # HERE
        r[0] = r[0] * i[6]
        """
        a = Instruction(mode = 'read-input', target = 0, op = '+', source = 4)
        b = Instruction(mode = 'read-input', target = 0, op = '-', source = 0)
        c = Instruction(mode = 'read-input', target = 1, op = '+', source = 7)
        d = Instruction(mode = 'read-register', target = 0, op = 'if_equal_or_higher_than', source = 1)
        e = Instruction(mode = 'read-register', target = 1, op = '-', source = 0)
        f = Instruction(mode = 'read-input', target = 0, op = '*', source = 6)
        instructions = [a,b,c,d,e,f]
        instructions_without_introns = Program.remove_introns(instructions)
        instructions.remove(c)
        instructions.remove(d)
        instructions.remove(e)
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

    def test_dont_remove_if_lesser_than_when_both_sides_are_equal_1(self):
        """
        It would make more sense to remove this type of if. But I prefer avoid bugs and keep them.

        r[0] = r[0] - i[1]
        if r[1] < r[1]:
            if r[0] >= i[0]:
                if r[0] < i[0]:
                    r[0] = cos(r[0])
        r[0] = r[0] - i[1]
        """
        a = Instruction(mode = 'read-input', target = 0, op = '-', source = 1)
        b = Instruction(mode = 'read-register', target = 1, op = 'if_lesser_than', source = 1)
        c = Instruction(mode = 'read-input', target = 0, op = 'if_equal_or_higher_than', source = 0)
        d = Instruction(mode = 'read-input', target = 0, op = 'if_lesser_than', source = 0)
        e = Instruction(mode = 'read-register', target = 0, op = 'cos', source = 0)
        f = Instruction(mode = 'read-input', target = 0, op = '-', source = 1)
        instructions = [a,b,c,d,e,f]
        instructions_without_introns = Program.remove_introns(instructions)
        self.assertEqual(instructions, instructions_without_introns)

    def test_dont_remove_if_lesser_than_when_both_sides_are_equal_2(self):
        """
        It would make more sense to remove this type of if. But I prefer avoid bugs and keep them.

        r[1] = r[1] + i[1]
        r[0] = r[0] * r[1]
        if r[1] >= r[1]:
            if r[1] < r[1]:
                r[0] = r[0] * i[5]
        r[1] = exp(r[1])
        r[1] = r[1] * i[3]
        r[0] = r[0] + r[1]
        """
        a = Instruction(mode = 'read-input', target = 1, op = '+', source = 1)
        b = Instruction(mode = 'read-register', target = 0, op = '*', source = 1)
        c = Instruction(mode = 'read-register', target = 1, op = 'if_equal_or_higher_than', source = 1)
        d = Instruction(mode = 'read-register', target = 1, op = 'if_lesser_than', source = 1)
        e = Instruction(mode = 'read-input', target = 0, op = '*', source = 5)
        f = Instruction(mode = 'read-register', target = 1, op = 'exp', source = 1)
        g = Instruction(mode = 'read-input', target = 1, op = '*', source = 3)
        h = Instruction(mode = 'read-register', target = 0, op = '+', source = 1)
        instructions = [a,b,c,d,e,f,g,h]
        instructions_without_introns = Program.remove_introns(instructions)
        self.assertEqual(instructions, instructions_without_introns)

if __name__ == '__main__':
    unittest.main()