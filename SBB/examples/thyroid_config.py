import copy

"""
##### Results using Mann-Whitney U-Test (http://www.socscistatistics.com/tests/mannwhitney/Default2.aspx):

THYROID_DEFAULT < THYROID_WITH_PARETOS: (old)
The U-value is 168. The distribution is approximately normal. Therefore, the Z-value above can be used.
The Z-Score is -2.794. The p-value is 0.00528. The result is significant at p <= 0.05.

THYROID_WITH_PARETOS < THYROID_WITH_PARETO_FOR_TEAMS_ONLY: (old)
The U-value is 197. The distribution is approximately normal. Therefore, the Z-value above can be used.
The Z-Score is -2.2313. The p-value is 0.02574. The result is significant at p <= 0.05.

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
#################### OVERALL RESULTS #################### (old)

Test Score per Run: [0.73487, 0.64663, 0.81808, 0.64663, 0.97086, 0.88397, 0.59611, 0.87215, 0.88763, 0.88425, 0.93716, 0.93864, 0.85918, 0.87286, 0.90614, 0.64663, 0.77507, 0.64663, 0.92979, 0.93025, 0.95475, 0.93108, 0.95831, 0.67403, 0.96206]
mean: 0.83455
std. deviation: 0.12124

Train Score per Generation across Runs:
mean: [0.525, 0.70866, 0.73999, 0.78133, 0.79633, 0.81866, 0.83166]
std. deviation: [0.07582, 0.1051, 0.09507, 0.1212, 0.11125, 0.10972, 0.11303]

Test Score per Generation across Runs:
mean: [0.52352, 0.70024, 0.74573, 0.77426, 0.78983, 0.80986, 0.83455]
std. deviation: [0.08604, 0.09477, 0.09776, 0.1187, 0.11562, 0.10995, 0.12124]

Finished execution, total elapsed time: 16250.383 secs (mean: 650.01532, std: 179.87195)

"""

THYROID_WITH_PARETOS = copy.deepcopy(THYROID_DEFAULT)
THYROID_WITH_PARETOS['advanced_training_parameters']['use_pareto_for_team_population_selection'] = True
THYROID_WITH_PARETOS['advanced_training_parameters']['use_pareto_for_point_population_selection'] = True
"""
#################### OVERALL RESULTS #################### (old)

Test Score per Run: [0.64459, 0.6969, 0.96019, 0.7823, 0.77515, 0.94043, 0.97135, 0.85577, 0.93783, 0.93661, 0.8784, 0.94235, 0.90138, 0.97607, 0.87257, 0.97954, 0.90812, 0.93232, 0.93648, 0.96286, 0.87725, 0.72491, 0.95513, 0.90305, 0.96395]
mean: 0.88862
std. deviation: 0.09112

Train Score per Generation across Runs:
mean: [0.55799, 0.76033, 0.795, 0.83066, 0.83266, 0.84566, 0.85233]
std. deviation: [0.06512, 0.08118, 0.06227, 0.06154, 0.06441, 0.07257, 0.07492]

Test Score per Generation across Runs:
mean: [0.56046, 0.76837, 0.83837, 0.86429, 0.87533, 0.869, 0.88862]
std. deviation: [0.06466, 0.11167, 0.10988, 0.09894, 0.09192, 0.09477, 0.09112]

Finished execution, total elapsed time: 14872.799 secs (mean: 594.91196, std: 2113.68824)
"""

THYROID_WITH_PARETO_FOR_TEAMS_ONLY = copy.deepcopy(THYROID_DEFAULT)
THYROID_WITH_PARETO_FOR_TEAMS_ONLY['advanced_training_parameters']['use_pareto_for_team_population_selection'] = True
"""
#################### OVERALL RESULTS #################### (old)

Test Score per Run: [0.82456, 0.97561, 0.95241, 0.9617, 0.95283, 0.90201, 0.97351, 0.98405, 0.9754, 0.90388, 0.9351, 0.9754, 0.98137, 0.97534, 0.93341, 0.95244, 0.94634, 0.95919, 0.88091, 0.97351, 0.92812, 0.9754, 0.92768, 0.93859, 0.84532]
mean: 0.94136
std. deviation: 0.04116

Train Score per Generation across Runs:
mean: [0.55033, 0.83, 0.88466, 0.91633, 0.93433, 0.93766, 0.95]
std. deviation: [0.07765, 0.07986, 0.07366, 0.0578, 0.05604, 0.05627, 0.03162]

Test Score per Generation across Runs:
mean: [0.5472, 0.80719, 0.87172, 0.88456, 0.90929, 0.92799, 0.94136]
std. deviation: [0.07371, 0.09, 0.08718, 0.08507, 0.07379, 0.05454, 0.04116]

Finished execution, total elapsed time: 17018.09599 secs (mean: 680.72383, std: 82.18161)
"""

THYROID_WITH_PARETO_FOR_POINTS_ONLY = copy.deepcopy(THYROID_DEFAULT)
THYROID_WITH_PARETO_FOR_POINTS_ONLY['advanced_training_parameters']['use_pareto_for_point_population_selection'] = True
"""

"""