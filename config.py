import sys

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
        'generations_total': 100,
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
                'remove_instruction': 0.8,
                'add_instruction': 0.9,
                'change_instruction': 0.9,
                'change_action': 0.1,
            },
        },
        'team_size': { # the min size is the total number of actions
            'max': 5,
        },
        'program_size': {
            'initial': 10,
            'min': 2,
            'max': 30,
        },
    },

    'advanced_training_parameters': {
        'use_operations': ['+', '-', '*', '/', 'ln', 'exp', 'cos', 'if_lesser_than', 'if_equal_or_higher_than'],
        'extra_registers': 1,
        'diversity': {
            'fitness_sharing': False,
            'genotype_fitness_maintanance': False,
            'genotype_fitness_maintanance_configs': {
                'p_value': 0.1,
                'k': 8,
            },        
        },
    },

    'verbose': { 
        # useful to set to 'True' if you are going to execute long runs
        # these values will be printed to the console and to the output file
        'show_recall_per_action_per_generation': False,
        'show_avg_dr_per_generations': False,
        'show_actions_distribution_per_generation': False,
    },
}

# restrictions
TASK_TYPES = ['classification', 'reinforcement']
WORKING_PATH = "pSBB/"
ROUND_DECIMALS_TO = 5
GENOTYPE_OPTIONS = {
    'operations': ['+', '-', '*', '/', 'ln', 'exp', 'cos', 'if_lesser_than', 'if_equal_or_higher_than'],
    'modes': ['read-register', 'read-input'],
    'one-operand-instructions': ['ln', 'exp', 'cos'],
    'if-instructions': ['if_lesser_than', 'if_equal_or_higher_than'],
}

""" Check if the parameters in CONFIG are valid """
def check_parameters():
    if CONFIG['task'] not in TASK_TYPES:
        sys.stderr.write("Error: Invalid 'task' in CONFIG! The valid values are "+str(TASK_TYPES)+"\n")
        raise SystemExit
    for op in CONFIG['advanced_training_parameters']['use_operations']:  
        if op not in GENOTYPE_OPTIONS['operations']:
            sys.stderr.write("Error: Invalid 'use_operations' in CONFIG! The valid values are "+str(CONFIG['advanced_training_parameters']['use_operations'])+"\n")
            raise SystemExit
    if CONFIG['advanced_training_parameters']['diversity']['fitness_sharing'] and CONFIG['advanced_training_parameters']['diversity']['genotype_fitness_maintanance']:
        sys.stderr.write("Error: Maximum of one diversity metric allowed!\n")
        raise SystemExit

check_parameters()