import random
import numpy
from team import Team
from diversity_maintenance import DiversityMaintenance
from pareto_dominance import ParetoDominance
from environments.default_environment import DefaultEnvironment
from utils.helpers import round_value
from config import Config

class Selection:
    """
    Encapsulates the selection algorithm, that selects the best individuals, generates children, 
    and replaces the worst individuals.
    """

    def __init__(self, environment):
        self.environment = environment

    def run(self, current_generation, teams_population, programs_population, validation = False):
        teams_population = self._evaluate_teams(teams_population)
        keep_teams, remove_teams, pareto_front = self._select_teams_to_keep_and_remove(teams_population)
        teams_to_clone = self._select_teams_to_clone(keep_teams)

        if validation:
            diversity_means = self._calculate_global_diversity_means(teams_population, self.environment.point_population())
        else:
            diversity_means = None

        teams_population = self._remove_teams(teams_population, remove_teams)
        programs_population = self._remove_programs_with_no_teams(programs_population)
        teams_population, programs_population = self._create_mutated_teams(current_generation, teams_to_clone, teams_population, programs_population)
        self._check_for_bugs(teams_population, programs_population)
        return teams_population, programs_population, pareto_front, diversity_means

    def _evaluate_teams(self, teams_population):
        """
        Create a point population in the environment, use it to evaluate the teams (calculate fitness_ and results_per_points_), 
        and then use the teams results to evluate the point population.
        """
        self.environment.setup(teams_population)
        self.environment.evaluate_teams_population(teams_population)
        self.environment.evaluate_point_population(teams_population)
        return teams_population

    def _select_teams_to_keep_and_remove(self, teams_population):
        teams_to_remove = int(Config.USER['training_parameters']['replacement_rate']['teams']*float(len(teams_population)))
        teams_to_keep = len(teams_population) - teams_to_remove

        if Config.USER['advanced_training_parameters']['use_pareto_for_team_population_selection']:
            keep_teams, remove_teams, pareto_front = ParetoDominance.pareto_front_for_teams(teams_population, self.environment.point_population(), teams_to_keep)
        else:
            DiversityMaintenance.apply_diversity_maintenance_to_teams(teams_population, self.environment.point_population())
            sorted_solutions = sorted(teams_population, key=lambda solution: solution.fitness_, reverse=True)
            keep_teams = sorted_solutions[0:teams_to_keep]
            remove_teams = sorted_solutions[teams_to_keep:]
            pareto_front = []
        return keep_teams, remove_teams, pareto_front

    def _calculate_global_diversity_means(self, teams_population, point_population):
        """
        Apply diversity maintenance to obtain the global and individual diversity values for all teams, that are useful metrics 
        when validating.
        If you are going to modify this method, ATTENTION: This method always must occur after _select_teams_to_keep_and_remove() and 
        _select_teams_to_clone(), in order to don't modify the fitness value of the teams. But it also never should be after 
        _remove_teams(), or this method will not be able to compute the global diversity.
        """
        DiversityMaintenance.apply_diversity_maintenance_to_teams(teams_population, point_population)
        diversity_means = {}
        if Config.USER['advanced_training_parameters']['diversity']['genotype_fitness_maintanance']:
            diversity_means['genotype_diversity'] = round_value(numpy.mean([t.diversity_['genotype_diversity'] for t in teams_population]))
        if Config.USER['advanced_training_parameters']['diversity']['fitness_sharing']:
            diversity_means['fitness_sharing_diversity'] = round_value(numpy.mean([t.diversity_['fitness_sharing_diversity'] for t in teams_population]))
        return diversity_means

    def _remove_teams(self, teams_population, remove_teams):
        for team in remove_teams:
            team.remove_references()
        teams_population = [team for team in teams_population if team not in remove_teams]
        return teams_population

    def _select_teams_to_clone(self, teams_population):
        new_teams_to_create = Config.USER['training_parameters']['populations']['teams'] - len(teams_population)
        fitness = [team.fitness_ for team in teams_population]
        total_fitness = sum(fitness)
        probabilities = [f/total_fitness for f in fitness]
        return numpy.random.choice(teams_population, size = new_teams_to_create, replace = False, p = probabilities)

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
        for team in teams_to_clone:
            clone = Team(current_generation, team.programs)
            if len(clone.programs) == Config.USER['training_parameters']['team_size']['max']:
                # remove programs that were never used by the parent team
                to_remove = []
                for program in clone.programs:
                    if program not in team.active_programs_:
                        to_remove.append(program)
                for program in to_remove:
                    if clone._is_ok_to_remove(program):
                        clone.remove_program(program)
            programs_population = clone.mutate(programs_population)
            teams_population.append(clone)
        return teams_population, programs_population

    def _check_for_bugs(self, teams_population, programs_population):
        if len(teams_population) != Config.USER['training_parameters']['populations']['teams']:
            raise ValueError("The size of the teams population changed during selection! You got a bug!")