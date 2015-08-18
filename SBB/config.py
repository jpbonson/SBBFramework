import sys
import numpy
from examples import thyroid_config, tictactoe_config, poker_config

class Config():
    """
    This class contain all the configurations and restrictions that will be used by SBB.
    You may change the attribute USER to run SBB with different configurations, but it 
    is not recommended to modify the attribute RESTRICTIONS.
    """

    # user configurable options
    USER = {
        'task': 'reinforcement',
        'classification_parameters': { # only used if 'task' is 'classification'
            'dataset': 'thyroid', # must have a .train and a .test file in the pSBB/datasets folder
        },
        'reinforcement_parameters': { # only used if 'task' is 'reinforcement'
            'environment': 'poker', # edit _initialize_environment() in SBB and RESTRICTIONS['environment_types'] to add new environments (they must implement DefaultEnvironment)
            'validation_population': 25, # at a validated generation, all the teams with be tested against this population, the best one is the champion
            'champion_population': 50, # at a validated generation, these are the points the champion team will play against to obtain the metrics
            'hall_of_fame': {
                'size': 5,
                'enabled': True,
                'diversity': 'normalized_compression_distance', # if None, use the fitness as the criteria to remove teams when the Hall of Fame is full
            },
            'debug_matches': False, # use this option to debug
            'poker': {
                'balance_based_on': 'hole_cards_strength', # hole_cards_strength or board_strength # TODO: refactor
            },            
        },

        'training_parameters': {
            'runs_total': 1,
            'generations_total': 25,
            'validate_after_each_generation': 25,
            'populations': {
                'teams': 20,
                'points': 20,
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
                'min': 2,
                'max': 10,
            },
        },

        'advanced_training_parameters': {
            'seed': 1, # default = None, it can be a single seed for all runs, or an array of seeds per run
            'use_pareto_for_point_population_selection': False, # if False, will select points using uniform probability
            'use_operations': ['+', '-', '*', '/', 'ln', 'exp', 'cos', 'if_lesser_than', 'if_equal_or_higher_than'],
            'extra_registers': 1,
            'diversity': {
                'use_and_show': ['normalized_compression_distance', 'genotype_distance'], # will be applied to fitness and show in the outputs
                'only_show': [], # will be only show in the outputs
                'k': 8,
            },
            'run_initialization_step2': False,
        },
    }

    # restrictions used to validate CONFIG and to control the system low-level configurations
    RESTRICTIONS = {
        'task_types': ['classification', 'reinforcement'],
        'environment_types': ['tictactoe', 'poker'],
        'diversity_options': ['genotype_distance', 'fitness_sharing', 'normalized_compression_distance', 'relative_entropy_distance'], #must have the same name as the methods in DiversityMaintenance
        'working_path': "SBB/",
        'round_to_decimals': 5, # if you change this value, you must update the unit tests
        'max_seed': numpy.iinfo(numpy.int32).max + abs(numpy.iinfo(numpy.int32).min), # so it works for both Windows and Ubuntu
        'is_nearly_equal_threshold': 0.001,
        'genotype_options': {
            'modes': ['read-register', 'read-input'],
            'simple_operations': ['+', '-', '*', '/'],
            'complex_operations': ['ln', 'exp', 'cos', 'sin', 'if_lesser_than', 'if_equal_or_higher_than'],
            'one-operand-instructions': ['ln', 'exp', 'cos', 'sin'],
            'if-instructions': ['if_lesser_than', 'if_equal_or_higher_than'],
            'instruction_size': 4,
            'output_registers': 1,
            'total_registers': None, # initialized by sbb.py
        },
        'total_actions': -1, # initialized by the environment
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
    }

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
            if diversity not in Config.RESTRICTIONS['diversity_options']:
                sys.stderr.write("Error: Invalid '"+diversity+"' diversity in CONFIG! The valid values are "+str(Config.RESTRICTIONS['diversity_options'])+"\n")
                raise SystemExit
        if Config.USER['task'] == 'classification':
            if 'normalized_compression_distance' in diversities:
                sys.stderr.write("Error: Can't calculate 'normalized_compression_distance' for a classification task!\n")
                raise SystemExit

        if Config.USER['task'] == 'reinforcement' and Config.USER['reinforcement_parameters']['hall_of_fame']['diversity']:
            if Config.USER['reinforcement_parameters']['hall_of_fame']['diversity'] not in Config.RESTRICTIONS['diversity_options']:
                sys.stderr.write("Error: Invalid 'diversity' for 'hall_of_fame' in CONFIG! The valid values are "+str(Config.RESTRICTIONS['diversity_options'])+"\n")
                raise SystemExit

        if Config.USER['task'] == 'reinforcement' and Config.USER['reinforcement_parameters']['environment'] not in Config.RESTRICTIONS['environment_types']:
            sys.stderr.write("Error: Invalid 'environment' in CONFIG! The valid values are "+str(Config.RESTRICTIONS['environment_types'])+"\n")
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

# To run SBB with a predefined parameter set, uncomment the next line. More defaults are available in /examples
# Config.USER = thyroid_config.THYROID_REGISTERS2
# Config.USER = tictactoe_config.TICTACTOE_DEFAULT
# Config.USER = poker_config.POKER_DEFAULT_ENTROPY_1