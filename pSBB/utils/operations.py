import math

class Operations(object):
    @staticmethod
    def sum(op1, op2):
        try:
            result = op1+op2
        except ArithmeticError:
            result = op1
        if math.isnan(result) or math.isinf(result):
            return op1
        return result

    @staticmethod
    def minus(op1, op2):
        try:
            result = op1-op2
        except ArithmeticError:
            result = op1
        if math.isnan(result) or math.isinf(result):
            return op1
        return result

    @staticmethod
    def multi(op1, op2):
        try:
            result = op1*op2
        except ArithmeticError:
            result = op1
        if math.isnan(result) or math.isinf(result):
            return op1
        return result

    @staticmethod
    def div(op1, op2):
        # report: foi escolhida a PD porque a QA alterava bastante os resultados para numeros pequenos, que ocorrem nesses datasets do trabalho
        # protected division
        try:
            if op2 != 0:
                result = op1/op2
            else:
                result = 1
        except ArithmeticError:
            result = op1
        if math.isnan(result) or math.isinf(result):
            return op1
        return result

    @staticmethod
    def ln(op1):
        if op1 == 0.0:
            return 1.0
        try:
            result = numpy.log(op1)
        except ArithmeticError:
            result = op1
        if math.isnan(result) or math.isinf(result):
            return op1
        return result

    @staticmethod
    def exp(op1):
        try:
            result = math.exp(op1)
        except ArithmeticError:
            result = op1
        if math.isnan(result) or math.isinf(result):
            return op1
        return result

    @staticmethod
    def cos(op1):
        try:
            result = numpy.cos(op1)
        except ArithmeticError:
            result = op1
        if math.isnan(result) or math.isinf(result):
            return op1
        return result