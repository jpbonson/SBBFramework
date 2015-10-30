import sys
import numpy
from collections import deque

class Config():
    """
    This class contain all the configurations and restrictions that will be used by SBB.
    You may change the attribute USER to run SBB with different configurations, but it 
    is not recommended to modify the attribute RESTRICTIONS.
    """

    # user configurable options
    USER = {
        'task': 'classification',
        'classification_parameters': { # only used if 'task' is 'classification'
            'dataset': 'thyroid', # must have a .train and a .test file in the pSBB/datasets folder
        },

        'training_parameters': {
            'runs_total': 1,
            'generations_total': 150,
            'validate_after_each_generation': 25,
            'populations': {
                'teams': 100,
                'points': 100,
            },
            'replacement_rate': {
                'teams': 0.5,
                'points': 0.2,
            },
            'mutation': {
                'team': {
                    'remove_program': 0.7,
                    'add_program': 0.7,
                    'mutate_program': 0.2, # is applied to all programs in the team, until at least one program is mutated
                },
                'program': {
                    'remove_instruction': 0.5,
                    'add_instruction': 0.5,
                    'change_instruction': 1.0,
                    'swap_instructions': 1.0,
                    'change_action': 0.1,
                },
            },
            'team_size': { # the min and initial size are the total number of actions
                'min': 2,
                'max': 9,
            },
            'program_size': {
                'min': 5,
                'max': 20,
            },
        },

        'advanced_training_parameters': {
            'seed': 1, # default = None, it can be a single seed for all runs, or an array of seeds per run
            'use_pareto_for_point_population_selection': False, # if False, will select points using uniform probability
            'use_operations': ['+', '-', '*', '/', 'ln', 'exp', 'cos', 'if_lesser_than', 'if_equal_or_higher_than', 'if_lesser_than_for_signal', 'if_equal_or_higher_than_for_signal'],
            'extra_registers': 3,
            'diversity': {
                'use_and_show': ['ncd_c3'], # will be applied to fitness and show in the outputs
                'only_show': ['genotype'], # will be only show in the outputs
                'k': 10,
                'total_bins': 5, # used to quantize the distances for the diversity metrics
            },
            'run_initialization_step2': False,
            'use_weighted_probability_selection': True, # if False, uniform probability will be used
            'use_agressive_mutations': True,
        },
    }

    # restrictions used to validate CONFIG and to control the system low-level configurations
    RESTRICTIONS = {
        'diversity_options': ['genotype', 'fitness_sharing'], # must have the same name as the methods in DiversityMaintenance
        'working_path': "SBB/",
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
            'training': 0,
            'validation': 1,
            'champion': 2,
        },
        'used_diversities': None, # initialized by sbb.py
        'multiply_normalization_by': 10.0,
        'profile': {
            'samples': deque(maxlen=int(USER['training_parameters']['populations']['points']*5.0)),
            'update_chance': 0.05,
        },
    }

    @staticmethod
    def check_parameters():
        """
        Check if the parameters in CONFIG are valid using RESTRICTIONS
        """

        diversities = Config.USER['advanced_training_parameters']['diversity']['use_and_show'] + Config.USER['advanced_training_parameters']['diversity']['only_show']
        
        for diversity in diversities:
            if diversity not in Config.RESTRICTIONS['diversity_options']:
                sys.stderr.write("Error: Invalid '"+diversity+"' diversity in CONFIG! The valid values are "+str(Config.RESTRICTIONS['diversity_options'])+"\n")
                raise SystemExit

        if Config.USER['task'] == 'classification':
            if 'ncd_c1' in diversities or 'entropy_c2' in diversities or 'hamming_c3' in diversities or 'ncd_c3' in diversities or 'entropy_c3' in diversities or 'ncd_c4' in diversities or 'euclidean' in diversities:
                sys.stderr.write("Error: Can't calculate this diversity for a classification task!\n")
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