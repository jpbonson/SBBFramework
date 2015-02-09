#!/usr/bin/env python
# encoding: utf-8
## vim:ts=4:et:nowrap

import random
import math
import time
import numpy
from random import randint
from collections import defaultdict
from scipy.special import expit
from sklearn.metrics import confusion_matrix, accuracy_score, recall_score
from helpers import *
from config import *
from program import Program

class Team:
    def __init__(self, generation, total_input_registers, total_classes, sample_programs=[]):
        self.team_id = -1 # TODO
        self.generation = generation
        self.total_input_registers = total_input_registers
        self.total_classes = total_classes
        self.accuracies_per_class = []
        self.conts_per_class = []
        self.conf_matrix = []
        self.fitness = -1
        self.accuracy_trainingset = 0
        self.accuracy_testset = 0
        self.recall = 0
        self.programs = []
        for i in range(CONFIG['initial_team_size']):
            index = randint(0, len(sample_programs)-1)
            self.programs.append(sample_programs[index])

    def execute(self, data, testset=False):
        # execute code for each input
        outputs = []
        X = get_X(data)
        Y = get_Y(data)
        for x in X:
            partial_outputs = []
            for program in self.programs:
                partial_outputs.append(program.execute(x, testset=False))
            output_class = self.programs[partial_outputs.index(max(partial_outputs))].action
            outputs.append(output_class)
        # calculate fitness and accuracy
        accuracy, macro_recall = self.calculate_performance_metrics(outputs, Y, testset)
        fitness = accuracy

        if testset:
            self.accuracy_testset = accuracy
            self.macro_recall_testset = macro_recall
        else:
            self.fitness = fitness
            self.accuracy_trainingset = accuracy
            self.macro_recall_trainingset = macro_recall

    def calculate_performance_metrics(self, predicted_outputs, desired_outputs, testset=False):
        conf_matrix = confusion_matrix(desired_outputs, predicted_outputs)
        accuracy = accuracy_score(desired_outputs, predicted_outputs)
        macro_recall = recall_score(desired_outputs, predicted_outputs, average='macro')
        if testset:
            self.conf_matrix = conf_matrix
            self.conts_per_class = [0] * self.total_classes
            self.recall = recall_score(desired_outputs, predicted_outputs, average=None)
            for p, d in zip(predicted_outputs, desired_outputs):
                if p == d:
                    self.conts_per_class[d] += 1.0
            self.accuracies_per_class = [x/float(len(predicted_outputs)) for x in self.conts_per_class]
        return accuracy, macro_recall

    def print_metrics(self):
        r = Operations.round_to_decimals
        m = str(self.team_id)+":"+str(self.generation)+", f: "+str(r(self.fitness))+", team size: "+str(len(self.programs))
        m += "\nTRAIN: acc: "+str(r(self.accuracy_trainingset))+", mrecall: "+str(r(self.macro_recall_trainingset))
        m += "\nTEST: acc: "+str(r(self.accuracy_testset))+", mrecall: "+str(r(self.macro_recall_testset))+", final: "+str(r(numpy.mean([self.accuracy_testset, self.macro_recall_testset])))+", recall: "+str(self.recall)
        return m

    def mutate(self):
        pass # TODO

    def to_str(self):
        text = "\nCode for team "+str(self.team_id)+" from generation "+str(self.generation)+", team size: "+str(len(self.programs))
        text += "\n################"
        for p in self.programs:
            text += "\n"+p.to_str()
        text += "\n################"
        return text


