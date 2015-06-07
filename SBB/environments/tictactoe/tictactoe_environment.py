import random
import numpy
from collections import defaultdict
from tictactoe_match import TictactoeMatch
from tictactoe_opponents import TictactoeRandomOpponent, TictactoeSmartOpponent
from ..default_environment import DefaultEnvironment, DefaultPoint
from ...team import Team
from ...diversity_maintenance import DiversityMaintenance
from ...pareto_dominance import ParetoDominance
from ...utils.helpers import round_value, flatten, is_nearly_equal_to
from ...config import Config

class TictactoePoint(DefaultPoint):
    """
    Encapsulates a tictactoe board configuration as a point.
    """

    def __init__(self, point_id, opponent):
        super(TictactoePoint, self).__init__(point_id)
        self.opponent = opponent

class TictactoeEnvironment(DefaultEnvironment):
    """
    This environment encapsulates all methods to deal with a reinforcement learning task for TicTacToe.
    This is a dummy environment, where the only point in the population is a random player.
    """

    def __init__(self):
        self.point_population_ = None
        self.total_actions_ = 9 # spaces in the board
        self.total_inputs_ = 9 # spaces in the board (0, 1, 2 as the states, 0: no player, 1: player 1, 2: player 2)
        self.total_positions_ = 2
        self.opponents_ = [TictactoeRandomOpponent, TictactoeSmartOpponent]
        self.test_population_ = self._initialize_random_balanced_population_of_coded_opponents(Config.USER['reinforcement_parameters']['validation_population'])
        self.champion_population_ = self._initialize_random_balanced_population_of_coded_opponents(Config.USER['reinforcement_parameters']['champion_population'])
        self.action_mapping_ = {
            '[0,0]': 0, '[0,1]': 1, '[0,2]': 2,
            '[1,0]': 3, '[1,1]': 4, '[1,2]': 5,
            '[2,0]': 6, '[2,1]': 7, '[2,2]': 8,
        }
        Config.RESTRICTIONS['total_actions'] = self.total_actions_
        Config.RESTRICTIONS['total_inputs'] = self.total_inputs_
        Config.RESTRICTIONS['action_mapping'] = self.action_mapping_
        Config.RESTRICTIONS['use_memmory_for_actions'] = False # since the task is reinforcement learning, there is a lot of actions per point, instead of just one
        Config.RESTRICTIONS['use_memmory_for_results'] = True # since the opponents are seeded, the same point will always produce the same final result
        
        # ensure the matches per opponents are balanced, and that no more than the team population size is used as sbb opponents
        if Config.USER['reinforcement_parameters']['opponents_pool'] == 'only_sbb':
            if Config.USER['training_parameters']['populations']['points'] > Config.USER['training_parameters']['populations']['teams']:
                Config.USER['training_parameters']['populations']['points'] = Config.USER['training_parameters']['populations']['teams']
        elif Config.USER['reinforcement_parameters']['opponents_pool'] == 'only_coded_opponents':
            super(TictactoeEnvironment, self)._round_point_population_based_on(len(self.opponents_))
        elif Config.USER['reinforcement_parameters']['opponents_pool'] == 'hybrid':
            total_opponents = len(self.opponents_)+1
            if Config.USER['training_parameters']['populations']['points']/total_opponents > Config.USER['training_parameters']['populations']['teams']:
                Config.USER['training_parameters']['populations']['points'] = Config.USER['training_parameters']['populations']['teams']*total_opponents
            super(TictactoeEnvironment, self)._round_point_population_based_on(total_opponents)

    def _initialize_random_balanced_population_of_coded_opponents(self, population_size):
        population = []
        for opponent_class in self.opponents_:
            for index in range(population_size/len(self.opponents_)):
                instance = opponent_class()
                population.append(TictactoePoint(str(instance), instance))
        random.shuffle(population)
        return population

    def reset_point_population(self):
        self.point_population_ = None

    def setup_point_population(self, teams_population):
        """
        Get a sample of the training dataset to create the point population. If it is the first generation 
        of the run, just gets random samples for each action of the dataset. For the next generations, it 
        replaces some of the points in the sample for new points.
        """
        population_size = Config.USER['training_parameters']['populations']['points']
        total_opponents = len(self.opponents_)+1
        if Config.USER['reinforcement_parameters']['opponents_pool'] == 'only_sbb':
            if self.point_population_:
                super(TictactoeEnvironment, self)._remove_points(self.point_population_, teams_population)
            self.point_population_ = self._initialize_point_population_of_sbb_opponents(teams_population, population_size)
        elif not self.point_population_: # first sampling of the run
            if Config.USER['reinforcement_parameters']['opponents_pool'] == 'only_coded_opponents':
                self.point_population_ = self._initialize_random_balanced_population_of_coded_opponents(population_size)
            elif Config.USER['reinforcement_parameters']['opponents_pool'] == 'hybrid':
                self.point_population_ = []
                self.point_population_ += self._initialize_point_population_of_sbb_opponents(teams_population, population_size/total_opponents)
                self.point_population_ += self._initialize_random_balanced_population_of_coded_opponents((population_size/total_opponents)*(total_opponents-1))
        else: # uses attributes defined in evaluate_point_population()  # HERE
            super(TictactoeEnvironment, self)._remove_points(flatten(self.samples_per_opponent_to_remove), teams_population)
            if Config.USER['reinforcement_parameters']['opponents_pool'] == 'hybrid':
                self.samples_per_opponent_to_keep.append(self._initialize_point_population_of_sbb_opponents(teams_population, population_size/total_opponents))
            sample = flatten(self.samples_per_opponent_to_keep) # join samples per opponent
            random.shuffle(sample)
            self.point_population_ = sample
        super(TictactoeEnvironment, self)._check_for_bugs()

    def _initialize_point_population_of_sbb_opponents(self, teams_population, size):
        sbb_opponents = random.sample(teams_population, size)
        population = []
        for opponent in sbb_opponents:
            population.append(TictactoePoint(opponent.__repr__(), opponent))
        return population

    def evaluate_point_population(self, teams_population):
        if Config.USER['reinforcement_parameters']['opponents_pool'] == 'only_sbb':
            return

        current_subsets_per_opponent = self._get_data_per_opponent(self.point_population_)
        if Config.USER['reinforcement_parameters']['opponents_pool'] == 'only_coded_opponents':
            total_samples_per_opponent = Config.USER['training_parameters']['populations']['points']/len(self.opponents_)
            removed_subsets_per_opponent = []
        elif Config.USER['reinforcement_parameters']['opponents_pool'] == 'hybrid':
            total_samples_per_opponent = Config.USER['training_parameters']['populations']['points']/(len(self.opponents_)+1)
            removed_subsets_per_opponent = [point for point in self.point_population_ if type(point.opponent) is Team]
        kept_subsets_per_opponent = []
        samples_per_opponent_to_keep = int(round(total_samples_per_opponent*(1.0-Config.USER['training_parameters']['replacement_rate']['points'])))

        if Config.USER['advanced_training_parameters']['use_pareto_for_point_population_selection']:
            # obtain the pareto front for each subset
            for subset in current_subsets_per_opponent:
                keep_solutions, remove_solutions = ParetoDominance.pareto_front_for_points(subset, teams_population, samples_per_opponent_to_keep)
                kept_subsets_per_opponent.append(keep_solutions)
                removed_subsets_per_opponent.append(remove_solutions)

            # add new points
            for subset, opponent_class in zip(kept_subsets_per_opponent, self.opponents_):
                samples_per_opponent_to_add = total_samples_per_opponent - len(subset)
                for x in range(samples_per_opponent_to_add):
                    instance = opponent_class()
                    subset.append(TictactoePoint(str(instance), instance))
        else:
            # obtain the data points that will be kept and that will be removed for each subset using uniform probability
            total_samples_per_opponent_to_add = total_samples_per_opponent - samples_per_opponent_to_keep
            for index, subset in enumerate(current_subsets_per_opponent):
                kept_subsets = random.sample(subset, samples_per_opponent_to_keep) # get points that will be kept
                for x in range(total_samples_per_opponent_to_add):
                    instance = self.opponents_[index]()
                    kept_subsets.append(TictactoePoint(str(instance), instance)) # add new points
                kept_subsets_per_opponent.append(kept_subsets)
                removed_subsets_per_opponent.append(list(set(subset) - set(kept_subsets))) # find the remvoed points

        self.samples_per_opponent_to_keep = kept_subsets_per_opponent
        self.samples_per_opponent_to_remove = removed_subsets_per_opponent

    def _get_data_per_opponent(self, point_population):
        """
        Get subsets of the point_population for each coded opponent (ie. ignored SBB opponents)
        """
        subsets_per_opponent = []
        for opponent_class in self.opponents_:
            values = [point for point in point_population if type(point.opponent) is opponent_class]
            subsets_per_opponent.append(values)
        return subsets_per_opponent

    def evaluate_team(self, team, mode):
        """
        Each team plays 2 matches against each point in the point population.
        One match as the player 1, another as player 2. The final score is 
        the mean of the scores in the matches (1: win, 0.5: draw, 0: lose)
        """
        if mode == DefaultEnvironment.MODE['training']:
            is_training = True
            population = self.point_population_
        else:
            is_training = False
            if mode == DefaultEnvironment.MODE['validation']:
                population = self.test_population_
            elif mode == DefaultEnvironment.MODE['champion']:
                population = self.champion_population_

        results = []
        extra_metrics = {}
        extra_metrics['opponents'] = defaultdict(list)

        for point in population:
            if is_training and Config.RESTRICTIONS['use_memmory_for_results'] and point.point_id in team.results_per_points_:
                results.append(team.results_per_points_[point.point_id])
            else:
                outputs = []
                for position in range(1, self.total_positions_+1):
                    outputs.append(self._play_match(position, point, team, is_training))
                result = numpy.mean(outputs)
                if is_training:
                    team.results_per_points_[point.point_id] = result
                else:
                    extra_metrics['opponents'][point.opponent.opponent_id].append(result)
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

    def _play_match(self, position, point, team, is_training):
        if position == 1:
            first_player = point.opponent
            is_training_for_first_player = False
            second_player = team
            is_training_for_second_player = is_training
            sbb_player = 2
        else:
            first_player = team
            is_training_for_first_player = is_training
            second_player = point.opponent
            is_training_for_second_player = False
            sbb_player = 1

        match = TictactoeMatch()
        point.opponent.initialize()
        while True:
            player = 1
            inputs = match.inputs_from_the_point_of_view_of(player)
            action = first_player.execute(point.point_id, inputs, match.valid_actions(), is_training_for_first_player)
            match.perform_action(player, action)
            if match.is_over():
                return match.result_for_player(sbb_player)
            player = 2
            inputs = match.inputs_from_the_point_of_view_of(player)
            action = second_player.execute(point.point_id, inputs, match.valid_actions(), is_training_for_second_player)
            match.perform_action(player, action)
            if match.is_over():
                return match.result_for_player(sbb_player)

    def validate(self, current_generation, teams_population):
        for team in teams_population:
            if team.generation != current_generation: # dont evaluate teams that have just being created (to improve performance and to get training metrics)
                self.evaluate_team(team, DefaultEnvironment.MODE['validation'])
        score = [p.score_testset_ for p in teams_population]
        best_team = teams_population[score.index(max(score))]
        print("\nChampion team test score in the initial matches: "+str(best_team.score_testset_))
        self.evaluate_team(best_team, DefaultEnvironment.MODE['champion'])
        return best_team

    def metrics(self):
        msg = ""
        msg += "\n### Environment Info:"
        msg += "\ntotal inputs: "+str(self.total_inputs_)
        msg += "\ntotal actions: "+str(self.total_actions_)
        msg += "\nactions mapping: "+str(self.action_mapping_)
        msg += "\npositions: "+str(self.total_positions_)
        msg += "\nmatches per opponents (for each position): "+str(Config.USER['training_parameters']['populations']['points']/len(self.opponents_))
        return msg