import abc
import random
import copy
import numpy
from collections import defaultdict
from ..default_environment import DefaultEnvironment
from ..default_point import  reset_points_ids
from ...core.team import Team
from ...core.diversity_maintenance import DiversityMaintenance
from ...core.pareto_dominance_for_teams import ParetoDominanceForTeams
from ...utils.helpers import round_value, round_array, flatten, accumulative_performances, rank_teams_by_accumulative_score
from ...config import Config

class ReinforcementEnvironment(DefaultEnvironment):

    __metaclass__  = abc.ABCMeta

    @abc.abstractmethod
    def _play_match(self, team, opponent, point, mode, match_id):
        """
        To be implemented via inheritance.
        """

    def __init__(self, total_actions, total_inputs, total_labels, coded_opponents_for_training, coded_opponents_for_validation, point_class):
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
        self.opponent_names_for_training_ = [c.OPPONENT_ID for c in self.coded_opponents_for_training_]
        if Config.USER['reinforcement_parameters']['hall_of_fame']['opponents'] > 0:
            self.opponent_names_for_training_.append('hall_of_fame')
        self.opponent_names_for_validation_ = [c.OPPONENT_ID for c in self.coded_opponents_for_validation_]
        self.matches_per_opponent_per_generation_ = None
        self._ensure_balanced_population_size_for_training()
        self._ensure_balanced_population_size('validation_population')
        self._ensure_balanced_population_size('champion_population')
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
        Config.RESTRICTIONS['use_memmory_for_actions'] = False # since the task is reinforcement learning, there is a lot of actions per point, instead of just one
        self.champion_matches_per_hall_of_fame_opponent_ = 20
        self.current_hall_of_fame_opponents_ = []

    def _ensure_balanced_population_size_for_training(self):
        pop_size = Config.USER['training_parameters']['populations']['points']
        total_opponents = len(self.coded_opponents_for_training_)
        if Config.USER['reinforcement_parameters']['hall_of_fame']['opponents'] > 0:
            total_opponents += Config.USER['reinforcement_parameters']['hall_of_fame']['opponents']
        temp = total_opponents*self.total_labels_
        pop_size = (pop_size/temp)*temp
        self.matches_per_opponent_per_generation_ = pop_size/total_opponents
        Config.USER['training_parameters']['populations']['points'] = pop_size

    def _ensure_balanced_population_size(self, population_key):
        pop_size = Config.USER['reinforcement_parameters'][population_key]
        temp = len(self.coded_opponents_for_validation_)*self.total_labels_
        pop_size = (pop_size/temp)*temp
        Config.USER['reinforcement_parameters'][population_key] = pop_size

    def _instantiate_coded_opponent(self, opponent_class):
        return opponent_class()

    def _instantiate_sbb_opponent(self, team, opponent_id):
        team.opponent_id = opponent_id
        return team

    def point_population(self):
        return self.point_population_

    def validation_population(self):
        return self.validation_point_population_

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
        self.validation_point_population_ = self._initialize_random_population_of_points(Config.USER['reinforcement_parameters']['validation_population'], ignore_cache = True)
        if Config.USER['reinforcement_parameters']['hall_of_fame']['opponents'] > 0:
            size = Config.USER['reinforcement_parameters']['champion_population'] + Config.USER['reinforcement_parameters']['hall_of_fame']['size']*self.champion_matches_per_hall_of_fame_opponent_
            population = self._initialize_random_population_of_points(size, ignore_cache = True)
            self.champion_point_population_ = population[:Config.USER['reinforcement_parameters']['champion_population']]
            self.champion_point_population_for_hall_of_fame_ = population[Config.USER['reinforcement_parameters']['champion_population']:]
        else:
            self.champion_point_population_ = self._initialize_random_population_of_points(Config.USER['reinforcement_parameters']['champion_population'], ignore_cache = True)
        self.training_opponent_population_ = self._initialize_random_balanced_population_of_coded_opponents_for_training(Config.USER['training_parameters']['populations']['points'])
        self.validation_opponent_population_ = self._initialize_random_balanced_population_of_coded_opponents_for_validation(Config.USER['reinforcement_parameters']['validation_population'])
        self.champion_opponent_population_ = self._initialize_random_balanced_population_of_coded_opponents_for_validation(Config.USER['reinforcement_parameters']['champion_population'])
        self.first_sampling_ = True

    def _initialize_random_population_of_points(self, population_size, ignore_cache = False):
        return [self.point_class() for index in range(population_size)]

    def _initialize_opponent_population(self):
        self.opponent_population_ = {}
        for opponent_class in self.coded_opponents_for_training_:
            self.opponent_population_[opponent_class.OPPONENT_ID] = [self._instantiate_coded_opponent(opponent_class)]
        if Config.USER['reinforcement_parameters']['hall_of_fame']['enabled']:
            self.opponent_population_['hall_of_fame'] = []

    def _initialize_random_balanced_population_of_coded_opponents_for_training(self, population_size):
        population = []
        for opponent_class in self.coded_opponents_for_training_:
            for index in range(self.matches_per_opponent_per_generation_):
                population.append(self._instantiate_coded_opponent(opponent_class))
        return population

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
        # initialize point population
        if self.first_sampling_:
            self.first_sampling_ = False
            population = self._initialize_random_population_of_points(Config.USER['training_parameters']['populations']['points'], ignore_cache = False)
            subsets_per_label = self._get_data_per_label(population)
            total_samples_per_class = Config.USER['training_parameters']['populations']['points']/self.total_labels_
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
                copied_team = Team(team_to_copy.generation, list(team_to_copy.programs), team_to_copy.environment)
                copied_team.team_id_ = team_to_copy.team_id_
                copied_team.fitness_ = team_to_copy.fitness_
                copied_team.active_programs_ = list(team_to_copy.active_programs_)
                copied_team.validation_active_programs_ = list(team_to_copy.validation_active_programs_)
                copied_team.encodings_ = copy.deepcopy(team_to_copy.encodings_)
                copied_team.extra_metrics_ = dict(team_to_copy.extra_metrics_)
                hall_of_fame.append(self._instantiate_sbb_opponent(copied_team, "hall_of_fame"))
                if len(hall_of_fame) > Config.USER['reinforcement_parameters']['hall_of_fame']['size']:
                    if Config.USER['reinforcement_parameters']['hall_of_fame']['diversity']:
                        novelty = Config.USER['reinforcement_parameters']['hall_of_fame']['diversity']
                        DiversityMaintenance.calculate_diversities_based_on_distances(hall_of_fame, k = Config.USER['reinforcement_parameters']['hall_of_fame']['size'], distances = [novelty])
                        keep_teams, remove_teams, pareto_front = ParetoDominanceForTeams.run(hall_of_fame, novelty, Config.USER['reinforcement_parameters']['hall_of_fame']['size'])
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
        samples_per_class_to_keep = int(round(total_samples_per_class*(1.0-Config.USER['training_parameters']['replacement_rate']['points'])))
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
            point_population = self.point_population()
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
            team.score_testset_ = numpy.mean(results)

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
                team.extra_metrics_['validation_score'] = round_value(team.score_testset_)
                team.extra_metrics_['validation_opponents'] = team.extra_metrics_['opponents']
                team.extra_metrics_['validation_points'] = team.extra_metrics_['points']
                team.extra_metrics_.pop('champion_score', None)
                team.extra_metrics_.pop('champion_opponents', None)
                team.extra_metrics_.pop('champion_points', None)
        score = [p.score_testset_ for p in teams_population]
        best_team = teams_population[score.index(max(score))]
        print "\nvalidating champion..."
        self.evaluate_team(best_team, Config.RESTRICTIONS['mode']['champion'])
        best_team.extra_metrics_['champion_score'] = round_value(best_team.score_testset_)
        best_team.extra_metrics_['champion_opponents'] = best_team.extra_metrics_['opponents']
        best_team.extra_metrics_['champion_points'] = best_team.extra_metrics_['points']
        return best_team

    def hall_of_fame(self):
        if 'hall_of_fame' in self.opponent_population_:
            return [p for p in self.opponent_population_['hall_of_fame']]
        else:
            return []

    def metrics_for_team(self, team):
        msg = ""
        if team.extra_metrics_:
            msg += "\n\n### Reinforcement Learning-specific metrics for the best team:"
            if 'champion_score' in team.extra_metrics_:
                msg += ("\n\nscore per opponent (except hall of fame) (champion): "
                    ""+str(team.extra_metrics_['champion_score']))
                total_opponents = Config.USER['reinforcement_parameters']['environment_parameters']['validation_opponents_labels']+['hall_of_fame']
                for key in team.extra_metrics_['opponents']:
                    if key in total_opponents:
                        msg += "\n"+key+": "+str(team.extra_metrics_['champion_opponents'][key])

            if 'validation_score' in team.extra_metrics_:
                msg += "\n\nscore per opponent (validation): "+str(team.extra_metrics_['validation_score'])
                for key in team.extra_metrics_['validation_opponents']:
                    msg += "\n"+key+": "+str(team.extra_metrics_['validation_opponents'][key])
                    
            if 'training_opponents' in team.extra_metrics_:
                msg += "\n\nscore per opponent (training): "+str(round_value(team.fitness_))
                total_opponents = Config.USER['reinforcement_parameters']['environment_parameters']['training_opponents_labels']+['hall_of_fame']
                for key in team.extra_metrics_['training_opponents']:
                    if key in total_opponents:
                        msg += "\n"+key+": "+str(team.extra_metrics_['training_opponents'][key])
        return msg

    def initialize_attributes_for_run_info(self, run_info):
        run_info.global_max_validation_score_per_validation_ = []
        run_info.global_opponent_results_per_validation_ = []
        run_info.hall_of_fame_per_validation_ = []
        run_info.global_fitness_per_opponent_per_generation_ = defaultdict(list)
        run_info.final_teams_validations_ = []
        run_info.final_teams_validations_ids_ = []
        run_info.individual_performance_in_last_generation_ = defaultdict(list)
        run_info.accumulative_performance_in_last_generation_ = defaultdict(list)
        run_info.ids_for_acc_performance_in_last_generation_ = defaultdict(list)
        run_info.accumulative_performance_summary_ = {}

    def generate_output_for_attributes_for_run_info(self, run_info):
        msg = ""
        msg += "\n\n\n\n#################### Reinforcement Learning-specific Metrics:"

        msg += "\n\n\n##### GLOBAL METRICS PER VALIDATION"

        msg += "\n\nGlobal Max. Validation Score per Validation: "+str(run_info.global_max_validation_score_per_validation_)
        
        msg += "\n\nGlobal Opponent Results per Validation"
        for key in run_info.global_opponent_results_per_validation_[-1]:
            msg += "\n - "+str(key)+": "+str([item[key] if key in item else 0.0 for item in run_info.global_opponent_results_per_validation_])
        
        if Config.USER['reinforcement_parameters']['hall_of_fame']['enabled']:
            msg += "\n\nHall of Fame per Validation: "+str(run_info.hall_of_fame_per_validation_)


        msg += "\n\n\n##### GLOBAL METRICS PER TRAINING"

        msg += "\n\nGlobal Fitness Score per Training (per opponent):"
        msg += "\n - predefined:"
        for opponent in self.opponent_names_for_training_:
            msg += "\n    - "+str(opponent)+": "+str(run_info.global_fitness_per_opponent_per_generation_[opponent])

        if Config.USER['reinforcement_parameters']['hall_of_fame']['enabled']:
            msg += "\n - hall of fame:"
            hall_of_fame = [x for x in run_info.global_fitness_per_opponent_per_generation_ if x not in self.opponent_names_for_training_]
            for key in hall_of_fame:
                msg += "\n    - "+str(key)+": "+str(run_info.global_fitness_per_opponent_per_generation_[key])


        msg += "\n\n\n##### FINAL TEAMS METRICS"

        msg += "\n\nFinal Teams Validations: "+str(run_info.final_teams_validations_)
        msg += "\nFinal Teams Ids: "+str(run_info.final_teams_validations_ids_)
        

        msg += "\n\n\n##### ACCUMULATIVE PERFORMANCES"

        for metric in run_info.individual_performance_in_last_generation_:
            msg += "\n\nOverall Accumulative Results ("+str(metric)+"):"
            msg += "\n- Individual Team Performance: "+str(run_info.individual_performance_in_last_generation_[metric])
            msg += "\n- Accumulative Team Performance: "+str(run_info.accumulative_performance_in_last_generation_[metric])
            msg += "\n- Team ids: "+str(run_info.ids_for_acc_performance_in_last_generation_[metric])

        
        msg += "\n\n\n##### TEAMS RANKED BY ACCUMULATIVE PERFORMANCE"

        msg += "\n\nTeams Ranked by Accumulative Score per Metric"
        for metric in run_info.accumulative_performance_summary_:
            msg += "\n - metric: "+str(metric)+" (len: "+str(len(run_info.accumulative_performance_summary_[metric]['overall']['ids_only']))+"):"
            msg += "\n    - Rank: "+str(run_info.accumulative_performance_summary_[metric]['overall']['rank'])
            msg += "\n    - Team ids: "+str(run_info.accumulative_performance_summary_[metric]['overall']['ids_only'])

        return msg

    def metrics(self):
        msg = ""
        msg += "\n### Environment Info:"
        msg += "\ntotal inputs: "+str(self.total_inputs_)
        msg += "\ntotal actions: "+str(self.total_actions_)
        return msg

    def store_per_generation_metrics(self, run_info, teams_population, current_generation, previous_diversity):
        super(ReinforcementEnvironment, self).store_per_generation_metrics(run_info, teams_population, current_generation, previous_diversity)
        older_teams = [team for team in teams_population if team.generation != current_generation]
        opponents = older_teams[0].extra_metrics_['training_opponents'].keys()
        for opponent in opponents:
            mean_fitness_per_opponent = round_value(numpy.mean([team.extra_metrics_['training_opponents'][opponent] for team in older_teams]), 3)
            run_info.global_fitness_per_opponent_per_generation_[opponent].append(mean_fitness_per_opponent)

    def store_per_validation_metrics(self, run_info, best_team, teams_population, programs_population, current_generation):
        super(ReinforcementEnvironment, self).store_per_validation_metrics(run_info, best_team, teams_population, programs_population, current_generation)
        older_teams = [team for team in teams_population if team.generation != current_generation]
        validation_score_mean = round_value(numpy.mean([team.extra_metrics_['validation_score'] for team in older_teams]))
        run_info.temp_info_['validation_score_mean'] = validation_score_mean
        opponent_means = {}
        for key in older_teams[0].extra_metrics_['validation_opponents']:
            opponent_means[key] = round_value(numpy.mean([t.extra_metrics_['validation_opponents'][key] for t in older_teams]))    
        if 'hall_of_fame' in best_team.extra_metrics_['champion_opponents']:
            opponent_means['hall_of_fame(champion)'] = best_team.extra_metrics_['champion_opponents']['hall_of_fame']
        run_info.global_mean_validation_score_per_validation_.append(validation_score_mean)
        run_info.global_max_validation_score_per_validation_.append(round_value(max([team.extra_metrics_['validation_score'] for team in older_teams])))
        run_info.global_opponent_results_per_validation_.append(opponent_means)               
        run_info.final_teams_validations_ = [team.extra_metrics_['validation_score'] for team in older_teams]

        if Config.USER['reinforcement_parameters']['hall_of_fame']['enabled']:
            run_info.hall_of_fame_per_validation_.append([p.__repr__() for p in self.hall_of_fame()])

    def print_per_validation_metrics(self, run_info, best_team, current_generation):
        super(ReinforcementEnvironment, self).print_per_validation_metrics(run_info, best_team, current_generation)
        if Config.USER['reinforcement_parameters']['hall_of_fame']['enabled']:
            print "\nHall of Fame: "+str(run_info.hall_of_fame_per_validation_[-1])

    def store_per_run_metrics(self, run_info, best_team, teams_population, pareto_front, current_generation):
        super(ReinforcementEnvironment, self).store_per_run_metrics(run_info, best_team, teams_population, pareto_front, current_generation)
        
        self._calculate_accumulative_performances(run_info, teams_population, current_generation)
        self._summarize_accumulative_performances(run_info)
        self._generate_second_layer_files(run_info, teams_population)
        
        older_teams = [team for team in teams_population if team.generation != current_generation]
        run_info.final_teams_validations_ids_ = [team.__repr__() for team in older_teams]

        # to ensure validation metrics exist for all teams in the hall of fame
        if Config.USER['reinforcement_parameters']['hall_of_fame']['enabled']:
            print "Validating hall of fame..."
            self.validate(current_generation, self.hall_of_fame())

    def _calculate_accumulative_performances(self, run_info, teams_population, current_generation):
        older_teams = [team for team in teams_population if team.generation != current_generation]
        metric = 'score'
        sorting_criteria = lambda x: x.extra_metrics_['validation_score']
        get_results_per_points = lambda x: x.results_per_points_for_validation_
        point_ids = [point.point_id_ for point in self.validation_population()]
        individual_performance, accumulative_performance, teams_ids = accumulative_performances(older_teams, point_ids, sorting_criteria, get_results_per_points)
        run_info.individual_performance_in_last_generation_[metric] = individual_performance
        run_info.accumulative_performance_in_last_generation_[metric] = accumulative_performance
        run_info.ids_for_acc_performance_in_last_generation_[metric] = teams_ids

    def _summarize_accumulative_performances(self, run_info, metrics = ['score']):
        for metric in metrics:
            run_info.accumulative_performance_summary_[metric] = {}
            ind_score = run_info.individual_performance_in_last_generation_[metric]
            acc_score = run_info.accumulative_performance_in_last_generation_[metric]
            ids = run_info.ids_for_acc_performance_in_last_generation_[metric]
            rank = rank_teams_by_accumulative_score(ind_score, acc_score, ids)
            run_info.accumulative_performance_summary_[metric]['overall'] = {}
            run_info.accumulative_performance_summary_[metric]['overall']['rank'] = rank
            run_info.accumulative_performance_summary_[metric]['overall']['ids_only'] = sorted([r[0] for r in rank])

    def _generate_second_layer_files(self, run_info, teams_population):
        top5_overall_ids = [r[0] for r in run_info.accumulative_performance_summary_['score']['overall']['rank'][:5]]
        top10_overall_ids = [r[0] for r in run_info.accumulative_performance_summary_['score']['overall']['rank'][:10]]
        top15_overall_ids = [r[0] for r in run_info.accumulative_performance_summary_['score']['overall']['rank'][:15]]
        if len(top5_overall_ids) == 5:
            run_info.second_layer_files_['top5_overall'] = [t for t in teams_population if t.__repr__() in top5_overall_ids]
        if len(top5_overall_ids) == 10:
            run_info.second_layer_files_['top10_overall'] = [t for t in teams_population if t.__repr__() in top10_overall_ids]
        if len(top5_overall_ids) == 15:
            run_info.second_layer_files_['top15_overall'] = [t for t in teams_population if t.__repr__() in top15_overall_ids]
        run_info.second_layer_files_['all'] = teams_population

    def generate_overall_metrics_output(self, run_infos):  
        msg, best_scores_per_runs = super(ReinforcementEnvironment, self).generate_overall_metrics_output(run_infos)

        score_means, score_stds = self._process_scores([run.global_max_validation_score_per_validation_ for run in run_infos])
        msg += "\n\nGlobal Max. Validation Score per Validation:"
        msg += "\nmean: "+str(score_means)
        msg += "\nstd. deviation: "+str(score_stds)

        msg += "\n\nGlobal Fitness per Opponent per Training:"
        for key in self.opponent_names_for_training_:
            score_means, score_stds = self._process_scores([run.global_fitness_per_opponent_per_generation_[key] for run in run_infos])
            msg += "\n- "+str(key)+":"
            msg += "\n- mean: "+str(round_array(score_means, 2))
            msg += "\n- std. deviation: "+str(round_array(score_stds, 2))
        for run_id, run in enumerate(run_infos):
            valid_names = [t.__repr__() for t in run.hall_of_fame_in_last_generation_]
            for key in run.global_fitness_per_opponent_per_generation_.keys():
                if key in valid_names:
                    msg += "\n- run "+str(run_id+1)+", "+str(key)+": "+str(run.global_fitness_per_opponent_per_generation_[key])

        msg += "\n\nFinal Teams Validations: "+str(flatten([round_array(run.final_teams_validations_, 3) for run in run_infos]))

        msg += "\n"
        msg += self._generate_overall_metrics_output_for_acc_curves(run_infos)

        return msg, best_scores_per_runs