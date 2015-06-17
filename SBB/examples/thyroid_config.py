import copy

"""
##### Results using Mann-Whitney U-Test (http://www.socscistatistics.com/tests/mannwhitney/Default2.aspx):

### COMPARISON REGARDING PARETO FRONT

THYROID_DEFAULT < THYROID_WITH_PARETOS:
The U-value is 137. The distribution is approximately normal. Therefore, the Z-value above can be used.
The Z-Score is -3.3955. The p-value is 0.00068. The result is significant at p <= 0.05.

THYROID_WITH_PARETOS == THYROID_WITH_PARETO_FOR_TEAM_ONLY
The U-value is 278. The distribution is approximately normal. Therefore, the Z-value above can be used.
The Z-Score is 0.6597. The p-value is 0.50926. The result is not significant at p <= 0.05.

THYROID_WITH_PARETOS > THYROID_WITH_PARETO_FOR_POINT_ONLY
The U-value is 190. The distribution is approximately normal. Therefore, the Z-value above can be used.
The Z-Score is 2.3671. The p-value is 0.01778. The result is significant at p <= 0.05.

THYROID_WITH_PARETO_FOR_TEAM_ONLY == THYROID_WITH_PARETO_FOR_POINT_ONLY
The U-value is 219. The distribution is approximately normal. Therefore, the Z-value above can be used.
The Z-Score is 1.8045. The p-value is 0.07186. The result is not significant at p <= 0.05.

Result: THYROID_WITH_PARETOS

### COMPARISON REGARDING STEP2 IN INITIALIZATION

THYROID_WITH_PARETOS ? THYROID_WITH_PARETOS_WITH_INIT2


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
            'teams': 80,
            'points': 120,
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
        'team_size': { # the min size is the total number of actions
            'min': 2,
            'max': 9,
        },
        'program_size': {
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
        'run_initialization_step2': False,
    },
}
"""
#################### OVERALL RESULTS ####################

Test Score per Run: [0.93968, 0.84174, 0.86566, 0.74651, 0.89466, 0.96654, 0.87476, 0.89466, 0.65502, 0.92675, 0.89483, 0.97494, 0.96469, 0.87886, 0.86556, 0.88882, 0.87538, 0.75205, 0.89466, 0.9754, 0.9743, 0.73868, 0.80234, 0.85047, 0.92488]
mean: 0.87447
std. deviation: 0.0808
best run: 20

Train Score per Generation across Runs:
mean: [0.49766, 0.748, 0.80133, 0.834, 0.84966, 0.88066, 0.89599]
std. deviation: [0.10618, 0.09583, 0.10681, 0.1001, 0.1007, 0.08633, 0.08103]

Test Score per Generation across Runs:
mean: [0.49462, 0.73521, 0.794, 0.82286, 0.84281, 0.86005, 0.87447]
std. deviation: [0.1052, 0.09856, 0.10679, 0.09927, 0.09958, 0.09298, 0.0808]

Finished execution, total elapsed time: 7039.47654 secs (mean: 281.57906, std: 103.43281)
"""

THYROID_WITH_PARETOS = copy.deepcopy(THYROID_DEFAULT)
THYROID_WITH_PARETOS['advanced_training_parameters']['use_pareto_for_team_population_selection'] = True
THYROID_WITH_PARETOS['advanced_training_parameters']['use_pareto_for_point_population_selection'] = True
"""
#################### OVERALL RESULTS ####################

Test Score per Run: [0.9063, 0.97161, 0.86276, 0.9092, 0.96421, 0.93336, 0.9554, 0.90153, 0.97048, 0.95012, 0.96375, 0.90897, 0.95139, 0.97772, 0.99129, 0.96021, 0.92455, 0.97304, 0.97683, 0.93143, 0.95265, 0.94095, 0.95705, 0.96158, 0.91164]
mean: 0.94432
std. deviation: 0.03004
best run: 15

Train Score per Generation across Runs:
mean: [0.49766, 0.76566, 0.80766, 0.85133, 0.86433, 0.87033, 0.885]
std. deviation: [0.10618, 0.072, 0.05358, 0.05886, 0.04821, 0.04333, 0.05467]

Test Score per Generation across Runs:
mean: [0.49462, 0.79749, 0.87264, 0.91202, 0.92783, 0.93648, 0.94432]
std. deviation: [0.1052, 0.09894, 0.07933, 0.05349, 0.03952, 0.03551, 0.03004]

Finished execution, total elapsed time: 17123.86355 secs (mean: 684.95454, std: 93.36165)
"""

THYROID_WITH_PARETO_FOR_TEAM_ONLY = copy.deepcopy(THYROID_DEFAULT)
THYROID_WITH_PARETO_FOR_TEAM_ONLY['advanced_training_parameters']['use_pareto_for_team_population_selection'] = True
THYROID_WITH_PARETO_FOR_TEAM_ONLY['advanced_training_parameters']['use_pareto_for_point_population_selection'] = False
"""
#################### OVERALL RESULTS ####################

Test Score per Run: [0.92108, 0.88554, 0.92352, 0.97163, 0.91356, 0.8996, 0.9754, 0.89842, 0.9787, 0.96286, 0.74019, 0.97093, 0.97362, 0.95377, 0.92403, 0.94614, 0.93551, 0.91464, 0.91393, 0.97083, 0.97068, 0.86836, 0.94607, 0.92203, 0.97808]
mean: 0.93036
std. deviation: 0.04991
best run: 9

Train Score per Generation across Runs:
mean: [0.49766, 0.78833, 0.89433, 0.921, 0.93366, 0.94733, 0.95366]
std. deviation: [0.10618, 0.09128, 0.05506, 0.04282, 0.04651, 0.04154, 0.03764]

Test Score per Generation across Runs:
mean: [0.49462, 0.76898, 0.86967, 0.89293, 0.92111, 0.9255, 0.93037]
std. deviation: [0.1052, 0.10063, 0.06671, 0.07241, 0.05683, 0.05523, 0.04991]

Finished execution, total elapsed time: 8806.14087 secs (mean: 352.24563, std: 82.29449)
"""

THYROID_WITH_PARETO_FOR_POINT_ONLY = copy.deepcopy(THYROID_DEFAULT)
THYROID_WITH_PARETO_FOR_POINT_ONLY['advanced_training_parameters']['use_pareto_for_team_population_selection'] = False
THYROID_WITH_PARETO_FOR_POINT_ONLY['advanced_training_parameters']['use_pareto_for_point_population_selection'] = True
"""
Test Score per Run: [0.89466, 0.9254, 0.6349, 0.84708, 0.87804, 0.97479, 0.91599, 0.88794, 0.77344, 0.9431, 0.86801, 0.98678, 0.96829, 0.97456, 0.9521, 0.8698, 0.62995, 0.69674, 0.94428, 0.95353, 0.90621, 0.83681, 0.66155, 0.9744, 0.96145]
mean: 0.87439
std. deviation: 0.10832
best run: 12

Train Score per Generation across Runs:
mean: [0.49766, 0.71899, 0.76366, 0.768, 0.80333, 0.812, 0.82733]
std. deviation: [0.10618, 0.08684, 0.09439, 0.0943, 0.08462, 0.06442, 0.07009]

Test Score per Generation across Runs:
mean: [0.49462, 0.73722, 0.79912, 0.80485, 0.82723, 0.84904, 0.87439]
std. deviation: [0.1052, 0.10485, 0.12844, 0.12219, 0.12927, 0.11914, 0.10832]

Finished execution, total elapsed time: 17771.89055 secs (mean: 710.87562, std: 118.74661)
"""

THYROID_WITH_PARETOS_WITH_INIT2 = copy.deepcopy(THYROID_WITH_PARETOS)
THYROID_WITH_PARETOS_WITH_INIT2['advanced_training_parameters']['run_initialization_step2'] = True
"""

"""