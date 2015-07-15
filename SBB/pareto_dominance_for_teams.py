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
    def sketch():
        for team in teams:
            team.domBy_ = 0
            team.domOf_ = 0

        dominatedTeams = []
        nonDominatedTeams = []
        for teamA in teams:
            for teamB in teams:
                # check if there are teams that have a better or equal [fitness, novelty] and that are better in at least 
                # one of the dimensions. If yes, then teamA is dominated by these teams.
                if (teamB.fitness >= teamA.fitness and teamB.novelty >= teamA.novelty and 
                    ((teamB.fitness > teamA.fitness and not is_nearly_equal_to(teamA.fitness, teamB.fitness)) or
                      (teamB.novelty > teamA.novelty and not is_nearly_equal_to(teamA.novelty, teamB.novelty)))):
                    teamA.domBy_ += 1
                    teamB.domOf_ += 1
                    if teamA not in dominatedTeams:
                        dominatedTeams.append(teamA)
            if teamA.domBy_ == 0:
                nonDominatedTeams.append(teamA)

        # use this score to balance the teams between rmeove and keep
        for team in teams:
            team.submission_score = team.domBy_/float(len(teams))
            team.dominance_score = team.domOf_/float(len(teams))
        
        # marcar atributos internos com_
        # conferir se separa as teams em grupos sem interseccao
        # conferir se ambas as metricas crescem ao longo das geracoes

        # definir onde a diversity da genration vai ser setada se houver mais de uma em 'use_and_show'

        # return keep_solutions, remove_solutions, pareto_front

    @staticmethod
    def pareto_front_for_teams(teams_population, point_population, to_keep, is_validation):
        """
        Finds the pareto front, i.e. the pareto dominant teams.
        """
        results_map = ParetoDominanceForTeams._generate_results_map_for_teams(teams_population, point_population)
        front, dominateds = ParetoDominanceForTeams._pareto_front(teams_population, results_map)

        pareto_front = [team for team in front]
        keep_solutions = front
        remove_solutions = dominateds
        if len(keep_solutions) < to_keep:  # must include some teams from dominateds
            DiversityMaintenance.calculate_diversities(teams_population, point_population, is_validation)

            diversities_to_apply = Config.USER['advanced_training_parameters']['diversity']['use_and_show']
            p = Config.USER['advanced_training_parameters']['diversity']['p_value']
            for team in teams_population:
                for diversity in diversities_to_apply:
                    team.fitness_ = (1.0-p)*(team.fitness_) + p*team.diversity_[diversity]

            keep_solutions, remove_solutions = ParetoDominanceForTeams._balance_pareto_front_to_up(teams_population, keep_solutions, remove_solutions, to_keep)
        if len(keep_solutions) > to_keep: # must discard some teams from front
            DiversityMaintenance.calculate_diversities(front, point_population, is_validation)

            diversities_to_apply = Config.USER['advanced_training_parameters']['diversity']['use_and_show']
            p = Config.USER['advanced_training_parameters']['diversity']['p_value']
            for team in teams_population:
                for diversity in diversities_to_apply:
                    team.fitness_ = (1.0-p)*(team.fitness_) + p*team.diversity_[diversity]

            keep_solutions, remove_solutions = ParetoDominanceForTeams._balance_pareto_front_to_down(front, keep_solutions, remove_solutions, to_keep)
        if len(keep_solutions) == to_keep:
            DiversityMaintenance.calculate_diversities(keep_solutions, point_population, is_validation) # in order to calculate fitness to obtain the teams to clone
        
            diversities_to_apply = Config.USER['advanced_training_parameters']['diversity']['use_and_show']
            p = Config.USER['advanced_training_parameters']['diversity']['p_value']
            for team in teams_population:
                for diversity in diversities_to_apply:
                    team.fitness_ = (1.0-p)*(team.fitness_) + p*team.diversity_[diversity]

        return keep_solutions, remove_solutions, pareto_front

    @staticmethod
    def _generate_results_map_for_teams(teams_population, point_population):
        """
        Create a a matrix of (points) x (results of teams for the point). This matrix is used by pareto to find a 
        front of teams that are able to solve various distinct points.
        """
        results_map = []
        for team in teams_population:
            results = []
            for point in point_population:
                results.append(team.results_per_points_[point.point_id])
            results_map.append(results)
        return results_map

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