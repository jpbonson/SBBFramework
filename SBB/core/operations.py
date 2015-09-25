import math
import numpy
import warnings

class Operation():
    """
    Class that provides protected execution of operations.
    If an operation results in an ArithmeticEroor, NaN, or Infinity, it returns the
    value of the 'target' register (ie. ignores the instruction)
    """

    @staticmethod
    def execute(operator, target, source=float('NaN')):
        with warnings.catch_warnings():
            warnings.simplefilter("ignore") # all errors are handled by this method, so there is no need for warnings here
            error = False
            try:
                if operator == '+':
                    result = target + source
                elif operator == '-':
                    result = target - source
                elif operator == '*':
                    result = target * source
                elif operator == '/':
                    result = target / source
                elif operator == 'ln':
                    result = numpy.log(target)
                elif operator == 'exp':
                    result = math.exp(target)
                elif operator == 'cos':
                    result = numpy.cos(target)
                elif operator == 'sin':
                    result = numpy.sin(target)
                elif operator == 'if_lesser_than_for_signal':
                    if (target < source):
                        return -target
                    else:
                        return target
                elif operator == 'if_equal_or_higher_than_for_signal':
                    if (target >= source):
                        return -target
                    else:
                        return target
            except ArithmeticError:
                error = True
            if error or math.isnan(result) or math.isinf(result):
                return target
            return result

    @staticmethod
    def execute_if(operator, target, source):
        if operator == 'if_lesser_than':
            if (target < source):
                return True
            else:
                return False
        if operator == 'if_equal_or_higher_than':
            if (target >= source):
                return True
            else:
                return False
        raise ValueError(str(operator)+" is not a valid 'if' operator.")