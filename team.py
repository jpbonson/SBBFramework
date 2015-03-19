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

def reset_teams_ids():
    global next_team_id
    next_team_id = 0

class Team:
    def __init__(self, generation, total_input_registers, total_classes, random_mode=True, sample_programs=[]):
        global next_team_id
        next_team_id += 1
        self.team_id = next_team_id
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
        if random_mode:
            test = False
            while not test:
                index = randint(0, len(sample_programs)-1)
                candidate_program = sample_programs[index]
                if len(self.programs) == 0:
                    self.programs.append(candidate_program)
                    candidate_program.add_team(self)
                elif candidate_program not in self.programs and self.there_is_at_least_two_different_actions_given_new_program(candidate_program):
                    self.programs.append(candidate_program)
                    candidate_program.add_team(self)
                if len(self.programs) == CONFIG['initial_team_size']:
                    test = True
        else:
            for p in sample_programs:
                p.add_team(self)
                self.programs.append(p)
        self.correct_samples = []

    def there_is_at_least_two_different_actions(self):
        actions = [p.action for p in self.programs]
        actions = set(actions)
        if len(actions) < 2:
            return False
        else:
            return True

    def there_is_at_least_two_different_actions_given_new_program(self, program):
        actions = [p.action for p in self.programs]
        actions.append(program.action)
        actions = set(actions)
        if len(actions) < 2:
            return False
        else:
            return True

    def there_is_at_least_two_different_actions_removing_program(self, program):
        actions = [p.action for p in self.programs if p != program]
        actions = set(actions)
        if len(actions) < 2:
            return False
        else:
            return True

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
        fitness = macro_recall

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
        recall = recall_score(desired_outputs, predicted_outputs, average=None)
        macro_recall = numpy.mean(recall)
        if testset: # t avoid wasting time processing metrics when they are not necessary
            self.conf_matrix = conf_matrix
            self.conts_per_class = [0] * self.total_classes
            self.recall = recall
            for p, d in zip(predicted_outputs, desired_outputs):
                if p == d:
                    self.conts_per_class[d] += 1.0
            self.accuracies_per_class = [x/float(len(predicted_outputs)) for x in self.conts_per_class]
        else:
            self.correct_samples = []
            for i, (p, d) in enumerate(zip(predicted_outputs, desired_outputs)):
                if p == d:
                    self.correct_samples.append(i)
        return accuracy, macro_recall

    def print_metrics(self):
        r = Operations.round_to_decimals
        teams_members_ids = [("("+str(p.program_id)+":"+str(p.generation)+")", p.action) for p in self.programs]
        teams_members_ids.sort(key=lambda tup: tup[1])
        m = str(self.team_id)+":"+str(self.generation)+", f: "+str(r(self.fitness))+", team size: "+str(len(self.programs))+", team members: "+str(teams_members_ids)
        m += "\nTRAIN: acc: "+str(r(self.accuracy_trainingset))+", mrecall: "+str(r(self.macro_recall_trainingset))
        m += "\nTEST: acc: "+str(r(self.accuracy_testset))+", mrecall: "+str(r(self.macro_recall_testset))+", recall: "+str(self.recall)
        return m

    def remove_programs_link(self):
        for p in self.programs:
            p.remove_team(self)

    def mutate(self, new_programs):
        mutation_type = randint(0,1)
        if len(self.programs) == CONFIG['minimum_team_size']:
            mutation_type = 1
        if len(self.programs) == CONFIG['max_team_size']:
            mutation_type = 0
        if mutation_type == 0: # remove random program
            test = False
            while not test:
                index = randint(0, len(self.programs)-1)
                if self.there_is_at_least_two_different_actions_removing_program(self.programs[index]):
                    self.programs[index].remove_team(self)
                    self.programs.pop(index)
                    test = True
        else: # add random program
            if len(new_programs) == 0:
                print "WARNING! NO NEW PROGRAMS!"
                return
            test = False
            while not test:
                index = randint(0, len(new_programs)-1)
                if new_programs[index] not in self.programs:
                    new_programs[index].add_team(self)
                    self.programs.append(new_programs[index])
                    test = True

    def avg_introns(self):
        total = 0.0
        for p in self.programs:
            total += len(p.instructions)-len(p.instructions_without_introns)
        return total/float(len(self.programs))

    def to_str(self):
        text = "\nCode for team "+str(self.team_id)+" from generation "+str(self.generation)+", team size: "+str(len(self.programs))
        text += "\n################"
        for p in self.programs:
            text += "\n"+p.to_str()
        text += "\n################"
        return text


