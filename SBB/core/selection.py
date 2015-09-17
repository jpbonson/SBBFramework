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
        programs_population = self._remove_programs_with_no_teams(programs_population)
        teams_population, programs_population = self._create_mutated_teams(current_generation, teams_to_clone, teams_population, programs_population)
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
            DiversityMaintenance.calculate_diversities(teams_population, self.environment.point_population())
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
            return numpy.random.choice(teams_population, size = new_teams_to_create, replace = False, p = probabilities)
        else:
            return numpy.random.choice(teams_population, size = new_teams_to_create, replace = False)

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