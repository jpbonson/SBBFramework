import random
import copy
import json
from collections import Counter, defaultdict
from program import Program
from ..environments.default_opponent import DefaultOpponent
from ..utils.helpers import round_value, round_array
from ..config import Config

def reset_teams_ids():
    global next_team_id
    next_team_id = 0

def get_team_id():
    global next_team_id
    next_team_id += 1
    return next_team_id

class Team(DefaultOpponent):
    def __init__(self, generation, programs):
        super(Team, self).__init__("sbb")
        self.generation = generation
        self.programs = []
        for program in programs:
            self._add_program(program)
        self.team_id_ = get_team_id()
        self.fitness_ = 0
        self.score_testset_ = 0
        self.extra_metrics_ = {}
        self.active_programs_ = [] # only for training, used for genotype diversity
        self.overall_active_programs_ = [] # for training and validation
        self.memory_actions_per_points_ = {}
        self.results_per_points_ = {}
        self.results_per_points_for_validation_ = {}
        self.diversity_ = {}
        self.action_sequence_ = {} # only used by reinforcement learning

    def _add_program(self, program):
        self.programs.append(program)
        program.add_team(self)

    def initialize(self, seed):
        """
        This method is called by the reinforcement learning environments to set 
        the opponent configurations before a match. This class implements this 
        method only in order to be transparent if the opponent is a sbb or 
        a coded opponent.
        """
        pass
        
    def execute(self, point_id_, inputs, valid_actions, is_training):
        if not self._actions_are_available(valid_actions):
            return None

        # if there is a least one program that can produce a valid action, execute the programs
        if is_training:
            # update profile
            if len(Config.RESTRICTIONS['profile']['samples']) < Config.RESTRICTIONS['profile']['samples'].maxlen:
                # add everything until it is full
                Config.RESTRICTIONS['profile']['samples'].append(inputs)
            else:
                # give a chance of adding or not
                if random.random() < Config.RESTRICTIONS['profile']['update_chance']:
                    Config.RESTRICTIONS['profile']['samples'].append(inputs)

            # run the programs
            if Config.RESTRICTIONS['use_memmory_for_actions'] and point_id_ in self.memory_actions_per_points_:
                return self.memory_actions_per_points_[point_id_]
            else:
                selected_program = self._select_program(inputs, valid_actions)
                output_class = selected_program.action
                if Config.RESTRICTIONS['use_memmory_for_actions']:
                    self.memory_actions_per_points_[point_id_] = output_class
                if selected_program not in self.active_programs_:
                    self.active_programs_.append(selected_program)
                if selected_program not in self.overall_active_programs_:
                    self.overall_active_programs_.append(selected_program)
                return output_class
        else: # just run the code without changing the attributes or using memmory
            selected_program = self._select_program(inputs, valid_actions)
            if selected_program not in self.overall_active_programs_:
                self.overall_active_programs_.append(selected_program)
            return selected_program.action

    def _actions_are_available(self, valid_actions):
        """
        Test if there are at least one program in the team that is able to provide a valid action
        If there is no such program, return None, so that the environment will use a default action
        """
        actions = [p.action for p in self.programs]
        possible_action = set(actions).intersection(valid_actions)
        if len(possible_action) == 0:
            return False
        return True

    def _select_program(self, inputs, valid_actions):
        """
        Generates the outputs for all programs and order them. The team checks if the first 
        action is valid before submitting it to the environment. If it is not valid, then 
        the second best action will be tried, and so on until a valid action is obtained.
        """
        partial_outputs = []
        valid_programs = []
        for program in self.programs:
            if program.action in valid_actions:
                partial_outputs.append(program.execute(inputs))
                valid_programs.append(program)
        selected_program = valid_programs[partial_outputs.index(max(partial_outputs))]
        return selected_program

    def generate_profile(self):
        profile = []
        for inputs in Config.RESTRICTIONS['profile']['samples']:
            partial_outputs = []
            valid_programs = []
            for program in self.programs:
                partial_outputs.append(program.execute(inputs))
                valid_programs.append(program)
            selected_program = valid_programs[partial_outputs.index(max(partial_outputs))]
            profile.append(selected_program.action)
        return profile

    def mutate(self, programs_population):
        """
        Generates mutation chances and mutate the team if it is a valid mutation.
        """
        if len(self.programs) > Config.USER['training_parameters']['team_size']['min']:
            mutation_chance = random.random()
            if mutation_chance <= Config.USER['training_parameters']['mutation']['team']['remove_program']:
                self._randomly_remove_program()

        if len(self.programs) < Config.USER['training_parameters']['team_size']['max']:
            mutation_chance = random.random()
            if mutation_chance <= Config.USER['training_parameters']['mutation']['team']['add_program']:
                self._randomly_add_program(programs_population)

        to_mutate = []
        while len(to_mutate) == 0:
            for program in self.programs:
                mutation_chance = random.random()
                if mutation_chance <= Config.USER['training_parameters']['mutation']['team']['mutate_program']:
                    to_mutate.append(program)
        for program in to_mutate:
            clone = Program(self.generation, copy.deepcopy(program.instructions), program.action)
            clone.mutate()
            self._add_program(clone)
            programs_population.append(clone)
            if self._is_ok_to_remove(program):
                self.remove_program(program)
        return programs_population

    def _randomly_remove_program(self):
        """
        Remove a program from the team. A program can be removed only if removing it will maintain ['team_size']['min'] distinct actions in the team.
        """
        while True:
            candidate_to_remove = random.choice(self.programs)
            if self._is_ok_to_remove(candidate_to_remove):
                self.remove_program(candidate_to_remove)
                return

    def _is_ok_to_remove(self, program_to_remove):
        actions = [p.action for p in self.programs]
        actions.remove(program_to_remove.action)
        if len(set(actions)) >= Config.USER['training_parameters']['team_size']['min']:
            return True
        return False

    def _randomly_add_program(self, programs_population):
        self._add_program(random.choice(programs_population))

    def remove_program(self, program):
        program.remove_team(self)
        self.programs.remove(program)
        if program in self.active_programs_:
            self.active_programs_.remove(program)
        if program in self.overall_active_programs_:
            self.overall_active_programs_.remove(program)

    def remove_references(self):
        """
        Remove all references from this object to other objects, so it can be safely deleted.
        """
        for p in self.programs:
            p.remove_team(self)

    def prune_partial(self):
        inactive_programs = list(set(self.programs) - set(self.active_programs_))
        while len(inactive_programs) > 0:
            candidate_to_remove = random.choice(inactive_programs)
            if self._is_ok_to_remove(candidate_to_remove):
                self.remove_program(candidate_to_remove)
                return
            else:
                inactive_programs.remove(candidate_to_remove)

    def prune_total(self):
        inactive_programs = list(set(self.programs) - set(self.active_programs_))
        for program in inactive_programs:
            self.remove_program(program)

    def metrics(self, full_version = False):
        overall_active_teams_members_ids = [p.__repr__() for p in self.overall_active_programs_]
        overall_inactive_programs = list(set(self.programs) - set(self.overall_active_programs_))
        overall_inactive_teams_members_ids = [p.__repr__() for p in overall_inactive_programs]
        active_teams_members_ids = [p.__repr__() for p in self.active_programs_]
        inactive_programs = list(set(self.programs) - set(self.active_programs_))
        inactive_teams_members_ids = [p.__repr__() for p in inactive_programs]
        msg = self.__repr__()
        msg += "\nteam members ("+str(len(self.programs))+"), A: "+str(overall_active_teams_members_ids)+", I: "+str(overall_inactive_teams_members_ids)
        msg += "\n- training only, A: "+str(active_teams_members_ids)+", I: "+str(inactive_teams_members_ids)
        msg += "\nfitness: "+str(round_value(self.fitness_))+", test score: "+str(round_value(self.score_testset_))
        msg += "\ninputs distribution: "+str(self.inputs_distribution())
        if Config.USER['task'] == 'classification' and self.extra_metrics_:
            msg += "\nrecall per action: "+str(self.extra_metrics_['recall_per_action'])
        if Config.USER['task'] == 'reinforcement' and self.extra_metrics_:
            msg += "\nlast opponent played against (training): "+self.extra_metrics_['last_training_opponent']
            if Config.USER['reinforcement_parameters']['environment'] == 'poker':
                if 'total_hands' in self.extra_metrics_:
                    if self.extra_metrics_['total_hands']['validation'] > 0:
                        msg += self._hand_player_metrics('validation')
                    if self.extra_metrics_['total_hands']['champion'] > 0:
                        msg += self._hand_player_metrics('champion')
                if 'agressiveness' in self.extra_metrics_:
                    msg += "\n\nagressiveness: "+str(self.extra_metrics_['agressiveness'])
                    msg += "\nvolatility: "+str(self.extra_metrics_['volatility'])
                if 'agressiveness_champion' in self.extra_metrics_:
                    msg += "\nagressiveness (champion): "+str(self.extra_metrics_['agressiveness_champion'])
                    msg += "\nvolatility (champion): "+str(self.extra_metrics_['volatility_champion'])

                if 'validation_points' in self.extra_metrics_:
                    msg += "\n\nscore per point (validation): "
                    for key in self.extra_metrics_['validation_points']:
                        msg += "\n"+key+": "+str(dict(self.extra_metrics_['validation_points'][key]))

                if 'champion_score' in self.extra_metrics_:
                    msg += "\n\nscore per point (champion): "
                    for key in self.extra_metrics_['champion_points']:
                        msg += "\n"+key+": "+str(dict(self.extra_metrics_['champion_points'][key]))

            if 'champion_score' in self.extra_metrics_:
                msg += "\n\nscore per opponent (champion): "+str(self.extra_metrics_['champion_score'])
                for key in self.extra_metrics_['opponents']:
                    msg += "\n"+key+": "+str(self.extra_metrics_['champion_opponents'][key])
        if full_version:
            if Config.USER['task'] == 'classification' and self.extra_metrics_:
                msg += "\n\naccuracy: "+str(round_value(self.extra_metrics_['accuracy']))
                msg += "\n\nconfusion matrix:\n"+str(self.extra_metrics_['confusion_matrix'])
            if Config.USER['task'] == 'reinforcement' and 'validation_score' in self.extra_metrics_:
                msg += "\n\nscore per opponent (validation): "+str(self.extra_metrics_['validation_score'])
                for key in self.extra_metrics_['validation_opponents']:
                    msg += "\n"+key+": "+str(self.extra_metrics_['validation_opponents'][key])
            msg += "\n"
            for key, value in self.diversity_.iteritems():
                msg +=  "\n"+str(key)+": "+str(value)
        return msg

    def inputs_distribution(self):
        inputs = []
        for program in self.active_programs_:
            inputs += program.inputs_list_
        inputs_distribution = Counter(inputs)
        return inputs_distribution

    def _hand_player_metrics(self, mode):
        msg = ""
        msg += "\n\nhands ("+mode+"):"
        a = round_value(self.extra_metrics_['hand_played'][mode]/float(self.extra_metrics_['total_hands'][mode]))
        b = None
        if self.extra_metrics_['hand_played'][mode] > 0:
            b = round_value(self.extra_metrics_['won_hands'][mode]/float(self.extra_metrics_['hand_played'][mode]))
        msg += "\ntotal: "+str(self.extra_metrics_['total_hands'][mode])+", played: "+str(a)+", won: "+str(b)
        for metric in self.extra_metrics_['total_hands_per_point_type'][mode]:
            for key in self.extra_metrics_['total_hands_per_point_type'][mode][metric]:
                a = self.extra_metrics_['total_hands_per_point_type'][mode][metric][key]
                b = None
                c = None
                if a > 0:
                    b = round_value(self.extra_metrics_['hand_played_per_point_type'][mode][metric][key]/float(self.extra_metrics_['total_hands_per_point_type'][mode][metric][key]))
                    if self.extra_metrics_['hand_played_per_point_type'][mode][metric][key] > 0:
                        c = round_value(self.extra_metrics_['won_hands_per_point_type'][mode][metric][key]/float(self.extra_metrics_['hand_played_per_point_type'][mode][metric][key]))
                msg += "\n"+str(metric)+", "+str(key)+" ("+str(a)+"): played: "+str(b)+", won: "+str(c)
        return msg

    def json(self):
        programs_json = []
        for program in self.programs:
            programs_json.append(program.dict())
        return json.dumps(programs_json)

    def __repr__(self): 
        return "("+str(self.team_id_)+"-"+str(self.generation)+")"

    def __str__(self):
        text = "TEAM "+self.__repr__()
        text += "\n\n#### METRICS\n"
        text += self.metrics(full_version = True)
        text += "\n\n######## PROGRAMS (ACTIVE)"
        for p in self.active_programs_:
            text += "\n"+str(p)
        text += "\n\n######## PROGRAMS (INACTIVE)"
        inactive_programs = list(set(self.programs) - set(self.active_programs_))
        if inactive_programs:
            for p in inactive_programs:
                text += "\n"+str(p)
        else:
            text += "\n[No inactive programs]"
        return text