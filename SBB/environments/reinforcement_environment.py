import abc
import random
import copy
import numpy
from collections import defaultdict
from default_environment import DefaultEnvironment, DefaultPoint
from ..team import Team
from ..diversity_maintenance import DiversityMaintenance
from ..pareto_dominance_for_points import ParetoDominanceForPoints
from ..pareto_dominance_for_teams import ParetoDominanceForTeams
from ..utils.helpers import round_value, flatten
from ..config import Config

class ReinforcementPoint(DefaultPoint):
    """
    
    """
    __metaclass__  = abc.ABCMeta

    def __init__(self):
        self.seed_ = random.randint(0, Config.RESTRICTIONS['max_seed'])
        point_id = str(self.seed_)
        super(ReinforcementPoint, self).__init__(point_id)

class ReinforcementEnvironment(DefaultEnvironment):
    """
    
    """
    __metaclass__  = abc.ABCMeta

    @abc.abstractmethod
    def _instantiate_point(self):
        """
        
        """

    @abc.abstractmethod
    def _play_match(self, team, point, mode):
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
        self.opponents_names_ = [str(opponent_class) for opponent_class in self.coded_opponents_for_training_]
        Config.RESTRICTIONS['total_actions'] = self.total_actions_
        Config.RESTRICTIONS['total_inputs'] = self.total_inputs_
        self.team_to_add_to_hall_of_fame_ = None
        self.opponent_population_ = None
        self.point_population_ = []
        self.validation_point_population_ = None
        self.champion_point_population_ = None
        self.validation_opponent_population_ = None
        self.champion_opponent_population_ = None
        self.first_sampling_ = True
        self.last_population_ = None
        self.current_opponent_ = None
        self.current_opponent_population_ = None
        self.samples_per_class_to_keep_ = []
        self.samples_per_class_to_remove_ = []
        Config.RESTRICTIONS['use_memmory_for_actions'] = False # since the task is reinforcement learning, there is a lot of actions per point, instead of just one
        Config.RESTRICTIONS['use_memmory_for_results'] = True # since the opponents are seeded, the same point will always produce the same final result
        
        self.opponent_population_ = {}
        for opponent_class in self.coded_opponents_for_training_:
            self.opponent_population_[str(opponent_class)] = []
        if Config.USER['reinforcement_parameters']['hall_of_fame']['enabled']:
            self.opponent_population_['hall_of_fame'] = []
            self.opponents_names_.append('hall_of_fame')

    def _instantiate_coded_opponent(self, opponent_class):
        return opponent_class()

    def _instantiate_sbb_opponent(self, team, opponent_id):
        team.opponent_id = opponent_id
        return team

    def point_population(self): # TODO: checar se as chamadas a esse metodo usam os oponentes
        return self.point_population_

    def validation_population(self):
        return self.validation_point_population_

    def reset(self):
        for key in self.opponent_population_:
            self.opponent_population_[key] = []
        self.point_population_ = []
        self.team_to_add_to_hall_of_fame_ = None
        self.validation_point_population_ = [self._instantiate_point() for index in range(Config.USER['reinforcement_parameters']['validation_population'])]
        self.champion_point_population_ = [self._instantiate_point() for index in range(Config.USER['reinforcement_parameters']['champion_population'])]
        self.validation_opponent_population_ = self._initialize_random_balanced_population_of_coded_opponents_for_validation(Config.USER['reinforcement_parameters']['validation_population'])
        self.champion_opponent_population_ = self._initialize_random_balanced_population_of_coded_opponents_for_validation(Config.USER['reinforcement_parameters']['champion_population'])
        self.first_sampling_ = True
        self.last_population_ = None
        self.current_opponent_ = None
        self.current_opponent_population_ = None

    def _initialize_random_balanced_population_of_coded_opponents_for_validation(self, population_size):
        population = []
        total_per_opponent = population_size/len(self.coded_opponents_for_validation_)
        for opponent_class in self.coded_opponents_for_validation_:
            for index in range(total_per_opponent):
                population.append(self._instantiate_coded_opponent(opponent_class))
        return population

    def setup(self, teams_population):
        """
        Setup the point and the opponent population.
        """
        # define current opponent population
        options = self.opponent_population_.keys()
        if Config.USER['reinforcement_parameters']['hall_of_fame']['enabled'] and len(self.opponent_population_['hall_of_fame']) < Config.USER['reinforcement_parameters']['hall_of_fame']['size']:
            options.remove('hall_of_fame')
        self.last_population_ = self.current_opponent_
        if len(options) > 1 and self.last_population_:
            options.remove(self.last_population_)
        self.current_opponent_ = random.choice(options)

        # initialize point population
        if self.first_sampling_:
            self.first_sampling_ = False
            self.point_population_ = []
            for index in range(Config.USER['training_parameters']['populations']['points']):
                self.point_population_.append(self._instantiate_point())
        else: # uses attributes defined in evaluate_point_population()
            self._remove_points(flatten(self.samples_per_class_to_remove_), teams_population)
            self.point_population_ = flatten(self.samples_per_class_to_keep_)
            random.shuffle(self.point_population_)

        # initialize opponent population
        self._initialize_point_population_per_opponent_for_coded_opponents()

        # setup hall of fame
        if Config.USER['reinforcement_parameters']['hall_of_fame']['enabled']:
            hall_of_fame = self.opponent_population_['hall_of_fame']
            if self.team_to_add_to_hall_of_fame_:
                team_to_copy = self.team_to_add_to_hall_of_fame_
                copied_team = Team(team_to_copy.generation, list(team_to_copy.programs))
                copied_team.team_id_ = team_to_copy.team_id_
                copied_team.fitness_ = team_to_copy.fitness_
                copied_team.active_programs_ = list(team_to_copy.active_programs_)
                hall_of_fame.append(self._instantiate_sbb_opponent(copied_team, "hall_of_fame"))
                if len(hall_of_fame) > Config.USER['reinforcement_parameters']['hall_of_fame']['size']:
                    if Config.USER['reinforcement_parameters']['hall_of_fame']['diversity']:
                        novelty = Config.USER['reinforcement_parameters']['hall_of_fame']['diversity']
                        teams = [p for p in hall_of_fame]
                        DiversityMaintenance.calculate_diversities_based_on_distances(teams, k = Config.USER['reinforcement_parameters']['hall_of_fame']['size'], distances = [novelty])
                        keep_teams, remove_teams, pareto_front = ParetoDominanceForTeams.run(teams, novelty, Config.USER['reinforcement_parameters']['hall_of_fame']['size'])
                        removed_point = [p for p in hall_of_fame if p == remove_teams[0]]
                        worst_point = removed_point[0]
                    else:
                        score = [p.fitness_ for p in hall_of_fame]
                        worst_point = hall_of_fame[score.index(min(score))]
                    self.opponent_population_['hall_of_fame'].remove(worst_point)
                self.team_to_add_to_hall_of_fame_ = None
            # reset action sequence
            for team in self.hall_of_fame():
                team.action_sequence_ = []

        # setup current_opponent_population
        self.current_opponent_population_ = []
        opponent = random.choice(self.opponent_population_[self.current_opponent_])
        for index in range(Config.USER['training_parameters']['populations']['points']):
            self.current_opponent_population_.append(opponent)

        self._check_for_bugs()

    def _initialize_point_population_per_opponent_for_coded_opponents(self):
        for opponent_class in self.coded_opponents_for_training_:
            for index in range(Config.USER['training_parameters']['populations']['points']):
                self.opponent_population_[str(opponent_class)].append(self._instantiate_coded_opponent(opponent_class))

    def _remove_points(self, points_to_remove, teams_population):
        """
        Remove the points to remove from the teams, in order to save memory.
        """
        for team in teams_population:
            for point in points_to_remove:
                if point.point_id in team.results_per_points_:
                    team.results_per_points_.pop(point.point_id)

    def _check_for_bugs(self):
        if len(self.point_population_) != Config.USER['training_parameters']['populations']['points']:
            raise ValueError("The size of the points population changed during selection! You got a bug! (it is: "+str(len(self.point_population_))+", should be: "+str(Config.USER['training_parameters']['populations']['points'])+")")

    def evaluate_point_population(self, teams_population): #TODO: fazer ser compativel entre ttt e poker
        # current_subsets_per_class = self._get_data_per_action(self.point_population_) # TODO
        current_subsets_per_class = [self.point_population_]
        total_classes = 1 # TODO
        total_samples_per_class = Config.USER['training_parameters']['populations']['points']/total_classes
        samples_per_class_to_keep = int(round(total_samples_per_class*(1.0-Config.USER['training_parameters']['replacement_rate']['points'])))

        kept_subsets_per_class = []
        removed_subsets_per_class = []
        if Config.USER['advanced_training_parameters']['use_pareto_for_point_population_selection']:
            # obtain the pareto front for each subset
            for subset in current_subsets_per_class:
                keep_solutions, remove_solutions = ParetoDominanceForPoints.run(subset, teams_population, samples_per_class_to_keep)
                kept_subsets_per_class.append(keep_solutions)
                removed_subsets_per_class.append(remove_solutions)

            # add new points # TODO
            for subset in kept_subsets_per_class:
                samples_per_class_to_add = total_samples_per_class - len(subset)
                for x in range(samples_per_class_to_add):
                    subset.append(self._instantiate_point())
        else:
            # obtain the data points that will be kept and that will be removed for each subset using uniform probability
            total_samples_per_class_to_add = total_samples_per_class - samples_per_class_to_keep
            for i, subset in enumerate(current_subsets_per_class):
                kept_subsets = random.sample(subset, samples_per_class_to_keep) # get points that will be kept
                for x in range(total_samples_per_class_to_add):
                    kept_subsets.append(self._instantiate_point()) # add new points # TODO
                kept_subsets_per_class.append(kept_subsets)
                removed_subsets_per_class.append(list(set(subset) - set(kept_subsets))) # find the remvoed points

        self.samples_per_class_to_keep_ = kept_subsets_per_class
        self.samples_per_class_to_remove_ = removed_subsets_per_class

    def evaluate_teams_population(self, teams_population):
        for team in teams_population:
            team.action_sequence_ = []
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
            is_training = True
            point_population = self.point_population()
            opponent_population = self.current_opponent_population_
        else:
            is_training = False
            if mode == Config.RESTRICTIONS['mode']['validation']:
                point_population = self.validation_point_population_
                opponent_population = self.validation_opponent_population_
            elif mode == Config.RESTRICTIONS['mode']['champion']:
                point_population = self.champion_point_population_
                opponent_population = self.champion_opponent_population_

        results = []
        extra_metrics_opponents = defaultdict(list)

        for point, opponent in zip(point_population, opponent_population):
            # if is_training and Config.RESTRICTIONS['use_memmory_for_results'] and point.point_id in team.results_per_points_:
            #     results.append(team.results_per_points_[point.point_id])
            # else: # TODO
            result = self._play_match(team, opponent, point, mode)
            if is_training:
                team.results_per_points_[point.point_id] = result
            else:
                if mode == Config.RESTRICTIONS['mode']['validation']:
                    team.results_per_points_for_validation_[point.point_id] = result
                extra_metrics_opponents[opponent.opponent_id].append(result)
            results.append(result)

        score = numpy.mean(results)
        
        if is_training:
            team.fitness_ = score
        else:
            for key in extra_metrics_opponents:
                extra_metrics_opponents[key] = round_value(numpy.mean(extra_metrics_opponents[key]))
            team.score_testset_ = score
            team.extra_metrics_['opponents'] = extra_metrics_opponents

    def validate(self, current_generation, teams_population):
        print "\nvalidating all..."
        for team in teams_population:
            if team.generation != current_generation: # dont evaluate teams that have just being created (to improve performance and to get training metrics)
                team.results_per_points_for_validation_ = {}
                self.evaluate_team(team, Config.RESTRICTIONS['mode']['validation'])
                team.extra_metrics_['validation_score'] = round_value(team.score_testset_)
                team.extra_metrics_['validation_opponents'] = team.extra_metrics_['opponents']
                team.extra_metrics_.pop('champion_score', None)
                team.extra_metrics_.pop('champion_opponents', None)
        score = [p.score_testset_ for p in teams_population]
        best_team = teams_population[score.index(max(score))]
        print "\nvalidating champion..."
        self.evaluate_team(best_team, Config.RESTRICTIONS['mode']['champion'])
        best_team.extra_metrics_['champion_score'] = round_value(best_team.score_testset_)
        best_team.extra_metrics_['champion_opponents'] = best_team.extra_metrics_['opponents']
        if Config.USER['reinforcement_parameters']['hall_of_fame']['enabled']:
            # reset action sequence
            for team in self.hall_of_fame():
                team.action_sequence_ = []
        return best_team

    def hall_of_fame(self):
        if 'hall_of_fame' in self.opponent_population_:
            return [p for p in self.opponent_population_['hall_of_fame']]
        else:
            return []