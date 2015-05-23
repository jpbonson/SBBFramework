import random
import copy
from program import Program
from team import Team
from diversity_maintenance import DiversityMaintenance
from utils.helpers import weighted_choice, pareto_front, balance_population_to_up, balance_population_to_down
from config import CONFIG

class Selection:
    """
    Encapsulates the selection algorithm, that selects the best individuals, generates children, 
    and replaces the worst individuals.
    """

    def __init__(self, environment):
        self.environment = environment

    def run(self, current_generation, teams_population, programs_population):
        teams_population = self._evaluate_teams(teams_population) # to calculate fitness_ and results_per_points_
        teams_to_remove = int(CONFIG['training_parameters']['replacement_rate']['teams']*float(len(teams_population)))
        teams_to_keep = len(teams_population) - teams_to_remove

        if CONFIG['advanced_training_parameters']['use_pareto_for_team_population_selection']:
            keep_teams, remove_teams = self._use_pareto_front_to_select_solutions(teams_population, teams_to_keep)
        else:
            teams_population = self._apply_diversity_maintenance(teams_population) # that modifies fitness to maintains diversity
            sorted_solutions = sorted(teams_population, key=lambda solution: solution.fitness_, reverse=True)
            keep_teams = sorted_solutions[0:teams_to_keep]
            remove_teams = sorted_solutions[teams_to_keep:]

        teams_population = self._remove_teams(teams_population, remove_teams)
        teams_to_clone = self._select_teams_to_clone(keep_teams)
        programs_population = self._remove_programs_with_no_teams(programs_population)
        programs_population, new_programs = self._create_mutated_programs(current_generation, programs_population)
        teams_population = self._create_mutated_teams(current_generation, teams_population, teams_to_clone, new_programs)
        self._check_for_bugs(teams_population, programs_population)
        return teams_population, programs_population

    def _evaluate_teams(self, teams_population):
        self.environment.setup_point_population(teams_population)
        for t in teams_population:
            self.environment.evaluate_team(t, is_training=True)
        self.environment.evaluate_point_population(teams_population)
        return teams_population

    def _use_pareto_front_to_select_solutions(self, teams_population, to_keep):
        results_map = []
        for team in teams_population:
            results = []
            for point in self.environment.point_population():
                results.append(team.results_per_points_[point.point_id])
            results_map.append(results)
        front, dominateds = pareto_front(teams_population, results_map)

        keep_solutions = front
        remove_solutions = dominateds
        if len(keep_solutions) < to_keep:  # must include some teams from dominateds
            teams_population = self._apply_diversity_maintenance(teams_population)
            keep_solutions, remove_solutions = balance_population_to_up(teams_population, keep_solutions, remove_solutions, to_keep)
        if len(keep_solutions) > to_keep: # must discard some teams from front
            front = self._apply_diversity_maintenance(front)
            keep_solutions, remove_solutions = balance_population_to_down(front, keep_solutions, remove_solutions, to_keep)
        return keep_solutions, remove_solutions

    def _apply_diversity_maintenance(self, teams_population):
        if CONFIG['advanced_training_parameters']['diversity']['genotype_fitness_maintanance']:
            teams_population = DiversityMaintenance.genotype_diversity(teams_population)
        if CONFIG['advanced_training_parameters']['diversity']['fitness_sharing']:
            teams_population = DiversityMaintenance.fitness_sharing(self.environment, teams_population)
        return teams_population

    def _remove_teams(self, teams_population, remove_teams):
        for team in remove_teams:
            team.remove_references()
        teams_population = [team for team in teams_population if team not in remove_teams]
        return teams_population

    def _select_teams_to_clone(self, teams_population):
        new_teams_to_create = CONFIG['training_parameters']['populations']['teams'] - len(teams_population)
        teams_to_clone = []
        while len(teams_to_clone) < new_teams_to_create:
            fitness = [team.fitness_ for team in teams_population]
            index = weighted_choice(fitness)
            teams_to_clone.append(teams_population[index])
        return teams_to_clone

    def _remove_programs_with_no_teams(self, programs_population):
        to_remove = []
        for p in programs_population:
            if len(p.teams_) == 0:
                to_remove.append(p)
        for p in programs_population:
            if p in to_remove:
                programs_population.remove(p)
        return programs_population

    def _create_mutated_programs(self, current_generation, programs_population):
        """
        Add new mutated programs to population, so it has the same size as before.
        """
        new_programs_to_create = CONFIG['training_parameters']['populations']['programs'] - len(programs_population)
        programs_to_clone = random.sample(programs_population, new_programs_to_create)
        new_programs = []
        for program in programs_to_clone:
            clone = Program(current_generation, copy.deepcopy(program.instructions), program.action)
            clone.mutate()
            new_programs.append(clone)
            programs_population.append(clone)
        return programs_population, new_programs

    def _create_mutated_teams(self, current_generation, teams_population, teams_to_clone, new_programs):
        """
        Create new mutated teams, cloning the old ones and mutating (if adding a program, can only add a new created program)
        """
        for team in teams_to_clone:
            clone = Team(current_generation, team.programs)
            clone.mutate(new_programs)
            teams_population.append(clone)
        return teams_population

    def _check_for_bugs(self, teams_population, programs_population):
        if len(teams_population) != CONFIG['training_parameters']['populations']['teams']:
            raise ValueError("The size of the teams population changed during selection! You got a bug!")
        if len(programs_population) != CONFIG['training_parameters']['populations']['programs']:
            raise ValueError("The size of the programs population changed during selection! You got a bug!")