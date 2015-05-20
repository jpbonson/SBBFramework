import random
import copy
from program import Program
from team import Team
from diversity_maintenance import DiversityMaintenance
from utils.helpers import weighted_choice, pareto_front
from config import CONFIG

class Selection:
    """
    Encapsulates the selection algorithm, that selects the best individuals, generates children, 
    and replaces the worst individuals.
    """

    def __init__(self, environment):
        self.environment = environment

    def run(self, current_generation, teams_population, programs_population):
        teams_population = self._evaluate_teams(teams_population) # to calculate fitness

        if CONFIG['advanced_training_parameters']['use_pareto_for_team_population_selection']:
            teams_to_be_replaced = int(CONFIG['training_parameters']['replacement_rate']['teams']*float(len(teams_population)))
            team_to_keep = len(teams_population) - teams_to_be_replaced
            results_map = []
            for team in teams_population:
                results = []
                for point in self.environment.point_population():
                    results.append(team.results_per_points[point.point_id])
                results_map.append(results)
            front, dominateds = pareto_front(results_map) # TODO
            # TODO: use diversity+fitness to add or remove from the pareto front
            raise SystemExit
        else:
            teams_population = self._apply_diversity_maintenance(teams_population) # that modifies fitness to maintains diversity
            teams_population = self._remove_worst_teams(teams_population)        
            teams_to_clone = self._select_teams_to_clone(teams_population)

        programs_population = self._remove_programs_with_no_teams(programs_population)
        programs_population, new_programs = self._create_mutated_programs(current_generation, programs_population)
        teams_population = self._create_mutated_teams(current_generation, teams_population, teams_to_clone, new_programs)
        return teams_population, programs_population

    def _evaluate_teams(self, teams_population):
        self.environment.setup_point_population()
        for t in teams_population:
            self.environment.evaluate(t, is_training=True)
        return teams_population

    def _apply_diversity_maintenance(self, teams_population):
        if CONFIG['advanced_training_parameters']['diversity']['genotype_fitness_maintanance']:
            DiversityMaintenance.genotype_diversity(teams_population)
        return teams_population

    def _remove_worst_teams(self, teams_population):
        teams_to_be_replaced = int(CONFIG['training_parameters']['replacement_rate']['teams']*float(len(teams_population)))
        team_to_keep = len(teams_population) - teams_to_be_replaced
        while len(teams_population) > team_to_keep:
            fitness = [t.fitness_ for t in teams_population]
            worst_team_index = fitness.index(min(fitness))
            worst_team = teams_population[worst_team_index]
            worst_team.remove_references()
            teams_population.remove(worst_team)
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