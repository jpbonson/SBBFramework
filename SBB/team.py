import random
from collections import Counter
from utils.helpers import round_value, round_array_to_decimals
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
        self.generation = generation
        self.programs = []
        for program in programs:
            self._add_program(program)
        self.team_id_ = get_team_id()
        self.fitness_ = -1
        self.score_trainingset_ = -1
        self.score_testset_ = -1
        self.extra_metrics_ = {}
        self.active_programs_ = []
        self.actions_per_points_ = {}
        self.results_per_points_ = {}

    def _add_program(self, program):
        self.programs.append(program)
        program.add_team(self)

    def _remove_program(self, program):
        program.remove_team(self)
        self.programs.remove(program)
        
    def execute(self, point_id, inputs, is_valid_action, is_training):
        if is_training:
            if RESTRICTIONS['use_memmory'] and point_id in self.actions_per_points_:
                return self.actions_per_points_[point_id]
            else:
                selected_program = self._select_program(inputs, is_valid_action)
                output_class = selected_program.action
                if RESTRICTIONS['use_memmory']:
                    self.actions_per_points_[point_id] = output_class
                if selected_program.program_id_ not in self.active_programs_:
                    self.active_programs_.append(selected_program.program_id_)
                return output_class
        else: # just run the code without changing the attributes or using memmory
            selected_program = self._select_program(inputs, is_valid_action)
            return selected_program.action

    def _select_program(self, inputs, is_valid_action):
        """
        Generates the outputs for all programs and order them. The team checks if the first 
        action is valid before submitting it to the environment. If it is not valid, then 
        the second best action will be tried, and so on until a valid action is obtained.
        """
        partial_outputs = []
        for program in self.programs:
            partial_outputs.append(program.execute(inputs))
        sorted_programs_indeces = sorted(range(len(partial_outputs)), key=lambda k: partial_outputs[k], reverse=True)
        for index in sorted_programs_indeces:
            selected_program = self.programs[index]
            if is_valid_action(selected_program.action):
                return selected_program
        raise ValueError("Team "+self.__repr__()+" wasn't able to output any valid action. You got a bug!")

    def mutate(self, new_programs):
        """
        Generates mutation chances and mutate the team if it is a valid mutation
        """
        mutation_chance = random.random()
        if mutation_chance <= CONFIG['training_parameters']['mutation']['team']['remove_program']:
            self._randomly_remove_program()
        if len(self.programs) < CONFIG['training_parameters']['team_size']['max']:
            mutation_chance = random.random()
            if mutation_chance <= CONFIG['training_parameters']['mutation']['team']['add_program']:
                self._randomly_add_program(new_programs)          

    def _randomly_remove_program(self):
        """
        Remove a program from the team. A program is removible only if there is at least two programs for its action
        """
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
        self._remove_program(removed_program)

    def _randomly_add_program(self, new_programs):
        if len(new_programs) == 0:
            print "Warning! No new programs to add from this generation! If this warning is occuring often you probably got a bug."
            return
        self._add_program(random.choice(new_programs))

    def remove_references(self):
        """
        Remove all references from this object to other objects, so it can be safely deleted.
        """
        for p in self.programs:
            p.remove_team(self)

    def metrics(self, full_version = False):
        teams_members_ids = [p.__repr__() for p in self.programs]
        msg = str(self.team_id_)+":"+str(self.generation)
        msg += "\nteam members ("+str(len(self.programs))+"): "+str(teams_members_ids)
        msg += "\nfitness (train): "+str(round_value(self.fitness_))+", score (train): "+str(round_value(self.score_trainingset_))+", score (test): "+str(round_value(self.score_testset_))
        if CONFIG['task'] == 'classification':
            msg += "\nrecall per action: "+str(self.extra_metrics_['recall_per_action'])
        if full_version:
            if CONFIG['task'] == 'classification':
                msg += "\n\naccuracy: "+str(round_value(self.extra_metrics_['accuracy']))
                msg += "\n\nconfusion matrix:\n"+str(self.extra_metrics_['confusion_matrix'])
        return msg

    def __repr__(self): 
        return "("+str(self.team_id_)+":"+str(self.generation)+")"

    def __str__(self):
        text = "Team "+self.__repr__()+", team size: "+str(len(self.programs))
        text += "\n################"
        for p in self.programs:
            text += "\n"+str(p)
        text += "\n################"
        return text