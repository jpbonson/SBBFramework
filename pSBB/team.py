import random
import math
import time
import numpy
from collections import defaultdict
from collections import Counter
from scipy.special import expit
from sklearn.metrics import confusion_matrix, accuracy_score, recall_score
from utils.helpers import *
from config import *
from program import Program

def reset_teams_ids():
    global next_team_id
    next_team_id = 0

def get_team_id():
    global next_team_id
    next_team_id += 1
    return next_team_id

class Team:
    def __init__(self, generation, total_input_registers, total_actions, programs, initialization=True):
        self.team_id = get_team_id()
        self.generation = generation
        self.total_input_registers = total_input_registers
        self.total_actions = total_actions
        self.accuracies_per_class = []
        self.conts_per_class = []
        self.conf_matrix = []
        self.fitness = -1
        self.accuracy_trainingset = 0
        self.accuracy_testset = 0
        self.recall = 0
        self.programs = []
        self.active_programs = []
        if initialization:
            # randomly gets one program per action
            for action in programs: # programs is an array of programs per action
                program = random.choice(action)
                self.programs.append(program)
                program.add_team(self)
        else:
            # add all programs to itself
            for program in programs: # programs is an array of programs
                self.programs.append(program)
                program.add_team(self)
        self.correct_samples = []

    def execute(self, data, testset=False):
        # execute code for each input
        outputs = []
        X = get_X(data)
        Y = get_Y(data)
        for x in X:
            partial_outputs = []
            for program in self.programs:
                partial_outputs.append(program.execute(x, testset=False))
            selected_program = self.programs[partial_outputs.index(max(partial_outputs))]
            output_class = selected_program.action
            outputs.append(output_class)
            if selected_program.program_id not in self.active_programs:
                self.active_programs.append(selected_program.program_id)
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
        recall = recall_score(desired_outputs, predicted_outputs, average=None)
        macro_recall = numpy.mean(recall)
        if testset: # to avoid wasting time processing metrics when they are not necessary
            self.conf_matrix = conf_matrix
            self.conts_per_class = [0] * self.total_actions
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
        r = round_value_to_decimals
        teams_members_ids = [("("+str(p.program_id)+":"+str(p.generation)+")", p.action) for p in self.programs]
        teams_members_ids.sort(key=lambda tup: tup[1])
        m = str(self.team_id)+":"+str(self.generation)+", f: "+str(r(self.fitness))+", team size: "+str(len(self.programs))+", team members: "+str(teams_members_ids)
        m += "\nTRAIN: acc: "+str(r(self.accuracy_trainingset))+", mrecall: "+str(r(self.macro_recall_trainingset))
        m += "\nTEST: acc: "+str(r(self.accuracy_testset))+", mrecall: "+str(r(self.macro_recall_testset))+", recall: "+str(round_array_to_decimals(self.recall))
        return m

    def remove_programs_link(self):
        for p in self.programs:
            p.remove_team(self)

    def mutate(self, new_programs):
        """ Generates mutation chances and mutate the team if it is a valid mutation """
        mutation_chance = random.random()
        if mutation_chance <= CONFIG['training_parameters']['mutation']['team']['remove_program']:
            self.remove_program()
        if len(self.programs) < CONFIG['training_parameters']['team_size']['max']:
            mutation_chance = random.random()
            if mutation_chance <= CONFIG['training_parameters']['mutation']['team']['add_program']:
                self.add_program(new_programs)          

    def remove_program(self):
        """ Remove a program from the team. A program is removible only if there is at least two programs for its action. """
        # Get list of actions with more than one program
        actions = [p.action for p in self.programs]
        actions_count = Counter(actions)
        valid_actions_to_remove = []
        for key, value in actions_count.iteritems():
            if value > 1:
                valid_actions_to_remove.append(key)
        if len(valid_actions_to_remove) == 0:
            return
        # Get list of programs for the removible actions
        valid_programs_to_remove = [p for p in self.programs if p.action in valid_actions_to_remove]
        # Randomly select a program to remove from the list
        removed_program = random.choice(valid_programs_to_remove)
        removed_program.remove_team(self)
        self.programs.remove(removed_program)

    def add_program(self, new_programs):
        if len(new_programs) == 0:
            print "WARNING! NO NEW PROGRAMS!"
            return
        test = False
        while not test:
            new_program = random.choice(new_programs)
            if new_program not in self.programs:
                new_program.add_team(self)
                self.programs.append(new_program)
                test = True

    def get_programs_per_class(self, programs):
        programs_per_class = []
        for class_index in range(self.total_actions):
            values = [p for p in programs if p.action == class_index]
            if len(values) == 0:
                print "WARNING! No programs for class "+str(class_index)
                raise Exception
            programs_per_class.append(values)
        return programs_per_class

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


