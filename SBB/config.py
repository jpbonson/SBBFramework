import sys
import re
import json
import numpy
from collections import deque

class Config():
    """
    This class contain all the configurations and restrictions that will be used by SBB.
    You may change the attribute USER to run SBB with different configurations, but it 
    is not recommended to modify the attribute RESTRICTIONS.
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
            'complex_operations': ['ln', 'exp', 'cos', 'sin', 'if_lesser_than', 'if_equal_or_higher_than', 'if_lesser_than_for_signal', 'if_equal_or_higher_than_for_signal'],
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
            'options': ['genotype', 'fitness_sharing', 'entropy_c2', 'hamming_c3', 'ncd_c3', 'entropy_c3', 'ncd_c4', 'euclidean'], # must have the same name as the methods in DiversityMaintenance
            'total_bins': 3, # used to organize the distances for the diversity metrics
            'max_ncd': 1.2,
        },
        'second_layer': {
            'action_mapping': {}, # initialized by sbb.py
            'short_action_mapping': {}, # initialized by sbb.py
        },
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
        Config.RESTRICTIONS['novelty_archive']['samples'] = deque(maxlen=int(Config.USER['training_parameters']['populations']['teams']*1.0))

    @staticmethod
    def check_parameters():
        """
        Check if the parameters in CONFIG are valid using RESTRICTIONS
        """
        if Config.USER['task'] not in Config.RESTRICTIONS['task_types']:
            sys.stderr.write("Error: Invalid 'task' in CONFIG! The valid values are "+str(Config.RESTRICTIONS['task_types'])+"\n")
            raise SystemExit

        diversities = Config.USER['advanced_training_parameters']['diversity']['use_and_show'] + Config.USER['advanced_training_parameters']['diversity']['only_show']
        
        for diversity in diversities:
            if diversity not in Config.RESTRICTIONS['diversity']['options']:
                sys.stderr.write("Error: Invalid '"+diversity+"' diversity in CONFIG! The valid values are "+str(Config.RESTRICTIONS['diversity']['options'])+"\n")
                raise SystemExit

        if Config.USER['task'] == 'classification':
            if 'ncd_c1' in diversities or 'entropy_c2' in diversities or 'hamming_c3' in diversities or 'ncd_c3' in diversities or 'entropy_c3' in diversities or 'ncd_c4' in diversities or 'euclidean' in diversities:
                sys.stderr.write("Error: Can't calculate this diversity for a classification task!\n")
                raise SystemExit

        if Config.USER['task'] == 'reinforcement':
            if Config.USER['reinforcement_parameters']['hall_of_fame']['diversity']:
                if Config.USER['reinforcement_parameters']['hall_of_fame']['diversity'] not in Config.RESTRICTIONS['diversity']['options']:
                    sys.stderr.write("Error: Invalid 'diversity' for 'hall_of_fame' in CONFIG! The valid values are "+str(Config.RESTRICTIONS['diversity']['options'])+"\n")
                    raise SystemExit
            if not Config.USER['reinforcement_parameters']['hall_of_fame']['enabled'] and Config.USER['reinforcement_parameters']['hall_of_fame']['opponents'] != 0:
                sys.stderr.write("Error: For hall of fame, 'opponents' can't be higher than 0 if 'enabled' is False\n")
                raise SystemExit
            if Config.USER['reinforcement_parameters']['hall_of_fame']['enabled'] and Config.USER['reinforcement_parameters']['hall_of_fame']['opponents'] < 0:
                sys.stderr.write("Error: For hall of fame, 'opponents' can't be lower than 0\n")
                raise SystemExit
            if Config.USER['reinforcement_parameters']['environment'] not in Config.RESTRICTIONS['environment_types']:
                sys.stderr.write("Error: Invalid 'environment' in CONFIG! The valid values are "+str(Config.RESTRICTIONS['environment_types'])+"\n")
                raise SystemExit

        if Config.USER['advanced_training_parameters']['novelty']['enabled'] and len(Config.USER['advanced_training_parameters']['diversity']['use_and_show']) == 0:
            sys.stderr.write("Error: Novelty can only be used along with a diversity metric\n")
            raise SystemExit

        valid_operations = Config.RESTRICTIONS['genotype_options']['simple_operations'] + Config.RESTRICTIONS['genotype_options']['complex_operations']
        for op in Config.USER['advanced_training_parameters']['use_operations']:  
            if op not in valid_operations:
                sys.stderr.write("Error: Invalid 'use_operations' in CONFIG! The valid values are "+str(valid_operations)+"\n")
                raise SystemExit

        if Config.USER['training_parameters']['generations_total'] % Config.USER['training_parameters']['validate_after_each_generation'] != 0:
            sys.stderr.write("Error: 'validate_after_each_generation' should be a multiple for 'generations_total', in order to ensure validation of the last generation.\n")
            raise SystemExit

        if isinstance(Config.USER['advanced_training_parameters']['seed'], list):
            if len(Config.USER['advanced_training_parameters']['seed']) != Config.USER['training_parameters']['runs_total']:
                sys.stderr.write("Error: If you are using an array of seeds, the size of the array must be equal to the total of runs.\n")
                raise SystemExit