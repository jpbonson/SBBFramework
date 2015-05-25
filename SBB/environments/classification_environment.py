import random
from collections import Counter
import numpy
from sklearn.metrics import confusion_matrix, accuracy_score, recall_score
from default_environment import DefaultEnvironment, DefaultPoint
from ..diversity_maintenance import DiversityMaintenance
from ..pareto_dominance import ParetoDominance
from ..utils.helpers import round_array_to_decimals, flatten, is_nearly_equal_to
from ..config import CONFIG, RESTRICTIONS

class ClassificationPoint(DefaultPoint):
    """
    Encapsulates a dataset value as a point.
    """

    def __init__(self, point_id, inputs, output):
        super(ClassificationPoint, self).__init__(point_id, inputs)
        self.output = output

    def __repr__(self): 
        return "("+str(self.point_id)+")"

    def __str__(self): 
        return "("+str(self.point_id)+")"

class ClassificationEnvironment(DefaultEnvironment):
    """
    This environment encapsulates all methods to deal with a classification task.
    """

    def __init__(self):
        train, test = self._initialize_datasets()
        self.train_population_ = self._dataset_to_points(train)
        self.test_population_ = self._dataset_to_points(test)
        self.trainset_class_distribution_ = Counter([p.output for p in self.train_population_])
        self.testset_class_distribution_ = Counter([p.output for p in self.test_population_])
        self.total_actions_ = len(self.testset_class_distribution_)
        self.total_inputs_ = len(self.train_population_[0].inputs)
        self.trainset_per_action_ = self._get_data_per_action(self.train_population_)
        self.point_population_ = None
        RESTRICTIONS['total_actions'] = self.total_actions_
        RESTRICTIONS['total_inputs'] = self.total_inputs_
        RESTRICTIONS['action_mapping'] = self.action_mapping_

        # ensures the population size is multiple of the total actions
        total_samples_per_class = CONFIG['training_parameters']['populations']['points']/self.total_actions_
        CONFIG['training_parameters']['populations']['points'] = total_samples_per_class*self.total_actions_

    def _initialize_datasets(self):
        """
        Read from file and normalize the train and tests sets.
        """
        dataset_filename = CONFIG['classification_parameters']['dataset']
        print("\nReading inputs from data: "+dataset_filename)
        train = self._read_space_separated_file(RESTRICTIONS['working_path']+"datasets/"+dataset_filename+".train")
        test = self._read_space_separated_file(RESTRICTIONS['working_path']+"datasets/"+dataset_filename+".test")
        normalization_params = self._get_normalization_params(train, test)
        train = self._normalize(normalization_params, train)
        test = self._normalize(normalization_params, test)
        return train, test

    def _read_space_separated_file(self, file_path):
        """
        Read files separated by space (example: 0.015 0.12 0.082 0.146 3)
        """
        with open(file_path) as f:
            content = f.readlines()
            content = [x.strip('\n').strip() for x in content]
            content = [x.split(' ') for x in content]
            X = [x[:-1] for x in content]
            Y = [x[-1:] for x in content]
            self.action_mapping_ = self._create_action_mapping(Y)
            Y = self._apply_action_mapping(Y)
            content = numpy.append(X, Y, axis = 1)
            content = [[float(y) for y in x]for x in content]
        return content

    def _create_action_mapping(self, Y):
        action_mapping_ = {}
        labels = sorted(set(flatten(Y)))
        for i, label in enumerate(labels):
            action_mapping_[label] = i
        return action_mapping_

    def _apply_action_mapping(self, Y):
        return [[self.action_mapping_[y] for y in x]for x in Y]

    def _get_normalization_params(self, train, test):
        """
        Get the mean and range for each column from the total dataset (train+test), excluding the labels column.
        """
        normalization_params = []
        data = numpy.append(train, test, axis = 0)
        attributes_len = len(data[0])
        for index in range(attributes_len-1): # dont get normalization parameters for the labels column
            column = data[:,index]
            normalization_params.append({'mean':numpy.mean(column), 'range':max(column)-min(column)})
        return normalization_params

    def _normalize(self, normalization_params, data):
        """
        Normalize all columns, except the labels, using the normalization parameters.
        """
        normalized_data = []
        for line in data:
            new_line = []
            for i, cell in enumerate(line):
                if not i == len(line)-1:  # dont normalize the labels column
                    if normalization_params[i]['range'] == 0.0:
                        cell = 0.0
                    else:
                        cell = (cell-normalization_params[i]['mean'])/normalization_params[i]['range']
                new_line.append(cell)
            normalized_data.append(new_line)
        return normalized_data

    def _dataset_to_points(self, data):
        """
        Use dataset to create point population.
        """
        population = []
        for index, item in enumerate(data):
            population.append(ClassificationPoint(index, numpy.array(item[:-1]), item[-1]))
        return population

    def _get_data_per_action(self, point_population):
        subsets_per_class = []
        for class_index in range(self.total_actions_):
            values = [point for point in point_population if point.output == class_index]
            subsets_per_class.append(values)
        return subsets_per_class

    def reset_point_population(self):
        self.point_population_ = None

    def setup_point_population(self, teams_population):
        """
        Get a sample of the training dataset to create the point population. If it is the first generation 
        of the run, just gets random samples for each action of the dataset. For the next generations, it 
        replaces some of the points in the sample for new points.
        """
        total_samples_per_class = CONFIG['training_parameters']['populations']['points']/self.total_actions_

        if not self.point_population_: # first sampling of the run
            # get random samples per class
            samples_per_class = []
            for subset in self.trainset_per_action_:
                samples_per_class.append(self._sample_subset(subset, total_samples_per_class))
        else: # uses attributes defined in evaluate_point_population()
            samples_per_class = self.samples_per_class_to_keep

            # remove the removed points from the teams, in order to save memory. If you want to speed up and
            # don't care about the memory, you may comment the next 5 lines
            to_remove = flatten(self.samples_per_class_to_remove)
            for team in teams_population:
                for point in to_remove:
                    if point.point_id in team.results_per_points_:
                        team.results_per_points_.pop(point.point_id)

        # ensure that the sampling is balanced for all classes, using oversampling for the ones with less than the minimum samples
        for sample in samples_per_class:
            while len(sample) < total_samples_per_class:
                sample += self._sample_subset(sample, total_samples_per_class-len(sample))

        sample = flatten(samples_per_class) # join samples per class
        random.shuffle(sample)
        self.point_population_ = sample
        self._check_for_bugs()

    def _sample_subset(self, subset, sample_size):
        if len(subset) <= sample_size:
            sample = subset
        else:
            sample = random.sample(subset, sample_size)
        return sample

    def _check_for_bugs(self):
        if len(self.point_population_) != CONFIG['training_parameters']['populations']['points']:
            raise ValueError("The size of the points population changed during selection! You got a bug! (it is: "+str(len(self.point_population_))+", should be: "+str(CONFIG['training_parameters']['populations']['points'])+")")

    def evaluate_point_population(self, teams_population):
        total_samples_per_class = CONFIG['training_parameters']['populations']['points']/self.total_actions_
        current_subsets_per_class = self._get_data_per_action(self.point_population_)
        samples_per_class_to_keep = int(round(total_samples_per_class*(1.0-CONFIG['training_parameters']['replacement_rate']['points'])))

        kept_subsets_per_class = []
        removed_subsets_per_class = []
        if CONFIG['advanced_training_parameters']['use_pareto_for_point_population_selection']:
            # obtain the pareto front for each subset
            for subset in current_subsets_per_class:
                # create the results_map, so that the pareto front will contain points that are selecting distinct teams
                results_map = self._generate_results_map_for_pareto(subset, teams_population)
                front, dominateds = ParetoDominance.pareto_front(subset, results_map)

                keep_solutions = front
                remove_solutions = dominateds
                if len(keep_solutions) < samples_per_class_to_keep:  # must include some teams from dominateds
                    subset = DiversityMaintenance.fitness_sharing_for_points(subset, results_map)
                    keep_solutions, remove_solutions = ParetoDominance.balance_pareto_front_to_up(subset, keep_solutions, remove_solutions, samples_per_class_to_keep)
                if len(keep_solutions) > samples_per_class_to_keep: # must discard some teams from front
                    front = DiversityMaintenance.fitness_sharing_for_points(front, results_map)
                    keep_solutions, remove_solutions = ParetoDominance.balance_pareto_front_to_down(front, keep_solutions, remove_solutions, samples_per_class_to_keep)
                kept_subsets_per_class.append(keep_solutions)
                removed_subsets_per_class.append(remove_solutions)
        else:
            # obtain the data points that will be kept and that will be removed for each subset using uniform probability
            total_samples_per_class_to_add = total_samples_per_class - samples_per_class_to_keep
            for i, subset in enumerate(current_subsets_per_class):
                kept_subsets = random.sample(subset, samples_per_class_to_keep) # get points that will be kept
                kept_subsets += self._sample_subset(self.trainset_per_action_[i], total_samples_per_class_to_add) # add new points
                kept_subsets_per_class.append(kept_subsets)
                removed_subsets_per_class.append(list(set(subset) - set(kept_subsets))) # find the remvoed points

        self.samples_per_class_to_keep = kept_subsets_per_class
        self.samples_per_class_to_remove = removed_subsets_per_class

    def _generate_results_map_for_pareto(self, subset, teams_population):
        """
        Create a a matrix of (points) x (array version of a matrix that compares all teams outcomes against 
        each other for this point  (0: <=, 1: >)). This matrix is used by pareto to find a front of points 
        that characterize distinct teams.
        """
        results_map = []
        try:
            for point in subset:      
                distinction_vector = []
                for team1 in teams_population:
                    outcome1 = team1.results_per_points_[point.point_id]
                    for team2 in teams_population:
                        outcome2 = team2.results_per_points_[point.point_id]                 
                        if outcome1 > outcome2 and not is_nearly_equal_to(outcome1, outcome2):
                            distinction_vector.append(1)
                        else:
                            distinction_vector.append(0)
                results_map.append(distinction_vector)
        except KeyError as e:
            raise KeyError("A team hasn't processed the point "+str(e)+" before! You got a bug!")
        return results_map
                        
    def point_population(self):
        return self.point_population_

    def evaluate_team(self, team, is_training=False):
        """
        Evaluate the team using the environment inputs.
        """
        if is_training:
            population = self.point_population_
        else:
            population = self.test_population_

        outputs = []
        for point in population:
            output = team.execute(point, is_training)
            outputs.append(output)
            if is_training:
                if output == point.output:
                    result = 1 # correct
                else:
                    result = 0 # incorrect
                team.results_per_points_[point.point_id] = result

        Y = [p.output for p in population]
        score, extra_metrics = self._calculate_team_metrics(outputs, Y, is_training)
        
        if is_training:
            team.fitness_ = score
            team.score_trainingset_ = score
        else:
            team.score_testset_ = score
            team.extra_metrics_ = extra_metrics

    def _calculate_team_metrics(self, predicted_outputs, desired_outputs, is_training=False):
        extra_metrics = {}
        recall = recall_score(desired_outputs, predicted_outputs, average=None)
        macro_recall = numpy.mean(recall)
        if not is_training: # to avoid wasting time processing metrics when they are not necessary
            extra_metrics['recall_per_action'] = round_array_to_decimals(recall)
            extra_metrics['accuracy'] = accuracy_score(desired_outputs, predicted_outputs)
            extra_metrics['confusion_matrix'] = confusion_matrix(desired_outputs, predicted_outputs)
        return macro_recall, extra_metrics

    def metrics(self):
        msg = ""
        msg += "\n### Dataset Info:"
        msg += "\nclass distribution (train set, "+str(len(self.train_population_))+" samples): "+str(self.trainset_class_distribution_)
        msg += "\nclass distribution (test set, "+str(len(self.test_population_))+" samples): "+str(self.testset_class_distribution_)
        msg += "\ntotal inputs: "+str(self.total_inputs_)
        msg += "\ntotal actions: "+str(self.total_actions_)
        msg += "\nactions mapping: "+str(self.action_mapping_)
        return msg