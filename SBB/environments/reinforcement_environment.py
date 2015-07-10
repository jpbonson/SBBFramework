import abc
import random
import copy
import numpy
from collections import defaultdict
from default_environment import DefaultEnvironment, DefaultPoint
from ..diversity_maintenance import DiversityMaintenance
from ..pareto_dominance import ParetoDominance
from ..utils.helpers import round_value, flatten
from ..config import Config

class ReinforcementPoint(DefaultPoint):
    """
    
    """
    __metaclass__  = abc.ABCMeta

    def __init__(self, point_id, opponent):
        super(ReinforcementPoint, self).__init__(point_id)
        self.opponent = opponent

class ReinforcementEnvironment(DefaultEnvironment):
    """
    
    """
    __metaclass__  = abc.ABCMeta

    @abc.abstractmethod
    def _instantiate_point_for_coded_opponent_class(self, opponent_class):
        """
        
        """

    @abc.abstractmethod
    def _instantiate_point_for_sbb_opponent(self, team):
        """
        
        """

    @abc.abstractmethod
    def _play_match(self, team, point, is_training):
        """
        
        """

    def __init__(self, total_actions, total_inputs, coded_opponents_for_training, coded_opponents_for_validation):
        self.total_actions_ = total_actions
        self.total_inputs_ = total_inputs
        self.coded_opponents_for_training_ = coded_opponents_for_training
        self.coded_opponents_for_validation_ = coded_opponents_for_validation
        self.opponent_class_mapping_ = {}
        for opponent in self.coded_opponents_for_training_:
            self.opponent_class_mapping_[str(opponent)] = opponent
        Config.RESTRICTIONS['total_actions'] = self.total_actions_
        Config.RESTRICTIONS['total_inputs'] = self.total_inputs_
        self.team_to_add_to_hall_of_fame_ = None
        self.test_population_ = None
        self.champion_population_ = None
        self.first_sampling_ = True
        self.last_population_ = None
        self.current_population_ = None
        self.samples_per_opponent_to_keep_ = {}
        self.samples_per_opponent_to_remove_ = {}
        Config.RESTRICTIONS['use_memmory_for_actions'] = False # since the task is reinforcement learning, there is a lot of actions per point, instead of just one
        Config.RESTRICTIONS['use_memmory_for_results'] = True # since the opponents are seeded, the same point will always produce the same final result
        self.point_population_size_per_opponent_, self.total_opponents_, self.point_population_per_opponent_ = self._get_balanced_metrics()
        Config.USER['training_parameters']['populations']['points'] = self.point_population_size_per_opponent_*self.total_opponents_
        if Config.USER['reinforcement_parameters']['balanced_opponent_populations']:
            self.population_size_ = self.point_population_size_per_opponent_
        else:
            if Config.USER['reinforcement_parameters']['opponents_pool'] != 'only_coded':
                if Config.USER['training_parameters']['populations']['points'] > Config.USER['training_parameters']['populations']['teams']:
                    Config.USER['training_parameters']['populations']['points'] = Config.USER['training_parameters']['populations']['teams']
            self.population_size_ = Config.USER['training_parameters']['populations']['points']
    
    def _get_balanced_metrics(self):
        """
        Ensure the matches per opponents are balanced across opponents, and that no more than the team population
        size is used as sbb opponents.
        """
        total_opponents = 0
        point_population_per_opponent = {}
        if Config.USER['reinforcement_parameters']['opponents_pool'] == 'only_sbb':
            total_opponents += 1
            point_population_per_opponent['sbb'] = []
        if Config.USER['reinforcement_parameters']['opponents_pool'] == 'only_coded':
            total_opponents += len(self.coded_opponents_for_training_)
            for opponent_class in self.coded_opponents_for_training_:
                point_population_per_opponent[str(opponent_class)] = []
        if Config.USER['reinforcement_parameters']['opponents_pool'] == 'hybrid':
            total_opponents += len(self.coded_opponents_for_training_)
            for opponent_class in self.coded_opponents_for_training_:
                point_population_per_opponent[str(opponent_class)] = []
            total_opponents += 1
            point_population_per_opponent['sbb'] = []
        if Config.USER['reinforcement_parameters']['hall_of_fame']['enabled']:
            total_opponents += 1
            point_population_per_opponent['hall_of_fame'] = []
        point_population_size_per_opponent = Config.USER['training_parameters']['populations']['points']/total_opponents
        if Config.USER['reinforcement_parameters']['opponents_pool'] == 'hybrid':
            if point_population_size_per_opponent > Config.USER['training_parameters']['populations']['teams']:
                point_population_size_per_opponent = Config.USER['training_parameters']['populations']['teams']
        return point_population_size_per_opponent, total_opponents, point_population_per_opponent

    def point_population(self):
        if Config.USER['reinforcement_parameters']['balanced_opponent_populations']:
            return flatten(self.point_population_per_opponent_.values())
        else:
            return self.point_population_per_opponent_[self.current_population_]

    def reset(self):
        for key in self.point_population_per_opponent_:
            self.point_population_per_opponent_[key] = []
        self.team_to_add_to_hall_of_fame_ = None
        self.test_population_ = self._initialize_random_balanced_population_of_coded_opponents_for_validation(Config.USER['reinforcement_parameters']['validation_population'])
        self.champion_population_ = self._initialize_random_balanced_population_of_coded_opponents_for_validation(Config.USER['reinforcement_parameters']['champion_population'])
        self.first_sampling_ = True
        self.last_population_ = None
        self.current_population_ = None

    def _initialize_random_balanced_population_of_coded_opponents_for_validation(self, population_size):
        population = []
        total_per_opponent = population_size/len(self.coded_opponents_for_validation_)
        for opponent_class in self.coded_opponents_for_validation_:
            for index in range(total_per_opponent):
                population.append(self._instantiate_point_for_coded_opponent_class(opponent_class))
        return population

    def setup(self, teams_population):
        """
        
        """
        if not Config.USER['reinforcement_parameters']['balanced_opponent_populations']:
            options = self.point_population_per_opponent_.keys()
            if Config.USER['reinforcement_parameters']['hall_of_fame']['enabled'] and len(self.point_population_per_opponent_['hall_of_fame']) == 0:
                options.remove('hall_of_fame')
            self.last_population_ = self.current_population_
            self.current_population_ = random.choice(options)

        if Config.USER['reinforcement_parameters']['opponents_pool'] == 'only_sbb':
            if len(self.point_population_per_opponent_['sbb']) > 0:
                self._remove_points(self.point_population_per_opponent_['sbb'], teams_population)
            self.point_population_per_opponent_['sbb'] = self._initialize_point_population_of_sbb_opponents(teams_population)
        else:
            if self.first_sampling_:
                self.first_sampling_ = False
                if Config.USER['reinforcement_parameters']['opponents_pool'] == 'only_coded':
                    self._initialize_point_population_per_opponent_for_coded_opponents()
                elif Config.USER['reinforcement_parameters']['opponents_pool'] == 'hybrid':
                    self._initialize_point_population_per_opponent_for_coded_opponents()
                    self.point_population_per_opponent_['sbb'] = self._initialize_point_population_of_sbb_opponents(teams_population)
            else: # uses attributes defined in evaluate_point_population() to update the point population
                self._remove_points(flatten(self.samples_per_opponent_to_remove_.values()), teams_population)
                if Config.USER['reinforcement_parameters']['opponents_pool'] == 'hybrid':
                    if not self.last_population_ or (self.last_population_ and self.last_population_ == 'sbb'):
                        if len(self.point_population_per_opponent_['sbb']) > 0:
                            self._remove_points(self.point_population_per_opponent_['sbb'], teams_population)
                        self.point_population_per_opponent_['sbb'] = self._initialize_point_population_of_sbb_opponents(teams_population)
                for key, values in self.samples_per_opponent_to_keep_.iteritems():
                    self.point_population_per_opponent_[key] = values

        if Config.USER['reinforcement_parameters']['hall_of_fame']['enabled']:
            hall_of_fame = self.point_population_per_opponent_['hall_of_fame']
            if self.team_to_add_to_hall_of_fame_ and self.team_to_add_to_hall_of_fame_ not in hall_of_fame:
                hall_of_fame.append(copy.deepcopy(self.team_to_add_to_hall_of_fame_))
                if len(hall_of_fame) > self.population_size_:
                    if Config.USER['reinforcement_parameters']['hall_of_fame']['use_genotype_diversity']:
                        teams = [p.opponent for p in hall_of_fame]
                        DiversityMaintenance.genotype_diversity(teams, p = 0.8, k = self.population_size_, use = True)
                    score = [p.opponent.fitness_ for p in hall_of_fame]
                    worst_team = hall_of_fame[score.index(min(score))]
                    self._remove_point_from_hall_of_fame(worst_team)

        self._check_for_bugs()

    def _initialize_point_population_of_sbb_opponents(self, teams_population):
        size = self.population_size_
        if size >= len(teams_population):
            sbb_opponents = teams_population
        else:
            fitness = [team.fitness_ for team in teams_population]
            total_fitness = sum(fitness)
            if total_fitness == 0:
                sbb_opponents = random.sample(teams_population, size)
            else:
                probabilities = [f/total_fitness for f in fitness]
                non_zeros = [p for p in probabilities if p != 0]
                if len(non_zeros) >= size:
                    sbb_opponents = numpy.random.choice(teams_population, size = size, replace = False, p = probabilities)
                else:
                    sbb_opponents = [team for team in teams_population if team.fitness_ != 0]
                    new_opponents = [team for team in teams_population if team.fitness_ == 0]
                    opponents_to_add = size - len(sbb_opponents)
                    sbb_opponents += random.sample(new_opponents, opponents_to_add)
        population = []
        for opponent in sbb_opponents:
            population.append(self._instantiate_point_for_sbb_opponent(opponent))
        return population

    def _initialize_point_population_per_opponent_for_coded_opponents(self):
        for opponent_class in self.coded_opponents_for_training_:
            for index in range(self.population_size_):
                self.point_population_per_opponent_[str(opponent_class)].append(self._instantiate_point_for_coded_opponent_class(opponent_class))

    def _remove_points(self, points_to_remove, teams_population):
        super(ReinforcementEnvironment, self)._remove_points(points_to_remove, teams_population)

    def _remove_point_from_hall_of_fame(self, point):
        self.point_population_per_opponent_['hall_of_fame'].remove(point)

    def _check_for_bugs(self):
        for key, values in self.point_population_per_opponent_.iteritems():
            if key != 'hall_of_fame' and len(values) != self.population_size_:
                raise ValueError("The size of the points population changed during selection for opponent "+str(key)+"! You got a bug! (it is: "+str(len(values))+", should be: "+str(self.population_size_)+")")

    def evaluate_point_population(self, teams_population):
        if Config.USER['reinforcement_parameters']['opponents_pool'] == 'only_sbb':
            return        

        if Config.USER['reinforcement_parameters']['balanced_opponent_populations']:
            opponents = []
            current_subsets_per_opponent = []
            for key, values in self.point_population_per_opponent_.iteritems():
                if key != 'hall_of_fame' and key != 'sbb':
                    opponents.append(key)
                    current_subsets_per_opponent.append(values)
        else:
            if self.current_population_ == 'hall_of_fame' or self.current_population_ == 'sbb':
                return
            opponents = [self.current_population_]
            current_subsets_per_opponent = [self.point_population_per_opponent_[self.current_population_]]

        samples_per_opponent_to_keep = int(round(self.population_size_*(1.0-Config.USER['training_parameters']['replacement_rate']['points'])))
        
        kept_subsets_per_opponent = []
        removed_subsets_per_opponent = []
        if Config.USER['advanced_training_parameters']['use_pareto_for_point_population_selection']:
            # obtain the pareto front for each subset
            for subset in current_subsets_per_opponent:
                keep_solutions, remove_solutions = ParetoDominance.pareto_front_for_points(subset, teams_population, samples_per_opponent_to_keep)
                kept_subsets_per_opponent.append(keep_solutions)
                removed_subsets_per_opponent.append(remove_solutions)
            
            # add new points
            for subset, opponent_class_name in zip(kept_subsets_per_opponent, opponents):
                samples_per_opponent_to_add = self.population_size_ - len(subset)
                for x in range(samples_per_opponent_to_add):
                    subset.append(self._instantiate_point_for_coded_opponent_class(self.opponent_class_mapping_[opponent_class_name]))
        else:
            # obtain the data points that will be kept and that will be removed for each subset using uniform probability
            total_samples_per_opponent_to_add = self.population_size_ - samples_per_opponent_to_keep
            for subset, opponent_class_name in zip(current_subsets_per_opponent, opponents):
                kept_subsets = random.sample(subset, samples_per_opponent_to_keep) # get points that will be kept
                for x in range(total_samples_per_opponent_to_add):
                    kept_subsets.append(self._instantiate_point_for_coded_opponent_class(self.opponent_class_mapping_[opponent_class_name])) # add new points
                kept_subsets_per_opponent.append(kept_subsets)
                removed_subsets_per_opponent.append(list(set(subset) - set(kept_subsets))) # find the remvoed points
        
        self.samples_per_opponent_to_keep_ = {}
        for key, values in zip(opponents, kept_subsets_per_opponent):
            self.samples_per_opponent_to_keep_[key] = values
        self.samples_per_opponent_to_remove_ = {}
        for key, values in zip(opponents, removed_subsets_per_opponent):
            self.samples_per_opponent_to_remove_[key] = values

    def evaluate_teams_population(self, teams_population):
        for team in teams_population:
            self.evaluate_team(team, Config.RESTRICTIONS['mode']['training'])
        if Config.USER['reinforcement_parameters']['hall_of_fame']['enabled']:
            sorted_teams = sorted(teams_population, key=lambda team: team.fitness_, reverse = True) # better ones first
            team_ids = [p.opponent.team_id_ for p in self.point_population_per_opponent_['hall_of_fame']]
            for team in sorted_teams:
                if team.team_id_ not in team_ids:
                    self.team_to_add_to_hall_of_fame_ = self._instantiate_point_for_sbb_opponent(team)
                    self.team_to_add_to_hall_of_fame_.opponent.opponent_id = "hall_of_fame"
                    break

    def evaluate_team(self, team, mode):
        """
        Each team plays 2 matches against each point in the point population.
        One match as the player 1, another as player 2. The final score is 
        the mean of the scores in the matches (1: win, 0.5: draw, 0: lose)
        """
        if mode == Config.RESTRICTIONS['mode']['training']:
            is_training = True
            point_population = self.point_population()
        else:
            is_training = False
            if mode == Config.RESTRICTIONS['mode']['validation']:
                if Config.USER['reinforcement_parameters']['hall_of_fame']['enabled']:
                    point_population = self.test_population_ + self.point_population_per_opponent_['hall_of_fame']
                else:
                    point_population = self.test_population_
            elif mode == Config.RESTRICTIONS['mode']['champion']:
                point_population = self.champion_population_

        results = []
        extra_metrics = {}
        extra_metrics['opponents'] = defaultdict(list)

        # use hall of fame as a criteria during training, and only used as a metric during validation
        dont_use_results_for_hall_of_fame = False
        if Config.USER['reinforcement_parameters']['hall_of_fame']['enabled'] and not is_training:
            dont_use_results_for_hall_of_fame = True

        for point in point_population:
            if is_training and Config.RESTRICTIONS['use_memmory_for_results'] and point.point_id in team.results_per_points_:
                results.append(team.results_per_points_[point.point_id])
            else:
                result = self._play_match(team, point, is_training)
                if is_training:
                    team.results_per_points_[point.point_id] = result
                else:
                    extra_metrics['opponents'][point.opponent.opponent_id].append(result)
                if not (point.opponent.opponent_id == "hall_of_fame" and dont_use_results_for_hall_of_fame):
                    results.append(result)

        score = numpy.mean(results)
        
        if is_training:
            team.fitness_ = score
            team.score_trainingset_ = score
        else:
            for key in extra_metrics['opponents']:
                extra_metrics['opponents'][key] = round_value(numpy.mean(extra_metrics['opponents'][key]))
            team.score_testset_ = score
            team.extra_metrics_ = extra_metrics

    def validate(self, current_generation, teams_population):
        for team in teams_population:
            if team.generation != current_generation: # dont evaluate teams that have just being created (to improve performance and to get training metrics)
                self.evaluate_team(team, Config.RESTRICTIONS['mode']['validation'])
        score = [p.score_testset_ for p in teams_population]
        best_team = teams_population[score.index(max(score))]
        validation_score = round_value(best_team.score_testset_)
        validation_opponents = best_team.extra_metrics_['opponents']
        print "\nscore (validation): "+str(validation_score)
        for key in validation_opponents:
            print "validation score against opponent ("+key+"): "+str(validation_opponents[key])
        self.evaluate_team(best_team, Config.RESTRICTIONS['mode']['champion'])
        best_team.extra_metrics_['validation_score'] = validation_score
        best_team.extra_metrics_['validation_opponents'] = validation_opponents
        return best_team

    def hall_of_fame(self):
        if 'hall_of_fame' in self.point_population_per_opponent_:
            return [p.opponent for p in self.point_population_per_opponent_['hall_of_fame']]
        else:
            return []