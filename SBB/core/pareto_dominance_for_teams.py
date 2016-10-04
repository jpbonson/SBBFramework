from diversity_maintenance import DiversityMaintenance
from ..utils.helpers import is_nearly_equal_to
from ..config import Config 

class ParetoDominanceForTeams():
    """
    Pareto dominance: Given a set of objectives, a solution is said to Pareto dominate another if the 
    first is not inferior to the second in all objectives, and, additionally, there is at least one 
    objective where it is better.

    This code is based on Stephen's version of the C++ SBB, that was focused in using pareto for 
    multi-objective between fitness and novelty for the teams.
    """

    @staticmethod
    def run(teams_population, novelty, teams_to_keep):
        front, dominateds = ParetoDominanceForTeams._pareto_front(teams_population, novelty)
        pareto_front = list(front)
        keep_solutions = list(front)
        remove_solutions = list(dominateds)
        if len(keep_solutions) < teams_to_keep: # must include some teams from dominateds
            keep_solutions, remove_solutions = ParetoDominanceForTeams._balance_pareto_front_to_up(dominateds, keep_solutions, remove_solutions, teams_to_keep)
        if len(keep_solutions) > teams_to_keep: # must discard some teams from front
            keep_solutions, remove_solutions = ParetoDominanceForTeams._balance_pareto_front_to_down(front, keep_solutions, remove_solutions, teams_to_keep)
        return keep_solutions, remove_solutions, pareto_front

    @staticmethod
    def _pareto_front(teams_population, novelty):
        """
        Finds the pareto front, i.e. the pareto dominant solutions.
        """
        for team in teams_population:
            team.dom_by_ = 0
            team.dom_of_ = 0

        front = []
        dominateds = []
        for teamA in teams_population:
            for teamB in teams_population:
                # check if there are teams that have a better or equal [fitness, novelty] and that are better in at least 
                # one of the dimensions. If yes, then teamA is dominated by these teams.
                if ParetoDominanceForTeams._is_dominated(teamA, teamB, novelty):
                    teamA.dom_by_ += 1
                    teamB.dom_of_ += 1
                    if teamA not in dominateds:
                        dominateds.append(teamA)
            if teamA.dom_by_ == 0:
                front.append(teamA)

        # use this score to balance the teams between remove and keep
        for team in teams_population:
            team.submission_score_ = team.dom_by_/float(len(teams_population)) # use it to add teams to the front (the lower, the better)
            team.dominance_score_ = team.dom_of_/float(len(teams_population)) # use it to remove teams from the front (the higher, the better)
        return front, dominateds

    @staticmethod
    def _is_dominated(teamA, teamB, novelty):
        """
        Check if a solution is domninated or equal to another, assuming that higher results are better than lower ones.
        """  
        if (teamB.fitness_ >= teamA.fitness_ and teamB.diversity_[novelty] >= teamA.diversity_[novelty] and 
                ((teamB.fitness_ > teamA.fitness_ and not is_nearly_equal_to(teamA.fitness_, teamB.fitness_)) or
                (teamB.diversity_[novelty] > teamA.diversity_[novelty] and 
                not is_nearly_equal_to(teamA.diversity_[novelty], teamB.diversity_[novelty])))):
            return True
        return False

    @staticmethod
    def _balance_pareto_front_to_up(dominateds, keep_solutions, remove_solutions, teams_to_keep):
        available = [team for team in dominateds if team.fitness_ > 0.0]
        if len(available) < teams_to_keep:
            not_available = [team for team in dominateds if team.fitness_ == 0.0]
            available += not_available[:teams_to_keep-len(available)]
        sorted_solutions = sorted(available, key=lambda solution: solution.submission_score_, reverse = False) # worse ones first
        for solution in sorted_solutions:
            if solution not in keep_solutions:
                keep_solutions.append(solution)
                remove_solutions.remove(solution)
            if len(keep_solutions) == teams_to_keep:
                break
        return keep_solutions, remove_solutions

    @staticmethod
    def _balance_pareto_front_to_down(front, keep_solutions, remove_solutions, teams_to_keep):
        sorted_solutions = sorted(front, key=lambda solution: solution.dominance_score_, reverse = True) # better ones first
        for solution in sorted_solutions:
            keep_solutions.remove(solution)
            remove_solutions.append(solution)
            if len(keep_solutions) == teams_to_keep:
                break
        return keep_solutions, remove_solutions