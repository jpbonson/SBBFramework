import bz2
import math
import numpy
from scipy import stats
from scipy.spatial.distance import hamming, euclidean
from collections import defaultdict
from ..utils.helpers import round_value
from ..config import Config

class DiversityMaintenance():
    """
    This class contains all the diversity maintenance methods for teams.
    """

    @staticmethod
    def calculate_diversities(teams_population, point_population):
        diversities_to_calculate = list(Config.USER['advanced_training_parameters']['diversity']['use_and_show'])
        diversities_to_calculate += Config.USER['advanced_training_parameters']['diversity']['only_show']

        diversities_to_calculate = set(diversities_to_calculate)
        if "fitness_sharing" in diversities_to_calculate:
            DiversityMaintenance._fitness_sharing(teams_population, point_population)
            diversities_to_calculate.remove("fitness_sharing")
        if len(diversities_to_calculate) > 0:
            DiversityMaintenance.calculate_diversities_based_on_distances(teams_population, 
                Config.USER['advanced_training_parameters']['diversity']['k'], diversities_to_calculate)

    @staticmethod
    def calculate_diversities_based_on_distances(population, k, distances):
        """
        The kNN algorithm is applied to the list of 
        distances, to get the k most similar teams. The diversity is average distance of the k teams.
        In the end, teams with more uncommon program sets will obtain higher diversity scores.
        """
        for team in population:
            # create array of distances to other teams
            results = defaultdict(list)
            for other_team in population:
                if team != other_team:
                    for distance in distances:
                        result = getattr(DiversityMaintenance, "_"+distance)(team, other_team)
                        results[distance].append(result)
            # get mean of the k nearest neighbours
            for distance in distances:
                sorted_list = sorted(results[distance])
                min_values = sorted_list[:k]
                diversity = numpy.mean(min_values)
                team.diversity_[distance] = round_value(diversity)

    @staticmethod
    def _fitness_sharing(population, point_population):
        """
        Uses the fitness sharing algorithm, so that individuals obtains more fitness by being able to solve
        points that other individuals can't. It assumes that all dimension have the same weight (if it is not
        true, normalize the dimensions before applying fitness sharing).
        """
        # calculate denominators in each dimension
        denominators = [1.0] * len(point_population) # initialized to 1 so we don't divide by zero
        for index, point in enumerate(point_population):
            for team in population:
                denominators[index] += float(team.results_per_points_[point.point_id_])

        # calculate fitness
        for team in population:
            score = 0.0
            for index, point in enumerate(point_population):
                score += float(team.results_per_points_[point.point_id_]) / denominators[index]
            diversity = score/float(len(point_population))
            team.diversity_['fitness_sharing'] = round_value(diversity)

    @staticmethod
    def _genotype(team, other_team):
        """
        Calculate the distance between pairs of teams, where the distance is the intersection of active 
        programs divided by the union of active programs. Active programs are the ones who the output 
        was selected at least once during the run.

        More details in: 
            "Kelly, Stephen, and Malcolm I. Heywood. "Genotypic versus Behavioural Diversity for Teams 
            of Programs Under the 4-v-3 Keepaway Soccer Task." Twenty-Eighth AAAI Conference on 
            Artificial Intelligence. 2014."

        Examples:
        1) 1 2 e 2 3 (mid ground) => 1 - 1/3 = 0.66
        2) 1 2 e 1 2 (least distant) => 1 - 2/2 = 0.0
        3) 1 2 e 3 4 (most distant) => 1 - 0/4 = 1.0
        """
        num_programs_intersection = len(set(team.active_programs_).intersection(other_team.active_programs_))
        num_programs_union = len(set(team.active_programs_).union(other_team.active_programs_))
        if num_programs_union > 0:
            distance = 1.0 - (float(num_programs_intersection)/float(num_programs_union))
        else:
            distance = 1.0
            print "Error: No union between teams' active programs! Look for bugs."
            raise SystemExit
        return distance

    @staticmethod
    def _entropy_c2(team, other_team):
        action_sequence = team.action_sequence_['coding2']
        other_action_sequence = other_team.action_sequence_['coding2']
        options = Config.RESTRICTIONS['total_raw_actions']
        distance = DiversityMaintenance._general_relative_entropy_distance(action_sequence, other_action_sequence, options)
        return distance

    @staticmethod
    def _hamming_c3(team, other_team):
        return hamming(team.action_sequence_['coding3'], other_team.action_sequence_['coding3'])

    @staticmethod
    def _ncd_c3(team, other_team):
        action_sequence = list(team.action_sequence_['coding3'])
        action_sequence = [str(a) for a in action_sequence]
        other_action_sequence = list(other_team.action_sequence_['coding3'])
        other_action_sequence = [str(a) for a in other_action_sequence]
        distance = DiversityMaintenance._general_normalized_compression_distance(action_sequence, other_action_sequence)
        return distance

    @staticmethod
    def _entropy_c3(team, other_team):
        action_sequence = team.action_sequence_['coding3']
        other_action_sequence = other_team.action_sequence_['coding3']
        options = Config.RESTRICTIONS['diversity']['total_bins']
        distance = DiversityMaintenance._general_relative_entropy_distance(action_sequence, other_action_sequence, options)
        return distance

    @staticmethod
    def _ncd_c4(team, other_team):
        action_sequence = team.action_sequence_['coding4']
        other_action_sequence = other_team.action_sequence_['coding4']
        distance = DiversityMaintenance._general_normalized_compression_distance(action_sequence, other_action_sequence)
        return distance

    @staticmethod
    def _euclidean(team, other_team):
        value = euclidean(team.action_sequence_['coding3'], other_team.action_sequence_['coding3'])
        max_value = DiversityMaintenance._get_max_euclidean(Config.RESTRICTIONS['diversity']['total_bins'])
        result = value/float(max_value)
        return result

    @staticmethod
    def _get_max_euclidean(options):
        if 'max_euclidean' not in Config.RESTRICTIONS['diversity']:
            max_value = math.sqrt(((options-1)**2)*Config.USER['training_parameters']['populations']['points'])
            Config.RESTRICTIONS['diversity']['max_euclidean'] = max_value
        return Config.RESTRICTIONS['diversity']['max_euclidean']

    @staticmethod
    def _general_normalized_compression_distance(action_sequence, other_action_sequence):
        """
        More details in: 
            Gomez, Faustino J. "Sustaining diversity using behavioral information distance." Proceedings of the 
            11th Annual conference on Genetic and evolutionary computation. ACM, 2009.
        """
        if len(action_sequence) == len(other_action_sequence):
            if action_sequence == other_action_sequence:
                return 0.0
        x_len = len(bz2.compress("".join(action_sequence)))
        y_len = len(bz2.compress("".join(other_action_sequence)))
        xy_len = len(bz2.compress("".join(action_sequence+other_action_sequence)))
        distance = (xy_len - min(x_len, y_len))/float(max(x_len, y_len))
        distance = distance/Config.RESTRICTIONS['diversity']['max_ncd']
        if distance < 0.0:
            print "Warning! Value lower than 0.0 for NCD! Value: "+str(distance)+" ("+str(x_len)+","+str(y_len)+","+str(xy_len)+")"
            distance = 0.0
        if distance > 1.0:
            print "Warning! Value higher than 1.0 for NCD! Value: "+str(distance)+" ("+str(x_len)+","+str(y_len)+","+str(xy_len)+")"
            distance = 1.0
        return distance

    @staticmethod
    def _general_relative_entropy_distance(action_sequence, other_action_sequence, options):
        """

        """
        if len(action_sequence) == len(other_action_sequence):
            if action_sequence == other_action_sequence:
                return 0.0
        max_entropy = DiversityMaintenance._get_max_entropy(options)
        pdf = DiversityMaintenance._pdf(action_sequence, options)
        other_pdf = DiversityMaintenance._pdf(other_action_sequence, options)
        e1 = stats.entropy(pdf, other_pdf)
        e2 = stats.entropy(other_pdf, pdf)
        total = e1+e2
        result = total/max_entropy
        return result

    @staticmethod
    def _get_max_entropy(options):
        if 'max_entropy' not in Config.RESTRICTIONS['diversity']:
            pdf = DiversityMaintenance._pdf([0], options)
            other_pdf = DiversityMaintenance._pdf([2], options)
            e1 = stats.entropy(pdf, other_pdf)
            e2 = stats.entropy(other_pdf, pdf)
            total = e1+e2
            Config.RESTRICTIONS['diversity']['max_entropy'] = total
        return Config.RESTRICTIONS['diversity']['max_entropy']

    @staticmethod
    def _pdf(array, options):
        probs = [0.0] * options
        for value in array:
            probs[int(value)] += 1.0
        for index, value in enumerate(probs):
            probs[index] = value/float(len(array))
            if probs[index] == 0.0:
                probs[index] = 0.000000000001 # to avoid values being divided by 0
        total = sum(probs)
        for index, value in enumerate(probs):
            probs[index] = value/float(total)
        return probs