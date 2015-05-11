#!/usr/bin/env python
# encoding: utf-8
## vim:ts=4:et:nowrap

import random
import math
import time
import numpy
from random import randint
from collections import defaultdict
from config import *

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

    @staticmethod
    def isfloat(element):
        try:
            float(element)
            return True
        except ValueError:
            return False

    @staticmethod
    def isnumber(element):
        if element.isdigit() or Operations.isfloat(element):
            return True
        return False

    @staticmethod
    def round_to_decimals(value, round_decimals_to = 5):
        number = float(10**round_decimals_to)
        return int(value * number) / number

def get_X(data):
    return [x[:-1] for x in data]

def get_Y(data):
    Y = [x[-1:] for x in data]
    Y = sum(Y, [])
    Y = [int(y) for y in Y]
    if 0 not in Y:
        Y = [y-1 for y in Y]  # added -1 due to class labels starting at 1
    return Y

def get_class_distribution(Y):
    cont = defaultdict(int)
    for y in Y:
        cont[y] += 1
    print("Class Distributions: "+str(cont)+", for a total of "+str(len(Y))+" samples")
    return cont

def read_inputs_already_partitioned(data_name):
    train = read_space_separated_file(WORKING_PATH+"datasets/"+data_name+".train")
    test = read_space_separated_file(WORKING_PATH+"datasets/"+data_name+".test")
    return train, test

def read_space_separated_file(file_path):
    with open(file_path) as f:
        content = f.readlines()
        content = [x.strip('\n').strip() for x in content]
        content = [x.split(' ') for x in content]
        content = [[float(y) for y in x]for x in content]
    return content