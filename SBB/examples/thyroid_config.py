import copy

"""
##### Results using Mann-Whitney U-Test (http://www.socscistatistics.com/tests/mannwhitney/Default2.aspx):

### COMPARISON REGARDING PARETO FRONT

THYROID_DEFAULT < THYROID_WITH_PARETOS:
The U-value is 137. The distribution is approximately normal. Therefore, the Z-value can be used.
The Z-Score is -3.3955. The p-value is 0.00068. The result is significant at p <= 0.05.

THYROID_WITH_PARETOS == THYROID_WITH_PARETO_FOR_TEAM_ONLY
The U-value is 278. The distribution is approximately normal. Therefore, the Z-value can be used.
The Z-Score is 0.6597. The p-value is 0.50926. The result is not significant at p <= 0.05.

THYROID_WITH_PARETOS > THYROID_WITH_PARETO_FOR_POINT_ONLY
The U-value is 190. The distribution is approximately normal. Therefore, the Z-value can be used.
The Z-Score is 2.3671. The p-value is 0.01778. The result is significant at p <= 0.05.

THYROID_WITH_PARETO_FOR_TEAM_ONLY == THYROID_WITH_PARETO_FOR_POINT_ONLY
The U-value is 219. The distribution is approximately normal. Therefore, the Z-value can be used.
The Z-Score is 1.8045. The p-value is 0.07186. The result is not significant at p <= 0.05.

Result: THYROID_WITH_PARETOS

### COMPARISON REGARDING STEP2 IN INITIALIZATION

THYROID_WITH_PARETOS == THYROID_WITH_PARETOS_WITH_INIT2
The U-value is 309. The distribution is approximately normal. Therefore, the Z-value can be used.
The Z-Score is -0.0582. The p-value is 0.95216. The result is not significant at p <= 0.05.

### COMPARISON REGARDING DIVERSITY

THYROID_WITH_PARETOS > THYROID_WITH_PARETOS_GENOTYPE_DIVERSITY03
The U-value is 151. The distribution is approximately normal. Therefore, the Z-value can be used.
The Z-Score is 3.1239. The p-value is 0.0018. The result is significant at p <= 0.05.

THYROID_WITH_PARETOS > THYROID_WITH_PARETOS_GENOTYPE_DIVERSITY05
The U-value is 113. The distribution is approximately normal. Therefore, the Z-value can be used.
The Z-Score is 3.8612. The p-value is 0.00012. The result is significant at p <= 0.05.

THYROID_WITH_PARETOS_GENOTYPE_DIVERSITY03 == THYROID_WITH_PARETOS_GENOTYPE_DIVERSITY05
The U-value is 247. The distribution is approximately normal. Therefore, the Z-value above can be used.
The Z-Score is 1.2612. The p-value is 0.20766. The result is not significant at p <= 0.05.
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
                'p_value': 0.3,
                'k': 8,
            },
            'fitness_sharing': {
                'p_value': 0.3,
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
#################### OVERALL RESULTS ####################

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
#################### OVERALL RESULTS ####################

Test Score per Run: [0.95426, 0.89435, 0.98604, 0.95046, 0.90764, 0.85537, 0.97965, 0.9324, 0.94663, 0.97041, 0.92708, 0.97215, 0.90459, 0.98164, 0.97946, 0.89659, 0.85201, 0.91057, 0.86968, 0.97124, 0.98573, 0.98798, 0.95217, 0.96331, 0.97243]
mean: 0.94015
std. deviation: 0.04177
best run: 22

Train Score per Generation across Runs:
mean: [0.50433, 0.75733, 0.82333, 0.84066, 0.85366, 0.86966, 0.88333]
std. deviation: [0.09083, 0.07196, 0.06867, 0.06152, 0.05523, 0.04587, 0.05259]

Test Score per Generation across Runs:
mean: [0.51286, 0.77806, 0.86982, 0.90174, 0.92266, 0.93113, 0.94015]
std. deviation: [0.09396, 0.10801, 0.0883, 0.07082, 0.04645, 0.04039, 0.04177]

Finished execution, total elapsed time: 17909.92512 secs (mean: 716.397, std: 59.22564)
"""

THYROID_WITH_PARETOS_GENOTYPE_DIVERSITY03 = copy.deepcopy(THYROID_WITH_PARETOS)
THYROID_WITH_PARETOS_GENOTYPE_DIVERSITY03['advanced_training_parameters']['diversity']['genotype_fitness_maintanance'] = True
"""
#################### OVERALL RESULTS ####################

Test Score per Run: [0.86774, 0.85546, 0.88318, 0.88313, 0.96044, 0.84929, 0.90413, 0.97579, 0.94778, 0.90749, 0.85579, 0.86504, 0.91821, 0.88369, 0.92023, 0.84667, 0.95005, 0.84632, 0.90481, 0.96699, 0.97369, 0.94749, 0.95103, 0.84829, 0.92461]
mean: 0.90549
std. deviation: 0.04366
best run: 8

Train Score per Generation across Runs:
mean: [0.49766, 0.661, 0.72933, 0.76166, 0.77199, 0.78366, 0.81]
std. deviation: [0.10618, 0.06756, 0.07223, 0.06087, 0.07011, 0.06215, 0.06289]

Test Score per Generation across Runs:
mean: [0.49462, 0.68539, 0.79235, 0.85164, 0.86913, 0.88336, 0.90549]
std. deviation: [0.1052, 0.09335, 0.10012, 0.06131, 0.06795, 0.04465, 0.04366]

Mean Diversity per Generation across Runs (genotype_diversity):
mean: [1.0, 0.81742, 0.81098, 0.8078, 0.80446, 0.8086, 0.80619]
std. deviation: [0.0, 0.02074, 0.0197, 0.02828, 0.02715, 0.02823, 0.02944]

Finished execution, total elapsed time: 16888.77011 secs (mean: 675.5508, std: 77.03365)
"""

THYROID_WITH_PARETOS_GENOTYPE_DIVERSITY05 = copy.deepcopy(THYROID_WITH_PARETOS)
THYROID_WITH_PARETOS_GENOTYPE_DIVERSITY05['advanced_training_parameters']['diversity']['genotype_fitness_maintanance'] = True
THYROID_WITH_PARETOS_GENOTYPE_DIVERSITY05['advanced_training_parameters']['diversity_configs']['genotype_fitness_maintanance']['p_value'] = 0.5
"""
#################### OVERALL RESULTS ####################

Test Score per Run: [0.86297, 0.89018, 0.93213, 0.88537, 0.84332, 0.84826, 0.88814, 0.917, 0.84282, 0.83364, 0.9058, 0.89267, 0.85013, 0.66477, 0.93729, 0.87304, 0.5619, 0.80769, 0.88261, 0.98143, 0.91175, 0.96817, 0.97996, 0.92095, 0.90181]
mean: 0.87135
std. deviation: 0.0889
best run: 20

Train Score per Generation across Runs:
mean: [0.49766, 0.58466, 0.65799, 0.68933, 0.73533, 0.73733, 0.78]
std. deviation: [0.10618, 0.07872, 0.09313, 0.08421, 0.06188, 0.09655, 0.06514]

Test Score per Generation across Runs:
mean: [0.49462, 0.59988, 0.70635, 0.74293, 0.80787, 0.81424, 0.87135]
std. deviation: [0.1052, 0.0956, 0.11911, 0.12048, 0.09526, 0.11586, 0.0889]

Mean Diversity per Generation across Runs (genotype_diversity):
mean: [1.0, 0.85205, 0.84515, 0.8369, 0.83685, 0.81965, 0.81555]
std. deviation: [0.0, 0.01628, 0.02001, 0.02329, 0.0275, 0.02846, 0.0303]

Finished execution, total elapsed time: 16413.5297 secs (mean: 656.54118, std: 48.3727)
"""

THYROID_WITH_PARETOS_GENOTYPE_DIVERSITY02 = copy.deepcopy(THYROID_WITH_PARETOS)
THYROID_WITH_PARETOS_GENOTYPE_DIVERSITY02['advanced_training_parameters']['diversity']['genotype_fitness_maintanance'] = True
THYROID_WITH_PARETOS_GENOTYPE_DIVERSITY02['advanced_training_parameters']['diversity_configs']['genotype_fitness_maintanance']['p_value'] = 0.2
"""

"""

THYROID_WITH_PARETOS_GENOTYPE_DIVERSITY01 = copy.deepcopy(THYROID_WITH_PARETOS)
THYROID_WITH_PARETOS_GENOTYPE_DIVERSITY01['advanced_training_parameters']['diversity']['genotype_fitness_maintanance'] = True
THYROID_WITH_PARETOS_GENOTYPE_DIVERSITY01['advanced_training_parameters']['diversity_configs']['genotype_fitness_maintanance']['p_value'] = 0.1
"""

"""