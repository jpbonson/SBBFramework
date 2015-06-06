import copy

"""
##### Results using Mann-Whitney U-Test (http://www.socscistatistics.com/tests/mannwhitney/Default2.aspx):

THYROID_DEFAULT < THYROID_WITH_PARETO:
The U-value is 168. The distribution is approximately normal. Therefore, the Z-value above can be used.
The Z-Score is -2.794. The p-value is 0.00528. The result is significant at p≤ 0.05.



"""

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
#################### OVERALL RESULTS ####################

Test Score per Run: [0.64459, 0.6969, 0.96019, 0.7823, 0.77515, 0.94043, 0.97135, 0.85577, 0.93783, 0.93661, 0.8784, 0.94235, 0.90138, 0.97607, 0.87257, 0.97954, 0.90812, 0.93232, 0.93648, 0.96286, 0.87725, 0.72491, 0.95513, 0.90305, 0.96395]
mean: 0.88862
std. deviation: 0.0911253303094

Train Score per Generation across Runs:
mean: [0.55799, 0.76033, 0.795, 0.83066, 0.83266, 0.84566, 0.85233]
std. deviation: [0.06512, 0.08118, 0.06227, 0.06154, 0.06441, 0.07257, 0.07492]

Test Score per Generation across Runs:
mean: [0.56046, 0.76837, 0.83837, 0.86429, 0.87533, 0.869, 0.88862]
std. deviation: [0.06466, 0.11167, 0.10988, 0.09894, 0.09192, 0.09477, 0.09112]

Finished execution, total elapsed time: 14872.799 secs (mean: 594.91196, std: 2113.68824)
"""