import copy

THYROID_DEFAULT = {
    'task': 'classification',
    'classification_parameters': { # only used if 'task' is 'classification'
        'dataset': 'thyroid', # must have a .train and a .test file in the pSBB/datasets folder
    }, 

    'training_parameters': {
        'runs_total': 25,
        'generations_total': 300,
        'validate_after_each_generation': 50,
        'populations': {
            'programs': 120,
            'teams': 60,
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

Test Score per Run: [0.87252, 0.9633, 0.83347, 0.91207, 0.98101, 0.90525, 0.86102, 0.64607, 0.98029, 0.85677, 0.53083, 0.90345, 0.93229, 0.87578, 0.91561, 0.78817, 0.91021, 0.94862, 0.8671, 0.96874, 0.89328, 0.66416, 0.84102, 0.81411, 0.92112]
mean: 0.8634504
std. deviation: 0.106350925054

Train Score per Generation across Runs:
mean: [0.53299, 0.75166, 0.79966, 0.83299, 0.84766, 0.85366, 0.86066]
std. deviation: [0.08421, 0.14212, 0.11868, 0.10794, 0.10103, 0.11217, 0.10462]

Test Score per Generation across Runs:
mean: [0.52268, 0.75596, 0.79362, 0.82899, 0.83987, 0.85555, 0.86345]
std. deviation: [0.08663, 0.12197, 0.11884, 0.10717, 0.10676, 0.10278, 0.10634]

Finished execution, total elapsed time: 16664.12 secs (mean: 666.5648, std: 122.92846)
"""

THYROID_WITH_PARETO = copy.deepcopy(THYROID_DEFAULT)
THYROID_WITH_PARETO['advanced_training_parameters']['use_pareto_for_team_population_selection'] = True
THYROID_WITH_PARETO['advanced_training_parameters']['use_pareto_for_point_population_selection'] = True
"""
#################### OVERALL RESULTS ####################

Test Score per Run: [0.9359, 0.92688, 0.80415, 0.93901, 0.89512, 0.90193, 0.97541, 0.9493, 0.88491, 0.89903, 0.91519, 0.8951, 0.848, 0.95963, 0.92072, 0.97645, 0.95148, 0.9625, 0.91999, 0.86205, 0.94975, 0.89287, 0.88386, 0.86669, 0.79967]
mean: 0.9086236
std. deviation: 0.0466395722004

Train Score per Generation across Runs:
mean: [0.56233, 0.83033, 0.89899, 0.92466, 0.94566, 0.96133, 0.966]
std. deviation: [0.0836, 0.09332, 0.05978, 0.05107, 0.03993, 0.03017, 0.02885]

Test Score per Generation across Runs:
mean: [0.5468, 0.81044, 0.85383, 0.87804, 0.89105, 0.91254, 0.90862]
std. deviation: [0.09441, 0.09349, 0.07772, 0.05945, 0.05571, 0.03456, 0.04663]

Finished execution, total elapsed time: 20276.60299 secs (mean: 811.06411, std: 67.81258)

##### Results using Mann-Whitney U-Test (http://www.socscistatistics.com/tests/mannwhitney/Default2.aspx):

"""