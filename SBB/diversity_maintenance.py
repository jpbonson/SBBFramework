import numpy
from config import CONFIG

class DiversityMaintenance():
    """
    This class contains all the diversity maintenance methods.
    """

    @staticmethod
    def genotype_diversity(teams_population):
        """
        Diversity based on the genotype distance between teams, as described in:
            "Kelly, Stephen, and Malcolm I. Heywood. "Genotypic versus Behavioural Diversity for Teams 
            of Programs Under the 4-v-3 Keepaway Soccer Task." Twenty-Eighth AAAI Conference on 
            Artificial Intelligence. 2014."
        """
        for team in teams_population:
            # create array of distances to other teams
            distances = []
            for other_team in teams_population:
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
            raw_fitness = team.fitness_
            team.fitness_ = (1.0-p)*(raw_fitness) + p*diversity
        return teams_population