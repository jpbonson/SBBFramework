import copy

THYROID_DEFAULT = {
    'task': 'classification',
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
        'runs_total': 25,
        'generations_total': 300,
        'validate_after_each_generation': 50,
        'populations': {
            'programs': 120,
            'teams': 60,
            'points': 120,
        },
        'replacement_rate': {
            'teams': 0.7,
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
            'max': 9,
        },
        'program_size': {
            'initial': 10,
            'min': 2,
            'max': 20,
        },
    },

    'advanced_training_parameters': {
        'seed': 1, # default = None
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
    },
}
"""
#################### OVERALL RESULTS ####################

Test Score per Run: [0.8496, 0.64652, 0.61856, 0.88388, 0.86671, 0.88676, 0.8875, 0.64663, 0.95081, 0.88335, 0.81659, 0.86227, 0.92473, 0.71969, 0.88585, 0.92872, 0.89273, 0.87107, 0.76012, 0.90365, 0.88931, 0.65017, 0.72053, 0.88773, 0.85161]
mean: 0.8274036
std. deviation: 0.0986365550445

Train Score per Generation across Runs:
mean: [0.53733, 0.75566, 0.79299, 0.80166, 0.80133, 0.82933, 0.834]
std. deviation: [0.08618, 0.11214, 0.11744, 0.13102, 0.11675, 0.1122, 0.09515]

Test Score per Generation across Runs:
mean: [0.54309, 0.74477, 0.78557, 0.79533, 0.7988, 0.81862, 0.8274]
std. deviation: [0.08596, 0.1125, 0.11035, 0.11198, 0.11392, 0.10399, 0.09863]

Finished execution, total elapsed time: 14989.70999 secs (mean: 599.58839, std: 116.31353)

"""

THYROID_WITH_PARETO = copy.deepcopy(THYROID_DEFAULT)
THYROID_WITH_PARETO['advanced_training_parameters']['use_pareto_for_team_population_selection'] = True
THYROID_WITH_PARETO['advanced_training_parameters']['use_pareto_for_point_population_selection'] = True
"""


##### Results using Mann-Whitney U-Test (http://www.socscistatistics.com/tests/mannwhitney/Default2.aspx):

"""