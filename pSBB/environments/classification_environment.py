from collections import defaultdict
import random
import numpy
from sklearn.metrics import confusion_matrix, accuracy_score, recall_score
from ..config import CONFIG, RESTRICTIONS

class ClassificationEnvironment:
    """

    """

    def __init__(self):
        self.train, self.test = self.__initialize_datasets()
        self.test_Y = self.__get_Y(self.test)
        self.testset_class_distribution = self.__get_class_distribution(self.test_Y)
        self.total_actions = len(self.testset_class_distribution)
        self.total_inputs = len(self.train[0])-1
        self.trainsubsets_per_class = self.__get_data_per_class(self.train)

    def __initialize_datasets(self):
        print("\nReading inputs from data: "+CONFIG['classification_parameters']['dataset'])
        train, test = self.__read_inputs_already_partitioned(CONFIG['classification_parameters']['dataset'])
        normalization_params = self.__get_normalization_params(train, test)
        train = self.__normalize(normalization_params, train)
        test = self.__normalize(normalization_params, test)
        return train, test

    def __read_inputs_already_partitioned(self, data_name):
        train = self.__read_space_separated_file(RESTRICTIONS['working_path']+"datasets/"+data_name+".train")
        test = self.__read_space_separated_file(RESTRICTIONS['working_path']+"datasets/"+data_name+".test")
        return train, test

    def __read_space_separated_file(self, file_path):
        with open(file_path) as f:
            content = f.readlines()
            content = [x.strip('\n').strip() for x in content]
            content = [x.split(' ') for x in content]
            content = [[float(y) for y in x]for x in content]
        return content

    def __get_normalization_params(self, train, test):
        normalization_params = []
        data = numpy.array(train+test)
        attributes_len = len(data[0])
        for index in range(attributes_len-1): # dont get the class' labels column
            column = data[:,index]
            normalization_params.append({'mean':numpy.mean(column), 'range':max(column)-min(column)})
        normalization_params.append({'mean': 0.0, 'range': 1.0}) # default values so the class labels will not change
        return normalization_params

    def __normalize(self, normalization_params, data):
        normalized_data = []
        for line in data:
            new_line = []
            for i, cell in enumerate(line):
                if normalization_params[i]['range'] == 0.0:
                    cell = 0.0
                else:
                    cell = (cell-normalization_params[i]['mean'])/normalization_params[i]['range']
                new_line.append(cell)
            normalized_data.append(new_line)
        return normalized_data

    def __get_class_distribution(self, labels):
        cont = defaultdict(int)
        for label in labels:
            cont[label] += 1
        return cont

    def __get_data_per_class(self, data):
        subsets_per_class = []
        for class_index in range(self.total_actions):
            values = [line for line in data if line[-1]-1 == class_index] # added -1 due to class labels starting at 1 instead of 0
            subsets_per_class.append(values)
        return subsets_per_class

    def get_sample(self, previous_samples=None):
        print("Sampling")
        num_samples_per_class = CONFIG['training_parameters']['populations']['points']/len(self.trainsubsets_per_class)

        if not previous_samples or CONFIG['training_parameters']['replacement_rate']['points'] == 1.0: # first sampling
            # get samples per class
            samples_per_class = []
            for subset in self.trainsubsets_per_class:
                if len(subset) <= num_samples_per_class:
                    sample = subset
                else:
                    sample = random.sample(subset, num_samples_per_class)
                samples_per_class.append(sample)
        else:
            current_subsets_per_class = self.__get_data_per_class(previous_samples)
            num_samples_per_class_to_maintain = int(round(num_samples_per_class*(1.0-CONFIG['training_parameters']['replacement_rate']['points'])))
            num_samples_per_class_to_add = num_samples_per_class - num_samples_per_class_to_maintain

            # obtain the data points that will be maintained
            maintained_subsets_per_class = []
            for subset in current_subsets_per_class:
                maintained_subsets_per_class.append(random.sample(subset, num_samples_per_class_to_maintain))

            # add the new data points
            for i, subset in enumerate(maintained_subsets_per_class):
                if len(self.trainsubsets_per_class[i]) <= num_samples_per_class_to_add:
                    subset += self.trainsubsets_per_class[i]
                else:
                    subset += random.sample(self.trainsubsets_per_class[i], num_samples_per_class_to_add)
            samples_per_class = maintained_subsets_per_class

        # ensure that the sampling is balanced for all classes, using oversampling for the unbalanced ones
        if CONFIG['classification_parameters']['use_oversampling']:
            for sample in samples_per_class:
                while len(sample) < num_samples_per_class:
                    to_sample = num_samples_per_class-len(sample)
                    if to_sample > len(sample):
                        to_sample = len(sample)
                    sample += random.sample(sample, to_sample)

        # join samples per class
        sample = sum(samples_per_class, [])

        random.shuffle(sample)
        return sample

    def evaluate(self, team, dataset, testset=False):
        outputs = []
        X = self.__get_X(dataset)
        Y = self.__get_Y(dataset)
        for x in X:
            outputs.append(team.execute(x))
        return self.__calculate_metrics(outputs, Y, testset)

    def __get_X(self, data):
        return [x[:-1] for x in data]

    def __get_Y(self, data):
        """
        Get the class labels
        """
        Y = [x[-1:] for x in data]
        Y = sum(Y, [])
        Y = [int(y) for y in Y]
        if 0 not in Y:
            Y = [y-1 for y in Y]  # added -1 due to class labels starting at 1
        return Y

    def __calculate_metrics(self, predicted_outputs, desired_outputs, testset=False):
        extra_metrics = {}
        recall = recall_score(desired_outputs, predicted_outputs, average=None)
        macro_recall = numpy.mean(recall)
        if testset: # to avoid wasting time processing metrics when they are not necessary
            extra_metrics['accuracy'] = accuracy_score(desired_outputs, predicted_outputs)
            extra_metrics['recall'] = recall
            extra_metrics['conf_matrix'] = confusion_matrix(desired_outputs, predicted_outputs)
            conts_per_class = [0] * self.total_actions
            for p, d in zip(predicted_outputs, desired_outputs):
                if p == d:
                    conts_per_class[d] += 1.0
            extra_metrics['accuracies_per_class'] = [x/float(len(predicted_outputs)) for x in conts_per_class]
        return macro_recall, extra_metrics

    def print_metrics(self, msg):
        msg += "\nDataset info:"   
        msg += "\nClass Distributions (test dataset): "+str(self.testset_class_distribution)+", for a total of "+str(len(self.test_Y))+" samples"
        msg += ("\ntotal samples (train): "+str(len(self.train)))
        msg += ("\ntotal samples (test): "+str(len(self.test)))
        msg += ("\ntotal_inputs: "+str(self.total_inputs))
        msg += ("\ntotal_classes: "+str(self.total_actions))
        print msg
        return msg