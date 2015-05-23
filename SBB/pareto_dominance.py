from utils.helpers import is_nearly_equal_to

class ParetoDominance():
    """
    Pareto dominance: Given a set of objectives, a solution is said to Pareto dominate another if the 
    first is not inferior to the second in all objectives, and, additionally, there is at least one 
    objective where it is better.
    """

    @staticmethod
    def pareto_front(solutions, results_map): # unit test!
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
                is_dominated, is_equal = ParetoDominance._check_if_is_dominated(outcomes1, outcomes2)
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
    def _check_if_is_dominated(results1, results2): # unit test!
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
    def balance_pareto_front_to_up(population, keep_solutions, remove_solutions, to_keep):
        sorted_solutions = sorted(population, key=lambda solution: solution.fitness_, reverse=True)
        for solution in sorted_solutions:
            if solution not in keep_solutions:
                keep_solutions.append(solution)
                remove_solutions.remove(solution)
            if len(keep_solutions) == to_keep:
                break
        return keep_solutions, remove_solutions

    @staticmethod
    def balance_pareto_front_to_down(population, keep_solutions, remove_solutions, to_keep):
        sorted_solutions = sorted(population, key=lambda solution: solution.fitness_, reverse=False)
        for solution in sorted_solutions:
            keep_solutions.remove(solution)
            remove_solutions.append(solution)
            if len(keep_solutions) == to_keep:
                break
        return keep_solutions, remove_solutions