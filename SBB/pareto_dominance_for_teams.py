from diversity_maintenance import DiversityMaintenance
from utils.helpers import is_nearly_equal_to
from config import Config 

class ParetoDominanceForTeams():
    """
    Pareto dominance: Given a set of objectives, a solution is said to Pareto dominate another if the 
    first is not inferior to the second in all objectives, and, additionally, there is at least one 
    objective where it is better.

    This code is based on Stephen's version of the C++ SBB, that was focused in using pareto for 
    multi-objective between fitness and novelty for the teams.
    """

    @staticmethod
    def run(teams_population, novelty, teams_to_keep, pareto_threshold = 0.01):
        for team in teams_population:
            team.domBy_ = 0
            team.domOf_ = 0

        front = []
        dominateds = []
        for indexA, teamA in enumerate(teams_population):
            for indexB, teamB in enumerate(teams_population):
                # check if there are teams that have a better or equal [fitness, novelty] and that are better in at least 
                # one of the dimensions. If yes, then teamA is dominated by these teams.
                if (teamB.fitness_ >= teamA.fitness_ and teamB.diversity_[novelty] >= teamA.diversity_[novelty] and 
                        ((teamB.fitness_ > teamA.fitness_ and not is_nearly_equal_to(teamA.fitness_, teamB.fitness_, pareto_threshold)) or
                        (teamB.diversity_[novelty] > teamA.diversity_[novelty] and 
                        not is_nearly_equal_to(teamA.diversity_[novelty], teamB.diversity_[novelty], pareto_threshold)))):
                    teamA.domBy_ += 1
                    teamB.domOf_ += 1
                    if teamA not in dominateds:
                        dominateds.append(teamA)
            if teamA.domBy_ == 0:
                front.append(teamA)

        # use this score to balance the teams between remove and keep
        for team in teams_population:
            team.submission_score_ = team.domBy_/float(len(teams_population)) # use it to add teams to the front (the lower, the better)
            team.dominance_score_ = team.domOf_/float(len(teams_population)) # use it to remove teams from the front (the higher, the better)

        pareto_front = list(front)
        keep_solutions = list(front)
        remove_solutions = list(dominateds)
        if len(keep_solutions) < teams_to_keep: # must include some teams from dominateds
            sorted_solutions = sorted(dominateds, key=lambda solution: solution.submission_score_, reverse = False) # worse ones first
            for solution in sorted_solutions:
                if solution not in keep_solutions:
                    keep_solutions.append(solution)
                    remove_solutions.remove(solution)
                if len(keep_solutions) == teams_to_keep:
                    break
        if len(keep_solutions) > teams_to_keep: # must discard some teams from front
            sorted_solutions = sorted(front, key=lambda solution: solution.dominance_score_, reverse = True) # better ones first
            for solution in sorted_solutions:
                keep_solutions.remove(solution)
                remove_solutions.append(solution)
                if len(keep_solutions) == teams_to_keep:
                    break

        # definir onde a diversity da genration vai ser setada se houver mais de uma em 'use_and_show'

        # dah para melhorar o calculo de diversity, quando se usa mais de uma diversity (soh calcular a daquela generation)

        # alterar 'is_nearly_equal_threshold': 0.1,

        # refatorar classe

        # opcao de randomly swap between diversity metrics (conferir se esta funcionando)

        # remover p_value

        # conferir tests

        return keep_solutions, remove_solutions, pareto_front

    @staticmethod
    def _pareto_front(solutions, results_map):
        """
        Finds the pareto front, i.e. the pareto dominant solutions.
        """
        front = []
        dominateds = []
        i = 0
        for solution, outcomes1 in zip(solutions, results_map):
            is_dominated = False
            j = 0
            for outcomes2 in results_map:
                is_dominated, is_equal = ParetoDominanceForTeams._check_if_is_dominated(outcomes1, outcomes2)
                if j < i and is_equal: # also dominated if equal to a previous processed item, since this one would be irrelevant
                    is_dominated = True
                if is_dominated:
                    break
                j += 1
            if is_dominated:
                dominateds.append(solution)
            else:
                front.append(solution)
            i += 1
        return front, dominateds

    @staticmethod
    def _check_if_is_dominated(results1, results2):
        """
        Check if a solution is domninated or equal to another, assuming that higher results are better than lower ones.
        """  
        equal = True
        for index in range(len(results1)):
            if not is_nearly_equal_to(results1[index], results2[index]):
                equal = False
                if(results1[index] > results2[index]): # not dominated since "results1" is greater than "results2" in this dimension
                    return False, equal
        if equal:
            return False, equal
        else:
            return True, equal

    @staticmethod
    def _balance_pareto_front_to_up(population, keep_solutions, remove_solutions, to_keep):
        sorted_solutions = sorted(population, key=lambda solution: solution.fitness_, reverse = True) # better ones first
        for solution in sorted_solutions:
            if solution not in keep_solutions:
                keep_solutions.append(solution)
                remove_solutions.remove(solution)
            if len(keep_solutions) == to_keep:
                break
        return keep_solutions, remove_solutions

    @staticmethod
    def _balance_pareto_front_to_down(population, keep_solutions, remove_solutions, to_keep):
        sorted_solutions = sorted(population, key=lambda solution: solution.fitness_, reverse = False) # worse ones first
        for solution in sorted_solutions:
            keep_solutions.remove(solution)
            remove_solutions.append(solution)
            if len(keep_solutions) == to_keep:
                break
        return keep_solutions, remove_solutions