import sys
import re
import json
import numpy
from collections import deque

class Config():
    """
    This class contain all the configurations and restrictions that will be used by SBB.
    """

    # user configurable options, choose a .json file when initializing main.py
    USER = {}

    # restrictions used to validate CONFIG and to control the system low-level configurations
    RESTRICTIONS = {
        'task_types': ['classification', 'reinforcement'],
        'environment_types': ['tictactoe', 'poker', 'sockets'],
        'round_to_decimals': 5, # if you change this value, you must update the unit tests
        'max_seed': numpy.iinfo(numpy.int32).max + abs(numpy.iinfo(numpy.int32).min), # so it works for both Windows and Ubuntu
        'is_nearly_equal_threshold': 0.0001,
        'genotype_options': {
            'modes': ['read-register', 'read-input'],
            'simple_operations': ['+', '-', '*', '/'],
            'complex_operations': ['ln', 'exp', 'cos', 'sin', 'if_lesser_than', 
                'if_equal_or_higher_than', 'if_lesser_than_for_signal', 'if_equal_or_higher_than_for_signal'],
            'one-operand-instructions': ['ln', 'exp', 'cos', 'sin'],
            'if-instructions': ['if_lesser_than', 'if_equal_or_higher_than'],
            'if-instructions-for-signal': ['if_lesser_than_for_signal', 'if_equal_or_higher_than_for_signal'],
            'instruction_size': 4,
            'output_registers': 1,
            'total_registers': None, # initialized by sbb.py
        },
        'total_actions': -1, # initialized by the environment, can be meta or atomic actions
        'total_raw_actions': -1, # initialized by the environment, are the atomic actions performed in the environment
        'total_inputs': -1, # initialized by the environment
        'action_mapping': {}, # initialized by the environment
        'use_memmory_for_actions': False, # initialized by the environment
        'write_output_files': True, # used by the test cases
        'mode': {
            'training': 'training',
            'validation': 'validation',
            'champion': 'champion',
        },
        'used_diversities': None, # initialized by sbb.py
        'multiply_normalization_by': 10.0,
        'novelty_archive':{
            'samples': -1, # set after config is loaded
            'threshold': 10,
        },
        'diversity': {
            'options': ['genotype', 'fitness_sharing', 'entropy', 'ncd', 'ncd_custom', 
            'hamming', 'euclidean'], # must have the same name as the methods in DiversityMaintenance
            'classification_compatible_diversities': ['genotype', 'fitness_sharing'],
            'reinforcement_compatible_diversities': ['genotype', 'fitness_sharing', 'entropy', 'ncd', 
                'ncd_custom', 'hamming', 'euclidean'],
            'total_bins': 3, # used to organize the distances for the action-based diversity metrics
            'max_ncd': 1.2, # used to normalize NCD
        },
        'second_layer': {
            'action_mapping': {}, # initialized by sbb.py
            'short_action_mapping': {}, # initialized by sbb.py
        },
        'output_folder': 'outputs/',
    }

    @staticmethod
    def load_config(json_file):
        """
        Load user configurations from a .json file
        """
        # removing comments
        content = ""
        with open(json_file, 'r') as fp:
            for line in fp:
                new_line = re.sub(r'(#+.*)', r'', line)
                content += new_line

        # initializing config
        Config.USER = json.loads(content)
        sample_size = deque(maxlen=int(Config.USER['training_parameters']['populations']['teams']*1.0))
        Config.RESTRICTIONS['novelty_archive']['samples'] = sample_size

    @staticmethod
    def check_parameters():
        """
        Check if the parameters in CONFIG are valid
        """
        Config.check_parameters_for_overall()

        if Config.USER['task'] == 'classification':
            Config.check_parameters_for_classification()

        if Config.USER['task'] == 'reinforcement':
            Config.check_parameters_for_reinforcement()

    @staticmethod
    def check_parameters_for_overall():
        if Config.USER['task'] not in Config.RESTRICTIONS['task_types']:
            sys.stderr.write("Error: Invalid 'task' in CONFIG! "
                "The valid values are "+str(Config.RESTRICTIONS['task_types'])+"\n")
            raise SystemExit

        diversities = Config.USER['advanced_training_parameters']['diversity']['metrics']
        for diversity in diversities:
            if diversity not in Config.RESTRICTIONS['diversity']['options']:
                sys.stderr.write("Error: Invalid '"+diversity+"' diversity in CONFIG! "
                    "The valid values are "+str(Config.RESTRICTIONS['diversity']['options'])+"\n")
                raise SystemExit

        if (Config.USER['advanced_training_parameters']['novelty']['enabled'] 
                and len(Config.USER['advanced_training_parameters']['diversity']['metrics']) == 0):
            sys.stderr.write("Error: Novelty can only be used along with a diversity metric\n")
            raise SystemExit

        valid_operations = (Config.RESTRICTIONS['genotype_options']['simple_operations'] 
            + Config.RESTRICTIONS['genotype_options']['complex_operations'])
        for op in Config.USER['advanced_training_parameters']['use_operations']:  
            if op not in valid_operations:
                sys.stderr.write("Error: Invalid 'use_operations' in CONFIG! "
                    "The valid values are "+str(valid_operations)+"\n")
                raise SystemExit

        if (Config.USER['training_parameters']['generations_total'] 
                % Config.USER['training_parameters']['validate_after_each_generation'] != 0):
            sys.stderr.write("Error: 'validate_after_each_generation' should be a multiple for "
                    "'generations_total', in order to ensure validation of the last generation.\n")
            raise SystemExit

        if isinstance(Config.USER['advanced_training_parameters']['seed'], list):
            if (len(Config.USER['advanced_training_parameters']['seed']) 
                    != Config.USER['training_parameters']['runs_total']):
                sys.stderr.write("Error: If you are using an array of seeds, "
                    "the size of the array must be equal to the total of runs.\n")
                raise SystemExit

    @staticmethod
    def check_parameters_for_classification():
        diversities = Config.USER['advanced_training_parameters']['diversity']['metrics']
        for diversity in diversities:
            if diversity not in Config.RESTRICTIONS['diversity']['classification_compatible_diversities']:
                sys.stderr.write("Error: Can't calculate this diversity for a classification task!\n")
                raise SystemExit

    @staticmethod
    def check_parameters_for_reinforcement():
        diversities = Config.USER['advanced_training_parameters']['diversity']['metrics']
        for diversity in diversities:
            if diversity not in Config.RESTRICTIONS['diversity']['reinforcement_compatible_diversities']:
                sys.stderr.write("Error: Can't calculate this diversity for a reinforcement task!\n")
                raise SystemExit

        if 'hamming' in diversities or 'euclidean' in diversities:
            if not Config.USER['reinforcement_parameters']['environment_parameters']['weights_per_action']:
                sys.stderr.write("Error: Can't calculate 'hamming' and 'euclidean' diversities "
                    " if there are no 'weights_per_action'!\n")
                raise SystemExit
            if (Config.USER['reinforcement_parameters']['environment_parameters']['actions_total'] 
                    != len(Config.USER['reinforcement_parameters']['environment_parameters']['weights_per_action'])):
                sys.stderr.write("Error: Can't calculate 'hamming' and 'euclidean' diversities "
                    " if there 'weights_per_action' is not the same size as 'actions_total'!\n")
                raise SystemExit

        if Config.USER['reinforcement_parameters']['hall_of_fame']['diversity']:
            if (Config.USER['reinforcement_parameters']['hall_of_fame']['diversity'] 
                    not in Config.RESTRICTIONS['diversity']['options']):
                sys.stderr.write("Error: Invalid 'diversity' for 'hall_of_fame' in CONFIG! "
                    "The valid values are "+str(Config.RESTRICTIONS['diversity']['options'])+"\n")
                raise SystemExit

        if (not Config.USER['reinforcement_parameters']['hall_of_fame']['enabled'] 
                and Config.USER['reinforcement_parameters']['hall_of_fame']['opponents'] != 0):
            sys.stderr.write("Error: For hall of fame, 'opponents' can't be higher than 0 "
                "if 'enabled' is False\n")
            raise SystemExit

        if (Config.USER['reinforcement_parameters']['hall_of_fame']['enabled'] 
                and Config.USER['reinforcement_parameters']['hall_of_fame']['opponents'] < 0):
            sys.stderr.write("Error: For hall of fame, 'opponents' can't be lower than 0\n")
            raise SystemExit

        if (Config.USER['reinforcement_parameters']['environment'] 
                not in Config.RESTRICTIONS['environment_types']):
            sys.stderr.write("Error: Invalid 'environment' in CONFIG! "
                "The valid values are "+str(Config.RESTRICTIONS['environment_types'])+"\n")
            raise SystemExit

        total_labels = Config.USER['reinforcement_parameters']['environment_parameters']['point_labels_total']
        if total_labels < 1:
            sys.stderr.write("Error: Invalid 'point_labels_total' in CONFIG! "
                "The minimum number of labels must always be at least 1.\n")
            raise SystemExit

        total_opponents = len(Config.USER['reinforcement_parameters']['environment_parameters']['training_opponents_labels'])
        minimum_pop_size = total_labels*total_opponents
        if Config.USER['training_parameters']['populations']['points'] < minimum_pop_size:
            sys.stderr.write("Error: Point population for training is too small, "
                "minimum size: "+str(minimum_pop_size)+"\n")
            raise SystemExit

        total_opponents = len(Config.USER['reinforcement_parameters']['environment_parameters']['validation_opponents_labels'])
        minimum_pop_size = total_labels*total_opponents
        if Config.USER['reinforcement_parameters']['validation_population'] < minimum_pop_size:
            sys.stderr.write("Error: Point population for validation is too small, "
                "minimum size: "+str(minimum_pop_size)+"\n")
            raise SystemExit

        if Config.USER['reinforcement_parameters']['champion_population'] < minimum_pop_size:
            sys.stderr.write("Error: Point population for champion is too small, "
                "minimum size: "+str(minimum_pop_size)+"\n")
            raise SystemExit