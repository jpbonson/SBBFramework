import sys

# user configurable options
CONFIG = {
    'task': 'classification',
    'classification_parameters': { # only used if 'task' is 'classification'
        'dataset': 'thyroid', # must have a .train and a .test file in the pSBB/datasets folder
        'use_oversampling': True,
    }, 
    'reinforcement_parameters': { # only used if 'task' is 'reinforcement'
        'environment': 'tictactoe', # must have a python implementation in the pSBB/environments folder
    },

    'training_parameters': {
        'runs_total': 2,
        'generations_total': 30,
        'populations': {
            'programs': 60,
            'teams': 30, # must be half the population_size (?)
            'points': 120,
        },
        'replacement_rate': {
            'teams': 0.6,
            'points': 0.2,
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
            'max': 5,
        },
        'program_size': {
            'initial': 3,
            'min': 2,
            'max': 5,
        },
    },

    'advanced_training_parameters': {
        'seed': None, # default = None
        'use_pareto_for_team_population_selection': False, # if False, will use weighted choice
        'use_operations': ['+', '-', '*', '/', 'ln', 'exp', 'cos', 'if_lesser_than', 'if_equal_or_higher_than'],
        'extra_registers': 1,
        'diversity': {
            'genotype_fitness_maintanance': True,
        },
        'diversity_configs': {
            'genotype_fitness_maintanance': {
                'p_value': 0.1,
                'k': 8,
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

    one_active_diversity = False
    for _, value in CONFIG['advanced_training_parameters']['diversity'].iteritems():
        if value and one_active_diversity:
            sys.stderr.write("Error: Maximum of one active diversity metric allowed!\n")
            raise SystemExit
        if value and not one_active_diversity:
            one_active_diversity = True

    if CONFIG['advanced_training_parameters']['verbose'] not in RESTRICTIONS['verbose_levels']:
        sys.stderr.write("Error: Invalid 'verbose' in CONFIG! The valid values are "+str(RESTRICTIONS['verbose_levels'])+"\n")
        raise SystemExit

check_parameters()