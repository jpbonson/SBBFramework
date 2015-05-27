import sys

# user configurable options
CONFIG = {
    'task': 'reinforcement',
    'classification_parameters': { # only used if 'task' is 'classification'
        'dataset': 'thyroid', # must have a .train and a .test file in the pSBB/datasets folder
    }, 
    'reinforcement_parameters': { # only used if 'task' is 'reinforcement'
        'environment': 'tictactoe', # must have a python implementation in the pSBB/environments folder, edit _initialize_environment() in SBB to add new environments
        'total_matches': 50,
    },

    'training_parameters': {
        'runs_total': 2,
        'generations_total': 100,
        'populations': {
            'programs': 120,
            'teams': 60,
            'points': 120, # may not be used by some environments (eg.: tictactoe)
        },
        'replacement_rate': {
            'teams': 0.8,
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
            'max': 12,
        },
        'program_size': {
            'initial': 10,
            'min': 2,
            'max': 20,
        },
    },

    'advanced_training_parameters': {
        'seed': None, # default = None
        'use_pareto_for_team_population_selection': False, # if False, will select solutions by best fitness
        'use_pareto_for_point_population_selection': False, # if False, will select points using uniform probability
        'use_operations': ['+', '-', '*', '/', 'ln', 'exp', 'cos', 'if_lesser_than', 'if_equal_or_higher_than'],
        'extra_registers': 1,
        'diversity': {
            'genotype_fitness_maintanance': False,
            'fitness_sharing': False,
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
        'verbose': 1, # default = 1
                      # = 2 if you are new to SBB, is debugging or are going to run really long jobs (ie. want the maximum information)
                      # = 0 for just the necessary minimum information
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
        'total_registers': 1+CONFIG['advanced_training_parameters']['extra_registers'],
    },
    'total_actions': -1, # initialized by the environment
    'total_inputs': -1, # initialized by the environment
    'action_mapping': {}, # initialized by the environment
    'use_memmory': False, # initialized by the environment
    'verbose_levels': [0, 1, 2],
}


""" Check if the parameters in CONFIG are valid using RESTRICTIONS """
def check_parameters():
    if CONFIG['task'] not in RESTRICTIONS['task_types']:
        sys.stderr.write("Error: Invalid 'task' in CONFIG! The valid values are "+str(RESTRICTIONS['task_types'])+"\n")
        raise SystemExit

    valid_operations = RESTRICTIONS['genotype_options']['simple_operations'] + RESTRICTIONS['genotype_options']['complex_operations']
    for op in CONFIG['advanced_training_parameters']['use_operations']:  
        if op not in valid_operations:
            sys.stderr.write("Error: Invalid 'use_operations' in CONFIG! The valid values are "+str(valid_operations)+"\n")
            raise SystemExit

    if CONFIG['advanced_training_parameters']['verbose'] not in RESTRICTIONS['verbose_levels']:
        sys.stderr.write("Error: Invalid 'verbose' in CONFIG! The valid values are "+str(RESTRICTIONS['verbose_levels'])+"\n")
        raise SystemExit

check_parameters()