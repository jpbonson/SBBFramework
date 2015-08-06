import random
from collections import Counter
import numpy
from sklearn.metrics import confusion_matrix, accuracy_score, recall_score
from default_environment import DefaultEnvironment, DefaultPoint, reset_points_ids
from ..pareto_dominance_for_points import ParetoDominanceForPoints
from ..utils.helpers import round_array, flatten
from ..config import Config

class ClassificationPoint(DefaultPoint):
    """
    Encapsulates a dataset value as a point.
    """

    def __init__(self, inputs, output):
        super(ClassificationPoint, self).__init__()
        self.inputs = inputs
        self.output = output

class ClassificationEnvironment(DefaultEnvironment):
    """
    This environment encapsulates all methods to deal with a classification task.
    """

    def __init__(self):
        reset_points_ids()
        self.point_population_ = None
        train, test = self._initialize_datasets()
        self.train_population_ = self._dataset_to_points(train)
        self.test_population_ = self._dataset_to_points(test)
        self.trainset_class_distribution_ = Counter([p.output for p in self.train_population_])
        self.testset_class_distribution_ = Counter([p.output for p in self.test_population_])
        self.total_actions_ = len(self.testset_class_distribution_)
        self.total_inputs_ = len(self.train_population_[0].inputs)
        self.trainset_per_action_ = self._get_data_per_action(self.train_population_)
        Config.RESTRICTIONS['total_actions'] = self.total_actions_
        Config.RESTRICTIONS['total_inputs'] = self.total_inputs_
        Config.RESTRICTIONS['use_memmory_for_actions'] = True # since for the same input, the output label is always the same
        # ensures that the point population will be balanced:
        total_samples_per_criteria = Config.USER['training_parameters']['populations']['points']/self.total_actions_
        Config.USER['training_parameters']['populations']['points'] = total_samples_per_criteria*self.total_actions_

    def _initialize_datasets(self):
        """
        Read from file and normalize the train and tests sets.
        """
        dataset_filename = Config.USER['classification_parameters']['dataset']
        print("\nReading inputs from data: "+dataset_filename)
        train = self._read_space_separated_file(Config.RESTRICTIONS['working_path']+"datasets/"+dataset_filename+".train")
        test = self._read_space_separated_file(Config.RESTRICTIONS['working_path']+"datasets/"+dataset_filename+".test")
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
            population.append(ClassificationPoint(numpy.array(item[:-1]), item[-1]))
        return population

    def _get_data_per_action(self, point_population):
        subsets_per_class = []
        for class_index in range(self.total_actions_):
            values = [point for point in point_population if point.output == class_index]
            subsets_per_class.append(values)
        return subsets_per_class

    def point_population(self):
        return self.point_population_

    def reset(self):
        self.point_population_ = None

    def setup(self, teams_population):
        """
        Get a sample of the training dataset to create the point population. If it is the first generation 
        of the run, just gets random samples for each action of the dataset. For the next generations, it 
        replaces some of the points in the sample for new points.
        """
        total_samples_per_class = Config.USER['training_parameters']['populations']['points']/self.total_actions_

        if not self.point_population_: # first sampling of the run
            # get random samples per class
            samples_per_class = []
            for subset in self.trainset_per_action_:
                samples_per_class.append(self._sample_subset(subset, total_samples_per_class))
        else: # uses attributes defined in evaluate_point_population()
            self._remove_points(flatten(self.samples_per_class_to_remove_), teams_population)
            samples_per_class = self.samples_per_class_to_keep_
        
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

    def _remove_points(self, points_to_remove, teams_population):
        """
        Remove the points to remove from the teams, in order to save memory.
        """
        for team in teams_population:
            for point in points_to_remove:
                if point.point_id_ in team.results_per_points_:
                    team.results_per_points_.pop(point.point_id_)
                if point.point_id_ in team.memory_actions_per_points_:
                    team.memory_actions_per_points_.pop(point.point_id_)

    def _check_for_bugs(self):
        if len(self.point_population_) != Config.USER['training_parameters']['populations']['points']:
            raise ValueError("The size of the points population changed during selection! You got a bug! (it is: "+str(len(self.point_population_))+", should be: "+str(Config.USER['training_parameters']['populations']['points'])+")")

    def evaluate_point_population(self, teams_population):
        current_subsets_per_class = self._get_data_per_action(self.point_population_)
        total_samples_per_class = Config.USER['training_parameters']['populations']['points']/self.total_actions_
        samples_per_class_to_keep = int(round(total_samples_per_class*(1.0-Config.USER['training_parameters']['replacement_rate']['points'])))

        kept_subsets_per_class = []
        removed_subsets_per_class = []
        if Config.USER['advanced_training_parameters']['use_pareto_for_point_population_selection']:
            # obtain the pareto front for each subset
            for subset in current_subsets_per_class:
                keep_solutions, remove_solutions = ParetoDominanceForPoints.run(subset, teams_population, samples_per_class_to_keep)
                kept_subsets_per_class.append(keep_solutions)
                removed_subsets_per_class.append(remove_solutions)

            # add new points
            for subset, trainset in zip(kept_subsets_per_class, self.trainset_per_action_):
                subset += self._sample_subset(trainset, total_samples_per_class - len(subset))
        else:
            # obtain the data points that will be kept and that will be removed for each subset using uniform probability
            total_samples_per_class_to_add = total_samples_per_class - samples_per_class_to_keep
            for i, subset in enumerate(current_subsets_per_class):
                kept_subsets = random.sample(subset, samples_per_class_to_keep) # get points that will be kept
                kept_subsets += self._sample_subset(self.trainset_per_action_[i], total_samples_per_class_to_add) # add new points
                kept_subsets_per_class.append(kept_subsets)
                removed_subsets_per_class.append(list(set(subset) - set(kept_subsets))) # find the remvoed points

        self.samples_per_class_to_keep_ = kept_subsets_per_class
        self.samples_per_class_to_remove_ = removed_subsets_per_class

    def evaluate_teams_population_for_training(self, teams_population):
        for team in teams_population:
            self.evaluate_team(team, Config.RESTRICTIONS['mode']['training'])

    def evaluate_team(self, team, mode):
        """
        Evaluate the team using the environment inputs.
        """
        if mode == Config.RESTRICTIONS['mode']['training']:
            population = self.point_population_
            is_training = True
        else:
            population = self.test_population_
            is_training = False

        outputs = []
        for point in population:
            output = team.execute(point.point_id_, point.inputs, range(Config.RESTRICTIONS['total_actions']), is_training)
            outputs.append(output)
            if is_training:
                if output == point.output:
                    result = 1 # correct
                else:
                    result = 0 # incorrect
                team.results_per_points_[point.point_id_] = result

        Y = [p.output for p in population]
        score, extra_metrics = self._calculate_team_metrics(outputs, Y, is_training)
        
        if is_training:
            team.fitness_ = score
        else:
            team.score_testset_ = score
            team.extra_metrics_ = extra_metrics

    def _calculate_team_metrics(self, predicted_outputs, desired_outputs, is_training = False):
        recall = recall_score(desired_outputs, predicted_outputs, average = None)
        macro_recall = numpy.mean(recall)
        extra_metrics = {}
        if not is_training: # to avoid wasting time processing metrics when they are not necessary
            extra_metrics['recall_per_action'] = round_array(recall)
            extra_metrics['accuracy'] = accuracy_score(desired_outputs, predicted_outputs)
            extra_metrics['confusion_matrix'] = confusion_matrix(desired_outputs, predicted_outputs)
        return macro_recall, extra_metrics

    def validate(self, current_generation, teams_population):
        fitness = [p.fitness_ for p in teams_population]
        best_team = teams_population[fitness.index(max(fitness))]
        self.evaluate_team(best_team, Config.RESTRICTIONS['mode']['validation'])
        return best_team

    def metrics(self):
        msg = ""
        msg += "\n### Dataset Info:"
        msg += "\ntotal inputs: "+str(self.total_inputs_)
        msg += "\ntotal actions: "+str(self.total_actions_)
        msg += "\nactions mapping: "+str(self.action_mapping_)
        msg += "\nclass distribution (train set, "+str(len(self.train_population_))+" samples): "+str(self.trainset_class_distribution_)
        msg += "\nclass distribution (test set, "+str(len(self.test_population_))+" samples): "+str(self.testset_class_distribution_)
        return msg