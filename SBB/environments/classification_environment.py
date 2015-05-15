import random
from collections import defaultdict, Counter
import numpy
from sklearn.metrics import confusion_matrix, accuracy_score, recall_score
from ..config import CONFIG, RESTRICTIONS

class ClassificationEnvironment:
    """
    This environment encapsulates all methods to deal with a classification task.
    """

    def __init__(self):
        self.train_, self.test_ = self._initialize_datasets()
        self.trainset_class_distribution_ = Counter(self._get_Y(self.train_))
        self.testset_class_distribution_ = Counter(self._get_Y(self.test_))
        self.total_actions_ = len(self.testset_class_distribution_)
        self.total_inputs_ = len(self.train_[0])-1
        self.trainset_per_action_ = self._get_data_per_action(self.train_)
        self.sample_ = None
        RESTRICTIONS['total_actions'] = self.total_actions_
        RESTRICTIONS['total_inputs'] = self.total_inputs_

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
            content = [[float(y) for y in x]for x in content] # gambiarra (a ultima coluna nao deveria ser convertida para float)
        return content

    def _get_normalization_params(self, train, test):
        """
        Get the mean and range for each column from the total dataset (train+test), excluding the labels column.
        """
        normalization_params = []
        data = numpy.array(train+test)
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

    def _get_data_per_action(self, data):
        subsets_per_class = []
        for class_index in range(self.total_actions_):
            values = [line for line in data if line[-1]-1 == class_index] # added -1 due to class labels starting at 1 instead of 0 # gambiarra
            subsets_per_class.append(values)
        return subsets_per_class

    def reset(self):
        self.sample_ = None

    def setup(self):
        self.sample_ = self._get_sample()

    def _get_sample(self):
        """
        Get a sample of the training dataset. If it is the first generation of the run, just
        gets random samples for each action of the dataset. For the next generations, it 
        replaces some of the points in the sample for new points.
        """
        total_samples_per_class = CONFIG['training_parameters']['populations']['points']/self.total_actions_

        if not self.sample_: # first sampling of the run
            # get random samples per class
            samples_per_class = []
            for subset in self.trainset_per_action_:
                samples_per_class.append(self._sample(subset, total_samples_per_class))
        else:
            current_subsets_per_class = self._get_data_per_action(self.sample_)
            total_samples_per_class_to_maintain = int(round(total_samples_per_class*(1.0-CONFIG['training_parameters']['replacement_rate']['points'])))
            total_samples_per_class_to_add = total_samples_per_class - total_samples_per_class_to_maintain

            # obtain the data points that will be maintained
            maintained_subsets_per_class = []
            for subset in current_subsets_per_class:
                maintained_subsets_per_class.append(random.sample(subset, total_samples_per_class_to_maintain))

            # add the new data points
            for i, subset in enumerate(maintained_subsets_per_class):
                subset += self._sample(self.trainset_per_action_[i], total_samples_per_class_to_add)
            samples_per_class = maintained_subsets_per_class

        # ensure that the sampling is balanced for all classes, using oversampling for the unbalanced ones
        if CONFIG['classification_parameters']['use_oversampling']:
            for sample in samples_per_class:
                while len(sample) < total_samples_per_class:
                    sample += self._sample(sample, total_samples_per_class-len(sample))

        # join samples per class
        sample = sum(samples_per_class, [])

        random.shuffle(sample)
        return sample

    def _sample(self, subset, sample_size):
        if len(subset) <= sample_size:
            sample = subset
        else:
            sample = random.sample(subset, sample_size)
        return sample

    def evaluate(self, team, training=False):
        """
        Evaluate the team using the environment inputs.
        """
        if training:
            dataset = self.sample_
        else:
            dataset = self.test_
        X = self._get_X(dataset)
        Y = self._get_Y(dataset)
        outputs = []
        for x in X:
            outputs.append(team.execute(x))
        score, extra_metrics = self._calculate_team_metrics(outputs, Y, training)
        if training:
            team.fitness = score
            team.score_trainingset = score
        else:
            team.score_testset = score
            team.extra_metrics = extra_metrics

    def _get_X(self, data):
        """
        Get the inputs
        """
        return [x[:-1] for x in data]

    def _get_Y(self, data):
        """
        Get the labels
        """
        Y = [x[-1:] for x in data]
        Y = sum(Y, [])
        Y = [int(y) for y in Y]
        if 0 not in Y:
            Y = [y-1 for y in Y]  # added -1 due to class labels starting at 1 # gambiarra
        return Y

    def _calculate_team_metrics(self, predicted_outputs, desired_outputs, training=False):
        extra_metrics = {}
        recall = recall_score(desired_outputs, predicted_outputs, average=None)
        macro_recall = numpy.mean(recall)
        if not training: # to avoid wasting time processing metrics when they are not necessary
            extra_metrics['recall_per_action'] = recall
            extra_metrics['accuracy'] = accuracy_score(desired_outputs, predicted_outputs)
            extra_metrics['confusion_matrix'] = confusion_matrix(desired_outputs, predicted_outputs)
        return macro_recall, extra_metrics

    def metrics(self):
        msg = ""
        msg += "\n### Dataset Info:"
        msg += "\nclass distribution (train set, "+str(len(self.train_))+" samples): "+str(self.trainset_class_distribution_)
        msg += "\nclass distribution (test set, "+str(len(self.test_))+" samples): "+str(self.testset_class_distribution_)
        msg += "\ntotal inputs: "+str(self.total_inputs_)
        msg += "\ntotal actions: "+str(self.total_actions_)
        msg += "\nactions mapping: "
        return msg