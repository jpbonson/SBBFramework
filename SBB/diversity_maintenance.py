import numpy
from config import CONFIG

class DiversityMaintenance():
    """
    This class contains all the diversity maintenance methods. These methods should only 
    modify the fitness_ attribute, nothing else.
    """

    @staticmethod
    def genotype_diversity(population):
        """
        Diversity based on the genotype distance between teams, as described in:
            "Kelly, Stephen, and Malcolm I. Heywood. "Genotypic versus Behavioural Diversity for Teams 
            of Programs Under the 4-v-3 Keepaway Soccer Task." Twenty-Eighth AAAI Conference on 
            Artificial Intelligence. 2014."
        """
        for team in population:
            # create array of distances to other teams
            distances = []
            for other_team in population:
                if team != other_team:
                    num_programs_intersection = len(set(team.active_programs_).intersection(other_team.active_programs_))
                    num_programs_union = len(set(team.active_programs_).union(other_team.active_programs_))
                    if num_programs_union > 0:
                        distance = 1.0 - (float(num_programs_intersection)/float(num_programs_union))
                    else:
                        distance = 1.0
                    distances.append(distance)
            # get mean of the k nearest neighbours
            sorted_list = sorted(distances)
            k = CONFIG['advanced_training_parameters']['diversity_configs']['genotype_fitness_maintanance']['k']
            min_values = sorted_list[:k]
            diversity = numpy.mean(min_values)
            # calculate fitness
            p = CONFIG['advanced_training_parameters']['diversity_configs']['genotype_fitness_maintanance']['p_value']
            team.fitness_ = (1.0-p)*(team.fitness_) + p*diversity
        return population

    @staticmethod
    def fitness_sharing(environment, population):
        """
        Uses the fitness sharing algorithm, so that individuals obtains more fitness by being able to solve
        points that other individuals can't. It assumes that all dimension have the same weight (if it is not
        true, normalize the dimensions before applying fitness sharing).
        """
        # calculate denominators in each dimension
        denominators = [1.0] * CONFIG['training_parameters']['populations']['points'] # initialized to 1 so we don't divide by zero
        for index, point in enumerate(environment.point_population()):
            for individual in population:
                denominators[index] += float(individual.results_per_points_[point.point_id])

        # calculate fitness
        p = CONFIG['advanced_training_parameters']['diversity_configs']['fitness_sharing']['p_value']
        for individual in population:
            score = 0.0
            for index, point in enumerate(environment.point_population()):
                score += float(individual.results_per_points_[point.point_id]) / denominators[index]
            diversity = score/float(len(environment.point_population()))
            individual.fitness_ = (1.0-p)*(individual.fitness_) + p*diversity
        return population

    @staticmethod
    def fitness_sharing_for_points(population, results_map):
        """
        Equal to fitness_sharing, but works specifically for points (ie. dont have previous fitness values and uses 'results_map').
        """
        # calculate denominators in each dimension
        denominators = [1.0] * len(results_map[0]) # initialized to 1 so we don't divide by zero
        for individual, results in zip(population, results_map):
            for index, value in enumerate(results):
                denominators[index] += float(value)

        # calculate fitness
        for individual, results in zip(population, results_map):
            score = 0.0
            for index, value in enumerate(results):
                score += float(value) / denominators[index]
            individual.fitness_ = score/float(len(results_map[0]))
        return population