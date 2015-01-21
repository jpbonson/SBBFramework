#!/usr/bin/env python
# encoding: utf-8
## vim:ts=4:et:nowrap

import random
import math
import time
from random import randint
from collections import defaultdict
from scipy.special import expit

def isfloat(element):
    try:
        float(element)
        return True
    except ValueError:
        return False

def isnumber(element):
    if element.isdigit() or isfloat(element):
        return True
    return False

def map_data(data):
    mapping = {}
    for item in data:
        if not isnumber(item):
            if item not in mapping:
                mapping[item] = len(mapping)
    return mapping

def read_inputs(data_file):
    with open(data_file) as f:
        content = f.readlines()
        content = [x.strip('\n') for x in content]
        content = [x.split(',') for x in content if x]
        random.shuffle(content)
        X = [x[:-1] for x in content]
        Y = [x[-1:] for x in content]
        Y = sum(Y, [])
    input_mapping = map_data(sum(X, []))
    output_mapping = map_data(Y)
    X = [[float(input_mapping.get(k, k)) for k in x] for x in X]
    Y = [int(output_mapping.get(x, x)) for x in Y]
    return X, Y, input_mapping, output_mapping

def get_class_distribution(Y):
    cont = defaultdict(int)
    for y in Y:
        cont[y] += 1
    print("Class Distributions: "+str(cont)+", for a total of "+str(len(Y))+" samples")
    return cont

def split_for_crossvalidation(X, Y, test_percentage):
    # split train and test datasets maintaing the data distribution
    cont = get_class_distribution(Y)
    test_quantities = {}
    for item, value in cont.items():
        test_quantities[item] = int(value*test_percentage)
    cont = defaultdict(int)
    X_train = []
    X_test = []
    Y_train = []
    Y_test = []
    for x, y in zip(X, Y):
        if cont[y] < test_quantities[y]:
            X_test.append(x)
            Y_test.append(y)
        else:
            X_train.append(x)
            Y_train.append(y)
        cont[y] += 1
    return X_train, Y_train, X_test, Y_test

def read_inputs_already_partitioned(data_file):
    X_train = []
    X_test = []
    Y_train = []
    Y_test = []
    return X_train, Y_train, X_test, Y_test

def round_to_decimals(value):
    round_decimals_to = 5
    number = float(10**round_decimals_to)
    return int(value * number) / number

class Operations(object):
    @staticmethod
    def sum(op1, op2):
        try:
            result = op1+op2
        except ArithmeticError:
            result = op1
        if math.isnan(result):
            return op1
        return result

    @staticmethod
    def minus(op1, op2):
        try:
            result = op1-op2
        except ArithmeticError:
            result = op1
        if math.isnan(result):
            return op1
        return result

    @staticmethod
    def multi(op1, op2):
        try:
            result = op1*op2
        except ArithmeticError:
            result = op1
        if math.isnan(result):
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
        if math.isnan(result):
            return op1
        return result