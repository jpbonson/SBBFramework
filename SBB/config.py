import sys

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
            'environment': 'tictactoe', # must have a python implementation in the pSBB/environments folder, edit _initialize_environment() in SBB to add new environments
            'training_matches': 10,
            'test_matches': 100,
            'champion_matches': 1000,
            'print_matches': False, # use this option to debug
        },

        'training_parameters': {
            'runs_total': 2,
            'generations_total': 50,
            'validate_after_each_generation': 10,
            'populations': {
                'programs': 60,
                'teams': 30,
                'points': 120, # may not be used by some environments (eg.: tictactoe)
            },
            'replacement_rate': {
                'teams': 0.7,
                'points': 0.2,  # may not be used by some environments (eg.: tictactoe)
            },
            'mutation': {
                'team': {
                    'remove_program': 0.7,
                    'add_program': 0.8,
                },
                'program': {
                    'remove_instruction': 0.7,
                    'add_instruction': 0.8,
                    'change_instruction': 0.8,
                    'change_action': 0.1,
                },
            },
            'team_size': { # the min size is the total number of actions
                'max': 18,
            },
            'program_size': {
                'initial': 10,
                'min': 2,
                'max': 20,
            },
        },

        'advanced_training_parameters': {
            'seed': None, # default = None
            'use_pareto_for_team_population_selection': True, # if False, will select solutions by best fitness
            'use_pareto_for_point_population_selection': True, # if False, will select points using uniform probability
            'use_operations': ['+', '-', '*', '/', 'ln', 'exp', 'cos', 'if_lesser_than', 'if_equal_or_higher_than'],
            'extra_registers': 1,
            'diversity': {
                'genotype_fitness_maintanance': True,
                'fitness_sharing': True,
            },
            'diversity_configs': { # p_value is with how much strenght this diversity metric will be applied to the fitness
                'genotype_fitness_maintanance': {
                    'p_value': 0.1,
                    'k': 8,
                },
                'fitness_sharing': {
                    'p_value': 0.1,
                },       
            },
        },
    }

    # restrictions used to validate CONFIG and to control the system low-level configurations
    RESTRICTIONS = {
        'task_types': ['classification', 'reinforcement'],
        'working_path': "SBB/",
        'round_to_decimals': 5,
        'genotype_options': {
            'modes': ['read-register', 'read-input'],
            'simple_operations': ['+', '-', '*', '/'],
            'complex_operations': ['ln', 'exp', 'cos', 'sin', 'if_lesser_than', 'if_equal_or_higher_than'],
            'one-operand-instructions': ['ln', 'exp', 'cos', 'sin'],
            'if-instructions': ['if_lesser_than', 'if_equal_or_higher_than'],
            'instruction_size': 4,
            'output_registers': 1,
            'total_registers': 1+USER['advanced_training_parameters']['extra_registers'],
        },
        'total_actions': -1, # initialized by the environment
        'total_inputs': -1, # initialized by the environment
        'action_mapping': {}, # initialized by the environment
        'use_memmory': False, # initialized by the environment
        'write_output_files': True, # used by the test cases
    }

    @staticmethod
    def check_parameters():
        """
        Check if the parameters in CONFIG are valid using RESTRICTIONS
        """
        if Config.USER['task'] not in Config.RESTRICTIONS['task_types']:
            sys.stderr.write("Error: Invalid 'task' in CONFIG! The valid values are "+str(Config.RESTRICTIONS['task_types'])+"\n")
            raise SystemExit

        valid_operations = Config.RESTRICTIONS['genotype_options']['simple_operations'] + Config.RESTRICTIONS['genotype_options']['complex_operations']
        for op in Config.USER['advanced_training_parameters']['use_operations']:  
            if op not in valid_operations:
                sys.stderr.write("Error: Invalid 'use_operations' in CONFIG! The valid values are "+str(valid_operations)+"\n")
                raise SystemExit

        if Config.USER['training_parameters']['generations_total'] % Config.USER['training_parameters']['validate_after_each_generation'] != 0:
            sys.stderr.write("Error: 'validate_after_each_generation' should be a multiple for 'generations_total', in order to ensure validation of the last generation.\n")
            raise SystemExit