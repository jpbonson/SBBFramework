import random
import numpy
from collections import Counter
from program import Program
from environments.classification_environment import ClassificationEnvironment
from utils.helpers import round_value_to_decimals, round_array_to_decimals
from config import CONFIG, RESTRICTIONS

def reset_teams_ids():
    global next_team_id
    next_team_id = 0

def get_team_id():
    global next_team_id
    next_team_id += 1
    return next_team_id

class Team:
    def __init__(self, generation, programs):
        self.team_id = get_team_id()
        self.generation = generation
        self.fitness = -1
        self.score_trainingset = -1
        self.score_testset = -1
        self.extra_metrics = {}
        self.programs = []
        self.active_programs = []
        for program in programs:
            self.programs.append(program)
            program.add_team(self)

    def execute(self, input_registers):
        partial_outputs = []
        for program in self.programs:
            partial_outputs.append(program.execute(input_registers))
        selected_program = self.programs[partial_outputs.index(max(partial_outputs))]
        output_class = selected_program.action
        if selected_program.program_id not in self.active_programs:
            self.active_programs.append(selected_program.program_id)
        return output_class

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

    def print_metrics(self):
        r = round_value_to_decimals
        teams_members_ids = [p.__repr__() for p in self.programs]
        m = str(self.team_id)+":"+str(self.generation)+", team members ("+str(len(self.programs))+"): "+str(teams_members_ids)
        # m += "\nTRAIN: acc: "+str(r(self.accuracy_trainingset)) +", mrecall: "+str(r(self.score_trainingset))
        # m += "\nTEST: acc: "+str(r(self.accuracy_testset))+", mrecall: "+str(r(self.score_testset))+", recall: "+str(round_array_to_decimals(self.recall))
        m += "\nfitness (train): "+str(r(self.fitness))+", score (train): "+str(r(self.score_trainingset))+", score (test): "+str(r(self.score_testset))
        #  print extra_metrics (versao sem verbose ser sem extra_metrics e sem action_counter?)
        return m

    def __repr__(self): 
        return "("+str(self.team_id)+":"+str(self.generation)+")"

    def __str__(self):
        text = "\nTeam "+self.__repr__()+", team size: "+str(len(self.programs))
        text += "\n################"
        for p in self.programs:
            text += "\n"+str(p)
        text += "\n################"
        return text


