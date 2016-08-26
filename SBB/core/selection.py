import random
import numpy
from team import Team
from diversity_maintenance import DiversityMaintenance
from pareto_dominance_for_teams import ParetoDominanceForTeams
from ..environments.default_environment import DefaultEnvironment
from ..utils.helpers import round_value
from ..config import Config

class Selection:
    """
    Encapsulates the selection algorithm, that selects the best individuals, generates children, 
    and replaces the worst individuals.
    """

    def __init__(self, environment):
        self.environment = environment
        self.previous_diversity_ = None

    def run(self, current_generation, teams_population, programs_population, validation = False):
        teams_population = self._evaluate_teams(teams_population)
        keep_teams, remove_teams, pareto_front = self._select_teams_to_keep_and_remove(teams_population, validation)
        teams_to_clone = self._select_teams_to_clone(keep_teams)
        teams_population = self._remove_teams(teams_population, remove_teams)
        teams_population = self._prune_teams(teams_population)
        teams_population, programs_population = self._create_mutated_teams(current_generation, teams_to_clone, teams_population, programs_population)
        programs_population = self._remove_programs_with_no_teams(programs_population)
        self._check_for_bugs(teams_population, programs_population)
        return teams_population, programs_population, pareto_front

    def _evaluate_teams(self, teams_population):
        """
        Create a point population in the environment, use it to evaluate the teams (calculate fitness_ and results_per_points_), 
        and then use the teams results to evluate the point population.
        """
        self.environment.setup(teams_population)
        self.environment.evaluate_teams_population_for_training(teams_population)
        self.environment.evaluate_point_population(teams_population)
        return teams_population

    def _select_teams_to_keep_and_remove(self, teams_population, is_validation):
        teams_to_remove = int(Config.USER['training_parameters']['replacement_rate']['teams']*float(len(teams_population)))
        teams_to_keep = len(teams_population) - teams_to_remove

        diversities_to_apply = Config.USER['advanced_training_parameters']['diversity']['use_and_show']
        if len(diversities_to_apply) == 0:
            if len(Config.USER['advanced_training_parameters']['diversity']['only_show']) > 0:
                DiversityMaintenance.calculate_diversities(teams_population, self.environment.point_population())
            sorted_solutions = sorted(teams_population, key=lambda solution: solution.fitness_, reverse=True)
            keep_teams = sorted_solutions[0:teams_to_keep]
            remove_teams = sorted_solutions[teams_to_keep:]
            pareto_front = []
        else:
            options = list(Config.USER['advanced_training_parameters']['diversity']['use_and_show'])
            if len(diversities_to_apply) > 1 and self.previous_diversity_:
                options.remove(self.previous_diversity_)
            novelty = random.choice(options)
            if Config.USER['advanced_training_parameters']['diversity']['use_novelty_archive']:
                DiversityMaintenance.calculate_diversities(teams_population+list(Config.RESTRICTIONS['novelty_archive']['samples']), self.environment.point_population())
                sorted_solutions = sorted(teams_population, key=lambda solution: solution.diversity_[novelty], reverse=True)
                sorted_samples = sorted(Config.RESTRICTIONS['novelty_archive']['samples'], key=lambda solution: solution.diversity_[novelty], reverse=False)
                if len(Config.RESTRICTIONS['novelty_archive']['samples']) == Config.RESTRICTIONS['novelty_archive']['samples'].maxlen:
                    for team in sorted_samples[0:Config.RESTRICTIONS['novelty_archive']['threshold']]:
                        Config.RESTRICTIONS['novelty_archive']['samples'].remove(team)
                for team in sorted_solutions[0:Config.RESTRICTIONS['novelty_archive']['threshold']]:
                    Config.RESTRICTIONS['novelty_archive']['samples'].append(team)
            else:
                DiversityMaintenance.calculate_diversities(teams_population, self.environment.point_population())
            if Config.USER['advanced_training_parameters']['diversity']['only_novelty']:
                sorted_solutions = sorted(teams_population, key=lambda solution: solution.diversity_[novelty], reverse=True)
                keep_teams = sorted_solutions[0:teams_to_keep]
                remove_teams = sorted_solutions[teams_to_keep:]
                pareto_front = []
            else:
                keep_teams, remove_teams, pareto_front = ParetoDominanceForTeams.run(teams_population, novelty, teams_to_keep)
            self.previous_diversity_ = novelty
        return keep_teams, remove_teams, pareto_front

    def _remove_teams(self, teams_population, remove_teams):
        for team in remove_teams:
            team.remove_references()
        teams_population = [team for team in teams_population if team not in remove_teams]
        return teams_population

    def _select_teams_to_clone(self, teams_population):
        new_teams_to_create = Config.USER['training_parameters']['populations']['teams'] - len(teams_population)
        if Config.USER['advanced_training_parameters']['use_weighted_probability_selection']:
            fitness = []
            for team in teams_population:
                if team.fitness_ == 0.0:
                    fitness.append(0.000001)
                else:
                    fitness.append(team.fitness_)
            total_fitness = sum(fitness)
            probabilities = [f/float(total_fitness) for f in fitness]
            result =  numpy.random.choice(teams_population, size = new_teams_to_create, replace = True, p = probabilities)
            return result
        else:
            return numpy.random.choice(teams_population, size = new_teams_to_create, replace = True)

    def _prune_teams(self, teams_population):
        for team in teams_population:
            if len(team.programs) == Config.USER['training_parameters']['team_size']['max']:
                team.prune_partial()
        return teams_population

    def _remove_programs_with_no_teams(self, programs_population):
        to_remove = []
        for p in programs_population:
            if len(p.teams_) == 0:
                to_remove.append(p)
        for p in programs_population:
            if p in to_remove:
                programs_population.remove(p)
        return programs_population

    def _create_mutated_teams(self, current_generation, teams_to_clone, teams_population, programs_population):
        """
        Create new mutated teams, cloning the old ones and mutating. New programs are be added to the program population 
        for the mutated programs in the new teams.
        """
        if Config.USER['advanced_training_parameters']['use_profiling']:
            bid_profiles = self._generate_bid_profiles(teams_to_clone)
            teams_population, programs_population = self._clone_teams_with_profiling(current_generation, teams_to_clone, teams_population, programs_population, bid_profiles)
        else:
            teams_population, programs_population = self._clone_teams_without_profiling(current_generation, teams_to_clone, teams_population, programs_population)
        return teams_population, programs_population

    def _generate_bid_profiles(self, teams_to_clone):
        bid_profiles = []
        for team in teams_to_clone:
            bid_profiles.append(team.generate_profile())
        return bid_profiles

    def _clone_teams_with_profiling(self, current_generation, teams_to_clone, teams_population, programs_population, bid_profiles):
        for team, parent_profile in zip(teams_to_clone, bid_profiles):
            clone = Team(current_generation, team.programs)
            programs_population = clone.mutate(programs_population)
            child_profile = clone.generate_profile()
            while parent_profile == child_profile:
                programs_population = clone.mutate(programs_population)
                child_profile = clone.generate_profile()
            while not self._team_has_different_bid_profile_overall(child_profile, bid_profiles):
                programs_population = clone.mutate(programs_population)
                child_profile = clone.generate_profile()
            teams_population.append(clone)
        return teams_population, programs_population

    def _clone_teams_without_profiling(self, current_generation, teams_to_clone, teams_population, programs_population):
        for team in teams_to_clone:
            clone = Team(current_generation, team.programs)
            programs_population = clone.mutate(programs_population)
            teams_population.append(clone)
        return teams_population, programs_population

    def _team_has_different_bid_profile_overall(self, team_profile, bid_profiles):
        for other_profile in bid_profiles:
            if team_profile == other_profile:
                return False
        return True

    def _check_for_bugs(self, teams_population, programs_population):
        if len(teams_population) != Config.USER['training_parameters']['populations']['teams']:
            raise ValueError("The size of the teams population changed during selection! You got a bug!")