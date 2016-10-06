import abc
import random
import copy
import numpy
from collections import defaultdict
from reinforcement_metrics import ReinforcementMetrics
from ..default_environment import DefaultEnvironment
from ..default_point import  reset_points_ids
from ...core.team import Team
from ...core.diversity_maintenance import DiversityMaintenance
from ...core.pareto_dominance_for_teams import ParetoDominanceForTeams
from ...utils.helpers import round_value, flatten 
from ...config import Config

class ReinforcementEnvironment(DefaultEnvironment):

    __metaclass__  = abc.ABCMeta

    @abc.abstractmethod
    def _play_match(self, team, opponent, point, mode, match_id):
        """
        To be implemented via inheritance.
        """

    def __init__(self, total_actions, total_inputs, total_labels, coded_opponents_for_training, 
            coded_opponents_for_validation, point_class):
        self.total_actions_ = total_actions
        self.total_inputs_ = total_inputs
        self.total_labels_ = total_labels

        if not coded_opponents_for_training:
            coded_opponents_for_training = [opponent_factory("DummyOpponent", 'dummy')]
        self.coded_opponents_for_training_ = coded_opponents_for_training
        if not coded_opponents_for_validation:
            coded_opponents_for_validation = [opponent_factory("DummyOpponent", 'dummy')]
        self.coded_opponents_for_validation_ = coded_opponents_for_validation

        self.point_class = point_class

        Config.RESTRICTIONS['total_actions'] = self.total_actions_
        Config.RESTRICTIONS['total_raw_actions'] = self.total_actions_
        Config.RESTRICTIONS['total_inputs'] = self.total_inputs_

        Config.RESTRICTIONS['use_memmory_for_actions'] = False # since the task is reinforcement learning, there is a lot of actions per point, instead of just one
        
        self.opponent_names_for_training_ = [c.OPPONENT_ID for c in self.coded_opponents_for_training_]
        if Config.USER['reinforcement_parameters']['hall_of_fame']['opponents'] > 0:
            self.opponent_names_for_training_.append('hall_of_fame')
        self.opponent_names_for_validation_ = [c.OPPONENT_ID for c in self.coded_opponents_for_validation_]

        self.matches_per_opponent_per_generation_ = None
        self._ensure_balanced_population_size_for_training()
        self._ensure_balanced_population_size_for_testing('validation_population')
        self._ensure_balanced_population_size_for_testing('champion_population')

        self.team_to_add_to_hall_of_fame_ = None
        self.opponent_population_ = None
        self.point_population_ = []
        self.validation_point_population_ = None
        self.champion_point_population_ = None
        self.champion_point_population_for_hall_of_fame_ = None
        self.training_opponent_population_ = None
        self.validation_opponent_population_ = None
        self.champion_opponent_population_ = None
        self.first_sampling_ = True
        self.samples_per_class_to_keep_ = []
        self.samples_per_class_to_remove_ = []
        self.champion_matches_per_hall_of_fame_opponent_ = 20
        self.current_hall_of_fame_opponents_ = []
        self.metrics_ = ReinforcementMetrics(self)

    def _ensure_balanced_population_size_for_training(self):
        pop_size = Config.USER['training_parameters']['populations']['points']
        total_opponents = len(self.coded_opponents_for_training_)
        if Config.USER['reinforcement_parameters']['hall_of_fame']['opponents'] > 0:
            total_opponents += Config.USER['reinforcement_parameters']['hall_of_fame']['opponents']
        temp = total_opponents*self.total_labels_
        pop_size = (pop_size/temp)*temp
        self.matches_per_opponent_per_generation_ = pop_size/total_opponents
        Config.USER['training_parameters']['populations']['points'] = pop_size

    def _ensure_balanced_population_size_for_testing(self, population_key):
        pop_size = Config.USER['reinforcement_parameters'][population_key]
        temp = len(self.coded_opponents_for_validation_)*self.total_labels_
        pop_size = (pop_size/temp)*temp
        Config.USER['reinforcement_parameters'][population_key] = pop_size

    def champion_population(self):
        if Config.USER['reinforcement_parameters']['hall_of_fame']['enabled']:
            return self.champion_point_population_ + self.champion_point_population_for_hall_of_fame_
        else:
            return self.champion_point_population_

    def champion_opponent_population(self):
        if Config.USER['reinforcement_parameters']['hall_of_fame']['enabled']:
            temp = self.opponent_population_['hall_of_fame']*self.champion_matches_per_hall_of_fame_opponent_
            return self.champion_opponent_population_ + temp
        else:
            return self.champion_opponent_population_

    def training_opponent_population(self):
        if Config.USER['reinforcement_parameters']['hall_of_fame']['enabled']:
            return self.training_opponent_population_ + self.current_hall_of_fame_opponents_
        else:
            return self.training_opponent_population_

    def reset(self):
        reset_points_ids()
        self._initialize_opponent_population()
        self.point_population_ = []
        self.team_to_add_to_hall_of_fame_ = None
        self.validation_point_population_ = self._initialize_random_population_of_points(
            Config.USER['reinforcement_parameters']['validation_population'], ignore_cache = True)
        if Config.USER['reinforcement_parameters']['hall_of_fame']['opponents'] > 0:
            size = (Config.USER['reinforcement_parameters']['champion_population']
                + Config.USER['reinforcement_parameters']['hall_of_fame']['size'] 
                * self.champion_matches_per_hall_of_fame_opponent_)
            population = self._initialize_random_population_of_points(size, ignore_cache = True)
            self.champion_point_population_ = population[:Config.USER['reinforcement_parameters']['champion_population']]
            self.champion_point_population_for_hall_of_fame_ = population[Config.USER['reinforcement_parameters']['champion_population']:]
        else:
            self.champion_point_population_ = self._initialize_random_population_of_points(Config.USER['reinforcement_parameters']['champion_population'], ignore_cache = True)
        self.training_opponent_population_ = self._initialize_random_balanced_population_of_coded_opponents_for_training(Config.USER['training_parameters']['populations']['points'])
        self.validation_opponent_population_ = self._initialize_random_balanced_population_of_coded_opponents_for_validation(Config.USER['reinforcement_parameters']['validation_population'])
        self.champion_opponent_population_ = self._initialize_random_balanced_population_of_coded_opponents_for_validation(Config.USER['reinforcement_parameters']['champion_population'])
        self.first_sampling_ = True

    def _initialize_opponent_population(self):
        self.opponent_population_ = {}
        for opponent_class in self.coded_opponents_for_training_:
            self.opponent_population_[opponent_class.OPPONENT_ID] = [opponent_class()]
        if Config.USER['reinforcement_parameters']['hall_of_fame']['enabled']:
            self.opponent_population_['hall_of_fame'] = []

    def _initialize_random_population_of_points(self, population_size, ignore_cache = False):
        return [self.point_class() for index in range(population_size)]

    def _initialize_random_balanced_population_of_coded_opponents_for_training(self, population_size):
        population = []
        for opponent_class in self.coded_opponents_for_training_:
            for index in range(self.matches_per_opponent_per_generation_):
                population.append(opponent_class())
        return population

    def _initialize_random_balanced_population_of_coded_opponents_for_validation(self, population_size):
        population = []
        total_per_opponent = population_size/len(self.coded_opponents_for_validation_)
        for opponent_class in self.coded_opponents_for_validation_:
            for index in range(total_per_opponent):
                population.append(opponent_class())
        return population

    def setup(self, teams_population):
        """
        Setup the point and the opponent population.
        """
        # initialize point population
        if self.first_sampling_:
            self.first_sampling_ = False
            population = self._initialize_random_population_of_points(
                Config.USER['training_parameters']['populations']['points'], ignore_cache = False)
            subsets_per_label = self._get_data_per_label(population)
            total_samples_per_class = (Config.USER['training_parameters']['populations']['points']
                /self.total_labels_)
            balanced_subsets = []
            for subset in subsets_per_label:
                if len(subset) > total_samples_per_class:
                    subset = random.sample(subset, total_samples_per_class)
                balanced_subsets.append(subset)
            self.point_population_ = flatten(balanced_subsets)
        else: # uses attributes defined in evaluate_point_population()
            self._remove_points(self.samples_per_class_to_remove_, teams_population)
            self.point_population_ = self.samples_per_class_to_keep_
        random.shuffle(self.point_population_)
        
        # setup hall of fame
        if Config.USER['reinforcement_parameters']['hall_of_fame']['enabled']:
            hall_of_fame = self.opponent_population_['hall_of_fame']
            if self.team_to_add_to_hall_of_fame_:
                team_to_copy = self.team_to_add_to_hall_of_fame_
                copied_team = Team(team_to_copy.generation, list(team_to_copy.programs), 
                    team_to_copy.environment)
                copied_team.team_id_ = team_to_copy.team_id_
                copied_team.fitness_ = team_to_copy.fitness_
                copied_team.active_programs_ = list(team_to_copy.active_programs_)
                copied_team.validation_active_programs_ = list(team_to_copy.validation_active_programs_)
                copied_team.encodings_ = copy.deepcopy(team_to_copy.encodings_)
                copied_team.extra_metrics_ = dict(team_to_copy.extra_metrics_)
                copied_team.opponent_id = "hall_of_fame"
                hall_of_fame.append(copied_team)
                if len(hall_of_fame) > Config.USER['reinforcement_parameters']['hall_of_fame']['size']:
                    if Config.USER['reinforcement_parameters']['hall_of_fame']['diversity']:
                        novelty = Config.USER['reinforcement_parameters']['hall_of_fame']['diversity']
                        DiversityMaintenance.calculate_diversities_based_on_distances(hall_of_fame, 
                            k = Config.USER['reinforcement_parameters']['hall_of_fame']['size'], 
                            distances = [novelty])
                        keep_teams, remove_teams, pareto_front = ParetoDominanceForTeams.run(hall_of_fame, 
                            novelty, Config.USER['reinforcement_parameters']['hall_of_fame']['size'])
                        removed_point = [p for p in hall_of_fame if p == remove_teams[0]]
                        worst_point = removed_point[0]
                    else:
                        score = [p.fitness_ for p in hall_of_fame]
                        worst_point = hall_of_fame[score.index(min(score))]
                    self.opponent_population_['hall_of_fame'].remove(worst_point)
                self.team_to_add_to_hall_of_fame_ = None

        # add hall of fame opponents to opponent population
        if Config.USER['reinforcement_parameters']['hall_of_fame']['enabled']:
            if len(self.opponent_population_['hall_of_fame']) >= Config.USER['reinforcement_parameters']['hall_of_fame']['opponents']:
                options = list(self.opponent_population_['hall_of_fame'])
                self.current_hall_of_fame_opponents_ = []
                for option in range(Config.USER['reinforcement_parameters']['hall_of_fame']['opponents']):
                    opponent = random.choice(options)
                    options.remove(opponent)
                    self.current_hall_of_fame_opponents_ += [opponent]*self.matches_per_opponent_per_generation_

    def _remove_points(self, points_to_remove, teams_population):
        """
        Remove the points to remove from the teams, in order to save memory.
        """
        for team in teams_population:
            for point in points_to_remove:
                if point.point_id_ in team.results_per_points_:
                    team.results_per_points_.pop(point.point_id_)

    def evaluate_point_population(self, teams_population):
        """

        """
        for point in self.point_population_:
            point.age_ += 1

        current_subsets_per_class = self._get_data_per_label(self.point_population_)

        total_samples_per_class = Config.USER['training_parameters']['populations']['points']/self.total_labels_
        samples_per_class_to_keep = int(round(total_samples_per_class
            *(1.0-Config.USER['training_parameters']['replacement_rate']['points'])))
        samples_per_class_to_remove = total_samples_per_class - samples_per_class_to_keep

        total_points_to_add = (total_samples_per_class - samples_per_class_to_keep)*self.total_labels_
        points_to_add_per_label = self._points_to_add_per_label(total_points_to_add)

        kept_subsets_per_class = []
        removed_subsets_per_class = []

        # obtain the data points that will be kept and that will be removed for each subset using age
        for subset, points_to_add in zip(current_subsets_per_class, points_to_add_per_label):
            subset.sort(key=lambda x: x.age_, reverse=True)
            remove_solutions = subset[:samples_per_class_to_remove]
            keep_solutions = list(set(subset) - set(remove_solutions))
            kept_subsets_per_class.append(keep_solutions)
            removed_subsets_per_class.append(remove_solutions)

        for subset, points_to_add in zip(kept_subsets_per_class, points_to_add_per_label):
            subset += points_to_add

        self.samples_per_class_to_keep_ = flatten(kept_subsets_per_class)
        self.samples_per_class_to_remove_ = flatten(removed_subsets_per_class)

    def _points_to_add_per_label(self, total_points_to_add):
        """
        This method only works if there is only one label. For more than one label you should 
        overhide it in the class that inherits this class.
        """
        points_to_add = [self.point_class() for x in range(total_points_to_add)]
        return [points_to_add]

    def _get_data_per_label(self, point_population):
        subsets_per_class = []
        for label_index in range(self.total_labels_):
            values = [point for point in point_population if point.label_ == label_index]
            subsets_per_class.append(values)
        return subsets_per_class

    def evaluate_teams_population_for_training(self, teams_population):
        for team in teams_population:
            team.encodings_['encoding_for_pattern_of_actions_per_match'] = []
            team.encodings_['encoding_for_actions_per_match'] = []
            team.encodings_['encoding_custom_info_per_match'] = []
            self.evaluate_team(team, Config.RESTRICTIONS['mode']['training'])
        
        if Config.USER['reinforcement_parameters']['hall_of_fame']['enabled']:
            sorted_teams = sorted(teams_population, key=lambda team: team.fitness_, reverse = True) # better ones first
            team_ids = [p.team_id_ for p in self.opponent_population_['hall_of_fame']]
            for team in sorted_teams:
                if team.team_id_ not in team_ids:
                    self.team_to_add_to_hall_of_fame_ = team
                    break

    def evaluate_team(self, team, mode):
        """
        Each team plays 2 matches against each point in the point population.
        One match as the player 1, another as player 2. The final score is 
        the mean of the scores in the matches (1: win, 0.5: draw, 0: lose)
        """
        if mode == Config.RESTRICTIONS['mode']['training']:
            point_population = self.point_population_
            opponent_population = self.training_opponent_population()
            results = []
            extra_metrics_opponents = defaultdict(list)
            match_id = 0

            if len(point_population) == 0:
                raise ValueError("Error: Nothing in point population. Probably the population size is too small.")
            if len(opponent_population) == 0:
                raise ValueError("Error: Nothing in opponent population. Probably the population size is too small.")

            for point, opponent in zip(point_population, opponent_population):
                match_id += 1
                result = self._play_match(team, opponent, point, mode, match_id)
                team.reset_registers()
                extra_metrics_opponents[opponent.opponent_id].append(result)
                team.results_per_points_[point.point_id_] = result
                results.append(result)
                if opponent.opponent_id == 'hall_of_fame': # since the hall of fame changes over time, it is better to dont use it to get the champion score, since you wouldnt be able to track the score improvement
                    extra_metrics_opponents[opponent.__repr__()].append(result)
            for key in extra_metrics_opponents:
                extra_metrics_opponents[key] = round_value(numpy.mean(extra_metrics_opponents[key]))
            team.extra_metrics_['training_opponents'] = extra_metrics_opponents
            team.fitness_ = numpy.mean(results)
        else:
            if mode == Config.RESTRICTIONS['mode']['validation']:
                point_population = self.validation_point_population_
                opponent_population = self.validation_opponent_population_
            elif mode == Config.RESTRICTIONS['mode']['champion']:
                point_population = self.champion_population()
                opponent_population = self.champion_opponent_population()
            else:
                raise ValueError("Invalid mode")
            results = []
            extra_metrics_opponents = defaultdict(list)
            extra_metrics_points = self._initialize_extra_metrics_for_points()
            match_id = 0

            if len(point_population) == 0:
                raise ValueError("Error: Nothing in point population. Probably the population size is too small.")
            if len(opponent_population) == 0:
                raise ValueError("Error: Nothing in opponent population. Probably the population size is too small.")

            for point, opponent in zip(point_population, opponent_population):
                match_id += 1
                result = self._play_match(team, opponent, point, mode, match_id)
                team.reset_registers()
                extra_metrics_opponents[opponent.opponent_id].append(result)
                extra_metrics_points = self._update_extra_metrics_for_points(extra_metrics_points, point, result)
                if mode == Config.RESTRICTIONS['mode']['validation']:
                    team.results_per_points_for_validation_[point.point_id_] = result
                    results.append(result)
                elif mode == Config.RESTRICTIONS['mode']['champion']:
                    if opponent.opponent_id != 'hall_of_fame': # since the hall of fame changes over time, it is better to dont use it to get the champion score, since you wouldnt be able to track the score improvement
                        results.append(result)
                    else:
                        extra_metrics_opponents[opponent.__repr__()].append(result)
            for key in extra_metrics_opponents:
                extra_metrics_opponents[key] = round_value(numpy.mean(extra_metrics_opponents[key]))
            team.extra_metrics_['opponents'] = extra_metrics_opponents
            for key in extra_metrics_points:
                for subkey in extra_metrics_points[key]:
                    extra_metrics_points[key][subkey] = round_value(numpy.mean(extra_metrics_points[key][subkey]))
            team.extra_metrics_['points'] = extra_metrics_points
            if mode == Config.RESTRICTIONS['mode']['validation']:
                team.score_validation_ = round_value(numpy.mean(results))
            else:
                team.score_champion_ = round_value(numpy.mean(results))

    def _initialize_extra_metrics_for_points(self):
        return {}

    def _update_extra_metrics_for_points(self, extra_metrics_points, point, result):
        return extra_metrics_points

    def validate(self, current_generation, teams_population):
        print "\nvalidating all..."
        for team in teams_population:
            if team.generation != current_generation: # dont evaluate teams that have just being created (to improve performance and to get training metrics)
                team.results_per_points_for_validation_ = {}
                self.evaluate_team(team, Config.RESTRICTIONS['mode']['validation'])
                team.extra_metrics_['validation_opponents'] = team.extra_metrics_['opponents']
                team.extra_metrics_['validation_points'] = team.extra_metrics_['points']
                team.extra_metrics_.pop('champion_score', None)
                team.extra_metrics_.pop('champion_opponents', None)
                team.extra_metrics_.pop('champion_points', None)
        score = [p.score_validation_ for p in teams_population]
        best_team = teams_population[score.index(max(score))]
        print "\nvalidating champion..."
        self.evaluate_team(best_team, Config.RESTRICTIONS['mode']['champion'])
        best_team.extra_metrics_['champion_opponents'] = best_team.extra_metrics_['opponents']
        best_team.extra_metrics_['champion_points'] = best_team.extra_metrics_['points']
        return best_team

    def hall_of_fame(self):
        if 'hall_of_fame' in self.opponent_population_:
            return [p for p in self.opponent_population_['hall_of_fame']]
        else:
            return []