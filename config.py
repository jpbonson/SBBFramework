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
        'team_size': {
            'max': 5,
        },
        'program_size': {
            'initial': 10,
            'min': 2,
            'max': 30,
        },
    },

    'advanced_training_parameters': {
        'use_complex_functions': True,
        'extra_registers': 1,
        'diversity': {
            'fitness_sharing': False,
            'genotype_fitness_maintanance': False,
            'genotype_configs': {
                'p_value': 0.1,
                'k': 8,
            },        
        },
    },

    'verbose': {
        'show_actions_distribution_per_generation': False,
    },
}

# restrictions
TASK_TYPES = ['classification', 'reinforcement']
# WORKING_PATH = "C:/Users/jpbonson/Dropbox/Dalhousie Winter 2015/Genetic Algorithms/GeneticProgrammingSandbox/pSBB/"
WORKING_PATH = "pSBB/"

if CONFIG['advanced_training_parameters']['use_complex_functions']:
    GENOTYPE_OPTIONS = {
        'modes': ['read-register', 'read-input'],
        'op': ['+', '-', '*', '/', 'ln', 'exp', 'cos', 'if_lesser_than', 'if_equal_or_higher_than'],
        'one-operand-instructions': ['ln', 'exp', 'cos'],
        'if-instructions': ['if_lesser_than', 'if_equal_or_higher_than'],
    }
else:
    GENOTYPE_OPTIONS = {
        'modes': ['read-register', 'read-input'],
        'op': ['+', '-', '*', '/'],
        'one-operand-instructions': [],
        'if-instructions': [],
    }

# refatorar complex instructions
# class para instructions?
# checar imports

""" Check if the parameters in CONFIG are valid """
def check_parameters():
    if CONFIG['task'] not in TASK_TYPES:
        sys.stderr.write("Error: Invalid 'task' in CONFIG! The valid values are "+str(TASK_TYPES)+"\n")
        raise SystemExit
check_parameters()