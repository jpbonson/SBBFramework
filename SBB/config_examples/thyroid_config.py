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

Results: Increases runtime without increasing performance.


### COMPARISON REGARDING GENOTYPE DIVERSITY

THYROID_WITH_PARETOS > THYROID_WITH_PARETOS_GENOTYPE_DIVERSITY03
The U-value is 151. The distribution is approximately normal. Therefore, the Z-value can be used.
The Z-Score is 3.1239. The p-value is 0.0018. The result is significant at p <= 0.05.

THYROID_WITH_PARETOS > THYROID_WITH_PARETOS_GENOTYPE_DIVERSITY05
The U-value is 113. The distribution is approximately normal. Therefore, the Z-value can be used.
The Z-Score is 3.8612. The p-value is 0.00012. The result is significant at p <= 0.05.

THYROID_WITH_PARETOS_GENOTYPE_DIVERSITY03 == THYROID_WITH_PARETOS_GENOTYPE_DIVERSITY05
The U-value is 247. The distribution is approximately normal. Therefore, the Z-value can be used.
The Z-Score is 1.2612. The p-value is 0.20766. The result is not significant at p <= 0.05.

THYROID_WITH_PARETOS > THYROID_WITH_PARETOS_GENOTYPE_DIVERSITY02
The U-value is 189. The distribution is approximately normal. Therefore, the Z-value can be used.
The Z-Score is 2.3866. The p-value is 0.01684. The result is significant at p <= 0.05.

THYROID_WITH_PARETOS == THYROID_WITH_PARETOS_GENOTYPE_DIVERSITY01
The U-value is 251. The distribution is approximately normal. Therefore, the Z-value can be used.
The Z-Score is 1.1836. The p-value is 0.238. The result is not significant at p <= 0.05.

Result: Genotype diversity wasn't very useful for this dataset and configuration, the only one 
that didn't decrease the performance was THYROID_WITH_PARETOS_GENOTYPE_DIVERSITY01. Further tests, 
for more generations, may improve the performance.


### COMPARISON REGARDING FITNESS SHARING DIVERSITY

THYROID_WITH_PARETOS == THYROID_WITH_PARETOS_SHARING_DIVERSITY02
The U-value is 278. The distribution is approximately normal. Therefore, the Z-value can be used.
The Z-Score is 0.6597. The p-value is 0.50926. The result is not significant at p <= 0.05.

THYROID_WITH_PARETOS == THYROID_WITH_PARETOS_SHARING_DIVERSITY03
The U-value is 245. The distribution is approximately normal. Therefore, the Z-value can be used.
The Z-Score is -1.3. The p-value is 0.1936. The result is not significant at p <= 0.05.

THYROID_WITH_PARETOS == THYROID_WITH_PARETOS_SHARING_DIVERSITY04
The U-value is 277. The distribution is approximately normal. Therefore, the Z-value can be used.
The Z-Score is -0.6791. The p-value is 0.4965. The result is not significant at p <= 0.05.

THYROID_WITH_PARETOS > THYROID_WITH_PARETOS_SHARING_DIVERSITY05
The U-value is 194. The distribution is approximately normal. Therefore, the Z-value can be used.
The Z-Score is 2.2895. The p-value is 0.02202. The result is significant at p <= 0.05.

Result: Fitness sharing wasn't very useful for this dataset and configuration, for p values equal or 
lower than 0.4 the diversity didn't decrease the performance. Further tests, for more generations, may 
improve the performance.


### COMPARISON REGARDING GENOTYPE DIVERSITY WITHOUT PARETO

THYROID_DEFAULT == THYROID_GENOTYPE_DIVERSITY03
The U-value is 295.5. The distribution is approximately normal. Therefore, the Z-value can be used.
The Z-Score is 0.3201. The p-value is 0.74896. The result is not significant at p <= 0.05.

THYROID_DEFAULT == THYROID_GENOTYPE_DIVERSITY04
The U-value is 299. The distribution is approximately normal. Therefore, the Z-value can be used.
The Z-Score is -0.2522. The p-value is 0.80258. The result is not significant at p <= 0.05.

THYROID_DEFAULT == THYROID_GENOTYPE_DIVERSITY05
The U-value is 233.5. The distribution is approximately normal. Therefore, the Z-value can be used.
The Z-Score is 1.5231. The p-value is 0.12852. The result is not significant at p <= 0.05.

THYROID_DEFAULT > THYROID_GENOTYPE_DIVERSITY06
The U-value is 195.5. The distribution is approximately normal. Therefore, the Z-value can be used.
The Z-Score is 2.2604. The p-value is 0.02382. The result is significant at p <= 0.05.

Result: Genotype diversity wasn't very useful for this dataset and configuration, for p values equal or 
lower than 0.5 the diversity didn't decrease the performance. Further tests, for more generations, may 
improve the performance.

### COMPARISON REGARDING FITNESS SHARING DIVERSITY WITHOUT PARETO

THYROID_DEFAULT == THYROID_SHARING_DIVERSITY03
The U-value is 268.5. The distribution is approximately normal. Therefore, the Z-value can be used.
The Z-Score is -0.844. The p-value is 0.4009. The result is not significant at p <= 0.05.

THYROID_DEFAULT == THYROID_SHARING_DIVERSITY04
The U-value is 244. The distribution is approximately normal. Therefore, the Z-value can be used.
The Z-Score is -1.3194. The p-value is 0.18684. The result is not significant at p <= 0.05.

THYROID_DEFAULT == THYROID_SHARING_DIVERSITY05
The U-value is 253.5. The distribution is approximately normal. Therefore, the Z-value can be used.
The Z-Score is -1.1351. The p-value is 0.25428. The result is not significant at p <= 0.05.

THYROID_DEFAULT == THYROID_SHARING_DIVERSITY06
The U-value is 259.5. The distribution is approximately normal. Therefore, the Z-value can be used.
The Z-Score is -1.0186. The p-value is 0.30772. The result is not significant at p <= 0.05.

THYROID_DEFAULT == THYROID_SHARING_DIVERSITY07
The U-value is 298.5. The distribution is approximately normal. Therefore, the Z-value can be used.
The Z-Score is -0.2619. The p-value is 0.79486. The result is not significant at p <= 0.05.

THYROID_DEFAULT == THYROID_SHARING_DIVERSITY08
The U-value is 279.5. The distribution is approximately normal. Therefore, the Z-value can be used.
The Z-Score is -0.6306. The p-value is 0.5287. The result is not significant at p <= 0.05.

THYROID_DEFAULT == THYROID_SHARING_DIVERSITY09
The U-value is 290. The distribution is approximately normal. Therefore, the Z-value can be used.
The Z-Score is -0.4269. The p-value is 0.6672. The result is not significant at p <= 0.05.

THYROID_DEFAULT == THYROID_SHARING_DIVERSITY10
The U-value is 312. The distribution is approximately normal. Therefore, the Z-value can be used.
The Z-Score is 0. The p-value is 1. The result is not significant at p <= 0.05.

Result: Without pareto all balances between fitness sharing and the raw fitness have insignificant
differences, so it seems fitness sharing (as it is implemented here) is useless without pareto.

### COMPARISON REGARDING PROGRAM SIZE (with and without pareto)

THYROID_DEFAULT == THYROID_MAX_INSTRUCTIONS40
The U-value is 308.5. The distribution is approximately normal. Therefore, the Z-value can be used.
The Z-Score is -0.0679. The p-value is 0.9442. The result is not significant at p <= 0.05.

THYROID_WITH_PARETOS == THYROID_WITH_PARETOS_MAX_INSTRUCTIONS40
The U-value is 294. The distribution is approximately normal. Therefore, the Z-value can be used.
The Z-Score is 0.3493. The p-value is 0.72634. The result is not significant at p <= 0.05.

Result: For this dataset a max instruction of 20 seems to be obtaining good enough results in less 
runtime.

### COMPARISON REGARDING MORE REGISTERS (with and without pareto)

THYROID_DEFAULT ? THYROID_REGISTERS2
...

THYROID_WITH_PARETOS ? THYROID_WITH_PARETOS_REGISTERS2
...

### COMPARISON REGARDING DIVERSITY FOR MORE GENERATIONS (WITH PARETO)


### COMPARISON REGARDING DIVERSITY FOR MORE GENERATIONS (WITHOUT PARETO)


### COMPARISON REGARDING GENOTYPE DIVERSITY FOR OTHER VALUES OF K

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
            'genotype': False,
            'fitness_sharing': False,
        },
        'diversity_configs': { # p_value is with how much strenght this diversity metric will be applied to the fitness
            'genotype': {
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
THYROID_WITH_PARETOS_GENOTYPE_DIVERSITY03['advanced_training_parameters']['diversity']['genotype'] = True
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
THYROID_WITH_PARETOS_GENOTYPE_DIVERSITY05['advanced_training_parameters']['diversity']['genotype'] = True
THYROID_WITH_PARETOS_GENOTYPE_DIVERSITY05['advanced_training_parameters']['diversity_configs']['genotype']['p_value'] = 0.5
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
THYROID_WITH_PARETOS_GENOTYPE_DIVERSITY02['advanced_training_parameters']['diversity']['genotype'] = True
THYROID_WITH_PARETOS_GENOTYPE_DIVERSITY02['advanced_training_parameters']['diversity_configs']['genotype']['p_value'] = 0.2
"""
#################### OVERALL RESULTS ####################

Test Score per Run: [0.93219, 0.88073, 0.87471, 0.57436, 0.98049, 0.97506, 0.97102, 0.9656, 0.8846, 0.96006, 0.85949, 0.87366, 0.90514, 0.94234, 0.94061, 0.88814, 0.97473, 0.903, 0.90579, 0.9514, 0.77317, 0.90334, 0.88747, 0.93206, 0.91544]
mean: 0.90218
std. deviation: 0.08124
best run: 5

Train Score per Generation across Runs:
mean: [0.49766, 0.70966, 0.76666, 0.78866, 0.79, 0.83433, 0.83833]
std. deviation: [0.10618, 0.09142, 0.0776, 0.07183, 0.0801, 0.06945, 0.06716]

Test Score per Generation across Runs:
mean: [0.49462, 0.73093, 0.82468, 0.84466, 0.8655, 0.89799, 0.90218]
std. deviation: [0.1052, 0.10754, 0.10977, 0.09601, 0.09265, 0.09125, 0.08124]

Mean Diversity per Generation across Runs (genotype_diversity):
mean: [1.0, 0.79948, 0.79006, 0.77074, 0.77799, 0.7809, 0.76476]
std. deviation: [0.0, 0.03173, 0.03385, 0.03367, 0.02883, 0.03074, 0.03303]

Finished execution, total elapsed time: 17602.50801 secs (mean: 704.10032, std: 70.47219)
"""

THYROID_WITH_PARETOS_GENOTYPE_DIVERSITY01 = copy.deepcopy(THYROID_WITH_PARETOS)
THYROID_WITH_PARETOS_GENOTYPE_DIVERSITY01['advanced_training_parameters']['diversity']['genotype'] = True
THYROID_WITH_PARETOS_GENOTYPE_DIVERSITY01['advanced_training_parameters']['diversity_configs']['genotype']['p_value'] = 0.1
"""
#################### OVERALL RESULTS ####################

Test Score per Run: [0.97677, 0.95037, 0.86553, 0.92353, 0.98127, 0.88952, 0.93441, 0.97064, 0.96159, 0.95841, 0.92458, 0.87039, 0.9405, 0.93123, 0.94219, 0.89178, 0.93791, 0.90012, 0.87424, 0.96627, 0.94067, 0.95834, 0.97965, 0.94995, 0.90413]
mean: 0.93295
std. deviation: 0.03432
best run: 5

Train Score per Generation across Runs:
mean: [0.49766, 0.72166, 0.789, 0.81566, 0.83733, 0.84033, 0.852]
std. deviation: [0.10618, 0.06629, 0.07504, 0.07627, 0.06245, 0.05862, 0.05603]

Test Score per Generation across Runs:
mean: [0.49462, 0.72982, 0.85119, 0.88694, 0.89596, 0.90877, 0.93296]
std. deviation: [0.1052, 0.10673, 0.09079, 0.06712, 0.07028, 0.04834, 0.03432]

Mean Diversity per Generation across Runs (genotype_diversity):
mean: [1.0, 0.76835, 0.76744, 0.7512, 0.7438, 0.73545, 0.7359]
std. deviation: [0.0, 0.02896, 0.0352, 0.02625, 0.03494, 0.02837, 0.03182]

Finished execution, total elapsed time: 17851.7231 secs (mean: 714.06892, std: 77.98048)
"""

THYROID_WITH_PARETOS_SHARING_DIVERSITY03 = copy.deepcopy(THYROID_WITH_PARETOS)
THYROID_WITH_PARETOS_SHARING_DIVERSITY03['advanced_training_parameters']['diversity']['fitness_sharing'] = True
"""
#################### OVERALL RESULTS ####################

Test Score per Run: [0.9734, 0.98358, 0.96354, 0.95897, 0.88154, 0.97996, 0.96133, 0.8797, 0.94978, 0.9659, 0.88493, 0.97592, 0.94911, 0.93189, 0.97346, 0.95418, 0.94775, 0.82829, 0.99024, 0.98148, 0.98101, 0.95538, 0.96959, 0.97608, 0.96759]
mean: 0.95058
std. deviation: 0.0392
best run: 19

Train Score per Generation across Runs:
mean: [0.49733, 0.75033, 0.82266, 0.85266, 0.866, 0.87033, 0.88866]
std. deviation: [0.10663, 0.08992, 0.0761, 0.08088, 0.07302, 0.07898, 0.05631]

Test Score per Generation across Runs:
mean: [0.49458, 0.76484, 0.85617, 0.88898, 0.92867, 0.93608, 0.95058]
std. deviation: [0.10524, 0.11166, 0.10551, 0.09358, 0.05031, 0.04725, 0.0392]

Mean Diversity per Generation across Runs (fitness_sharing_diversity):
mean: [0.01202, 0.01216, 0.01217, 0.01219, 0.01219, 0.0122, 0.01221]
std. deviation: [1e-05, 3e-05, 7e-05, 5e-05, 6e-05, 6e-05, 7e-05]

Finished execution, total elapsed time: 17108.0315 secs (mean: 684.32126, std: 86.57374)
"""

THYROID_WITH_PARETOS_SHARING_DIVERSITY05 = copy.deepcopy(THYROID_WITH_PARETOS)
THYROID_WITH_PARETOS_SHARING_DIVERSITY05['advanced_training_parameters']['diversity']['fitness_sharing'] = True
THYROID_WITH_PARETOS_SHARING_DIVERSITY05['advanced_training_parameters']['diversity_configs']['fitness_sharing']['p_value'] = 0.5
"""
#################### OVERALL RESULTS ####################

Test Score per Run: [0.88965, 0.88793, 0.96687, 0.93612, 0.88313, 0.98363, 0.96564, 0.97571, 0.95314, 0.68527, 0.88556, 0.87117, 0.91443, 0.87072, 0.71296, 0.83828, 0.93955, 0.91597, 0.8668, 0.91159, 0.97308, 0.8925, 0.97818, 0.87346, 0.92617]
mean: 0.8999
std. deviation: 0.07187
best run: 6

Train Score per Generation across Runs:
mean: [0.49433, 0.754, 0.81033, 0.84399, 0.83966, 0.83966, 0.848]
std. deviation: [0.10991, 0.07867, 0.05078, 0.04918, 0.05663, 0.06464, 0.05784]

Test Score per Generation across Runs:
mean: [0.49112, 0.78544, 0.86608, 0.88203, 0.89385, 0.89819, 0.8999]
std. deviation: [0.10893, 0.10353, 0.06243, 0.05973, 0.06379, 0.07313, 0.07186]

Mean Diversity per Generation across Runs (fitness_sharing_diversity):
mean: [0.01202, 0.01215, 0.01217, 0.01218, 0.01218, 0.01218, 0.01219]
std. deviation: [1e-05, 5e-05, 4e-05, 6e-05, 5e-05, 5e-05, 5e-05]

Finished execution, total elapsed time: 17706.12629 secs (mean: 708.24505, std: 110.4064)
"""

THYROID_WITH_PARETOS_SHARING_DIVERSITY02 = copy.deepcopy(THYROID_WITH_PARETOS)
THYROID_WITH_PARETOS_SHARING_DIVERSITY02['advanced_training_parameters']['diversity']['fitness_sharing'] = True
THYROID_WITH_PARETOS_SHARING_DIVERSITY02['advanced_training_parameters']['diversity_configs']['fitness_sharing']['p_value'] = 0.2
"""
#################### OVERALL RESULTS ####################

Test Score per Run: [0.91304, 0.92354, 0.94423, 0.86432, 0.91015, 0.93657, 0.91441, 0.88044, 0.9754, 0.9776, 0.95282, 0.93024, 0.8923, 0.9586, 0.95629, 0.96564, 0.98012, 0.9575, 0.95235, 0.95474, 0.97125, 0.88683, 0.92005, 0.94395, 0.96705]
mean: 0.93717
std. deviation: 0.03184
best run: 17

Train Score per Generation across Runs:
mean: [0.49766, 0.74666, 0.81433, 0.83499, 0.85466, 0.85533, 0.87333]
std. deviation: [0.10618, 0.07176, 0.05459, 0.04515, 0.0446, 0.04777, 0.04606]

Test Score per Generation across Runs:
mean: [0.49458, 0.7972, 0.87742, 0.90667, 0.91534, 0.92982, 0.93718]
std. deviation: [0.10525, 0.11565, 0.06911, 0.05174, 0.04653, 0.03472, 0.03184]

Mean Diversity per Generation across Runs (fitness_sharing_diversity):
mean: [0.01202, 0.01215, 0.01218, 0.01217, 0.01219, 0.01219, 0.0122]
std. deviation: [1e-05, 4e-05, 4e-05, 5e-05, 3e-05, 4e-05, 4e-05]

Finished execution, total elapsed time: 17254.93292 secs (mean: 690.19731, std: 76.81315)
"""

THYROID_WITH_PARETOS_SHARING_DIVERSITY04 = copy.deepcopy(THYROID_WITH_PARETOS)
THYROID_WITH_PARETOS_SHARING_DIVERSITY04['advanced_training_parameters']['diversity']['fitness_sharing'] = True
THYROID_WITH_PARETOS_SHARING_DIVERSITY04['advanced_training_parameters']['diversity_configs']['fitness_sharing']['p_value'] = 0.4
"""
#################### OVERALL RESULTS ####################

Test Score per Run: [0.97481, 0.9829, 0.96692, 0.94766, 0.91753, 0.94019, 0.98263, 0.97434, 0.94263, 0.92169, 0.88732, 0.98238, 0.95816, 0.97583, 0.95642, 0.95052, 0.93494, 0.91456, 0.90081, 0.9807, 0.97279, 0.94339, 0.9159, 0.95439, 0.96728]
mean: 0.94986
std. deviation: 0.02705
best run: 2

Train Score per Generation across Runs:
mean: [0.49566, 0.75833, 0.79866, 0.84233, 0.87766, 0.88733, 0.88966]
std. deviation: [0.10809, 0.08673, 0.07636, 0.06703, 0.04266, 0.04784, 0.04906]

Test Score per Generation across Runs:
mean: [0.49356, 0.77157, 0.8455, 0.90738, 0.94195, 0.95044, 0.94987]
std. deviation: [0.10605, 0.12858, 0.11726, 0.06499, 0.03103, 0.03172, 0.02705]

Mean Diversity per Generation across Runs (fitness_sharing_diversity):
mean: [0.01202, 0.01214, 0.01216, 0.01217, 0.01219, 0.0122, 0.01221]
std. deviation: [1e-05, 7e-05, 0.0001, 7e-05, 5e-05, 5e-05, 4e-05]

Finished execution, total elapsed time: 17322.42747 secs (mean: 692.89709, std: 81.17469)
"""

THYROID_GENOTYPE_DIVERSITY03 = copy.deepcopy(THYROID_DEFAULT)
THYROID_GENOTYPE_DIVERSITY03['advanced_training_parameters']['diversity']['genotype'] = True
"""
#################### OVERALL RESULTS ####################

Test Score per Run: [0.8806, 0.84176, 0.83299, 0.86542, 0.85606, 0.90608, 0.95884, 0.9391, 0.8601, 0.90642, 0.86637, 0.96947, 0.91196, 0.87455, 0.87927, 0.89466, 0.96022, 0.96812, 0.87479, 0.72943, 0.82859, 0.85799, 0.84419, 0.75759, 0.96301]
mean: 0.8811
std. deviation: 0.05951
best run: 12

Train Score per Generation across Runs:
mean: [0.49766, 0.74933, 0.816, 0.85466, 0.86733, 0.89266, 0.89399]
std. deviation: [0.10618, 0.0917, 0.08956, 0.08527, 0.06822, 0.0595, 0.06344]

Test Score per Generation across Runs:
mean: [0.49462, 0.74474, 0.81064, 0.85189, 0.86876, 0.87946, 0.8811]
std. deviation: [0.1052, 0.09417, 0.09663, 0.07323, 0.06966, 0.05641, 0.05951]

Mean Diversity per Generation across Runs (genotype_diversity):
mean: [1.0, 0.79603, 0.81438, 0.81919, 0.82183, 0.83259, 0.82329]
std. deviation: [0.0, 0.05028, 0.03815, 0.02897, 0.02884, 0.02544, 0.02757]

Finished execution, total elapsed time: 7440.26044 secs (mean: 297.61041, std: 58.68585)
"""

THYROID_GENOTYPE_DIVERSITY04 = copy.deepcopy(THYROID_DEFAULT)
THYROID_GENOTYPE_DIVERSITY04['advanced_training_parameters']['diversity']['genotype'] = True
THYROID_GENOTYPE_DIVERSITY04['advanced_training_parameters']['diversity_configs']['genotype']['p_value'] = 0.4
"""
#################### OVERALL RESULTS ####################

Test Score per Run: [0.89235, 0.85486, 0.84522, 0.86269, 0.87903, 0.83084, 0.90031, 0.864, 0.93333, 0.95578, 0.90269, 0.94788, 0.95503, 0.92577, 0.87117, 0.89466, 0.87654, 0.88354, 0.88773, 0.95031, 0.87862, 0.91707, 0.89466, 0.88313, 0.83384]
mean: 0.89284
std. deviation: 0.03563
best run: 10

Train Score per Generation across Runs:
mean: [0.49766, 0.691, 0.80566, 0.86233, 0.877, 0.884, 0.90533]
std. deviation: [0.10618, 0.10046, 0.09918, 0.06115, 0.0649, 0.06476, 0.04274]

Test Score per Generation across Runs:
mean: [0.49462, 0.68899, 0.79836, 0.86396, 0.87813, 0.88177, 0.89284]
std. deviation: [0.1052, 0.09461, 0.08868, 0.06319, 0.04696, 0.05888, 0.03563]

Mean Diversity per Generation across Runs (genotype_diversity):
mean: [1.0, 0.84043, 0.81249, 0.82676, 0.82027, 0.82711, 0.82404]
std. deviation: [0.0, 0.03824, 0.03176, 0.02844, 0.03064, 0.03088, 0.02617]

Finished execution, total elapsed time: 6995.9999 secs (mean: 279.83999, std: 49.42049)
"""

THYROID_SHARING_DIVERSITY03 = copy.deepcopy(THYROID_DEFAULT)
THYROID_SHARING_DIVERSITY03['advanced_training_parameters']['diversity']['fitness_sharing'] = True
"""
#################### OVERALL RESULTS ####################

Test Score per Run: [0.89466, 0.86981, 0.85396, 0.64486, 0.89466, 0.86364, 0.93142, 0.89638, 0.94886, 0.89466, 0.89466, 0.86425, 0.94722, 0.94931, 0.89466, 0.88427, 0.92494, 0.88157, 0.88957, 0.89284, 0.91174, 0.97445, 0.88385, 0.90025, 0.96626]
mean: 0.89411
std. deviation: 0.05991
best run: 22

Train Score per Generation across Runs:
mean: [0.49766, 0.78766, 0.83, 0.86366, 0.90566, 0.90366, 0.904]
std. deviation: [0.10618, 0.10506, 0.09504, 0.07283, 0.0647, 0.05754, 0.066]

Test Score per Generation across Runs:
mean: [0.49462, 0.77608, 0.8193, 0.85698, 0.88376, 0.89452, 0.89411]
std. deviation: [0.1052, 0.105, 0.1039, 0.07966, 0.06131, 0.05758, 0.05991]

Mean Diversity per Generation across Runs (fitness_sharing_diversity):
mean: [0.01202, 0.01148, 0.01181, 0.01199, 0.01204, 0.01211, 0.01209]
std. deviation: [1e-05, 0.00113, 0.00081, 0.00056, 0.00044, 0.00018, 0.00022]

Finished execution, total elapsed time: 7499.67609 secs (mean: 299.98704, std: 89.11312)
"""

THYROID_SHARING_DIVERSITY04 = copy.deepcopy(THYROID_DEFAULT)
THYROID_SHARING_DIVERSITY04['advanced_training_parameters']['diversity']['fitness_sharing'] = True
THYROID_SHARING_DIVERSITY04['advanced_training_parameters']['diversity_configs']['fitness_sharing']['p_value'] = 0.4
"""
#################### OVERALL RESULTS ####################

Test Score per Run: [0.88849, 0.91817, 0.97135, 0.90031, 0.89009, 0.87352, 0.9234, 0.90667, 0.8655, 0.89466, 0.9166, 0.97996, 0.8746, 0.95809, 0.88131, 0.8891, 0.85531, 0.962, 0.89466, 0.94041, 0.91564, 0.86787, 0.88397, 0.95963, 0.9505]
mean: 0.91047
std. deviation: 0.03562
best run: 12

Train Score per Generation across Runs:
mean: [0.49733, 0.76933, 0.838, 0.88599, 0.907, 0.91233, 0.91499]
std. deviation: [0.10642, 0.1168, 0.0962, 0.08071, 0.06144, 0.05598, 0.04654]

Test Score per Generation across Runs:
mean: [0.49448, 0.74947, 0.82125, 0.87159, 0.88977, 0.89895, 0.91047]
std. deviation: [0.10523, 0.11444, 0.09445, 0.08183, 0.05708, 0.05901, 0.03562]

Mean Diversity per Generation across Runs (fitness_sharing_diversity):
mean: [0.01202, 0.01182, 0.01182, 0.01211, 0.01215, 0.01216, 0.01211]
std. deviation: [1e-05, 0.00065, 0.00082, 0.00011, 7e-05, 8e-05, 0.00017]

Finished execution, total elapsed time: 6811.79699 secs (mean: 272.47187, std: 85.85712)
"""

THYROID_GENOTYPE_DIVERSITY05 = copy.deepcopy(THYROID_DEFAULT)
THYROID_GENOTYPE_DIVERSITY05['advanced_training_parameters']['diversity']['genotype'] = True
THYROID_GENOTYPE_DIVERSITY05['advanced_training_parameters']['diversity_configs']['genotype']['p_value'] = 0.5
"""
#################### OVERALL RESULTS ####################

Test Score per Run: [0.88773, 0.85788, 0.81675, 0.85384, 0.8628, 0.88693, 0.84737, 0.86787, 0.82894, 0.82052, 0.85693, 0.82235, 0.87338, 0.91689, 0.90577, 0.89466, 0.89256, 0.86133, 0.88773, 0.85765, 0.81134, 0.8584, 0.88671, 0.85537, 0.93692]
mean: 0.86594
std. deviation: 0.03115
best run: 25

Train Score per Generation across Runs:
mean: [0.49766, 0.677, 0.76366, 0.79866, 0.857, 0.863, 0.87366]
std. deviation: [0.10618, 0.1025, 0.11476, 0.09558, 0.06878, 0.05602, 0.0435]

Test Score per Generation across Runs:
mean: [0.49462, 0.6646, 0.75239, 0.79827, 0.84853, 0.85878, 0.86595]
std. deviation: [0.1052, 0.10856, 0.11571, 0.09525, 0.06429, 0.05861, 0.03116]

Mean Diversity per Generation across Runs (genotype_diversity):
mean: [1.0, 0.84879, 0.84014, 0.83727, 0.84414, 0.84381, 0.84674]
std. deviation: [0.0, 0.03765, 0.02718, 0.02991, 0.02498, 0.02102, 0.02165]

Finished execution, total elapsed time: 6835.48363 secs (mean: 273.41934, std: 61.04908)
"""

THYROID_SHARING_DIVERSITY05 = copy.deepcopy(THYROID_DEFAULT)
THYROID_SHARING_DIVERSITY05['advanced_training_parameters']['diversity']['fitness_sharing'] = True
THYROID_SHARING_DIVERSITY05['advanced_training_parameters']['diversity_configs']['fitness_sharing']['p_value'] = 0.5
"""
#################### OVERALL RESULTS ####################

Test Score per Run: [0.89466, 0.94507, 0.96626, 0.7523, 0.87668, 0.83945, 0.90404, 0.86163, 0.71873, 0.98711, 0.90215, 0.74251, 0.95914, 0.9798, 0.87917, 0.89466, 0.96968, 0.92012, 0.88908, 0.96775, 0.88882, 0.9608, 0.93912, 0.90434, 0.89386]
mean: 0.89747
std. deviation: 0.07064
best run: 10

Train Score per Generation across Runs:
mean: [0.49733, 0.75666, 0.81499, 0.86399, 0.89099, 0.90633, 0.91933]
std. deviation: [0.10642, 0.10705, 0.08925, 0.07894, 0.06806, 0.06957, 0.05961]

Test Score per Generation across Runs:
mean: [0.49448, 0.74416, 0.79867, 0.85271, 0.88693, 0.89116, 0.89748]
std. deviation: [0.10523, 0.11124, 0.09931, 0.08376, 0.08046, 0.07942, 0.07064]

Mean Diversity per Generation across Runs (fitness_sharing_diversity):
mean: [0.01202, 0.01174, 0.01195, 0.01197, 0.0121, 0.01212, 0.01217]
std. deviation: [1e-05, 0.00081, 0.00034, 0.0005, 0.00017, 0.00018, 0.00016]

Finished execution, total elapsed time: 7530.66866 secs (mean: 301.22674, std: 83.51817)
"""

THYROID_GENOTYPE_DIVERSITY06 = copy.deepcopy(THYROID_DEFAULT)
THYROID_GENOTYPE_DIVERSITY06['advanced_training_parameters']['diversity']['genotype'] = True
THYROID_GENOTYPE_DIVERSITY06['advanced_training_parameters']['diversity_configs']['genotype']['p_value'] = 0.6
"""
#################### OVERALL RESULTS ####################

Test Score per Run: [0.88773, 0.64663, 0.85173, 0.88982, 0.89466, 0.86387, 0.64663, 0.80544, 0.8476, 0.62568, 0.64663, 0.84185, 0.84871, 0.33311, 0.88261, 0.91616, 0.90871, 0.84457, 0.88773, 0.90234, 0.88128, 0.85945, 0.63458, 0.8802, 0.86416]
mean: 0.80367
std. deviation: 0.13518
best run: 16

Train Score per Generation across Runs:
mean: [0.49766, 0.61333, 0.68266, 0.73566, 0.74833, 0.81166, 0.81033]
std. deviation: [0.10618, 0.11782, 0.12997, 0.13442, 0.13646, 0.11556, 0.13577]

Test Score per Generation across Runs:
mean: [0.49462, 0.60566, 0.68523, 0.72366, 0.7442, 0.81085, 0.80368]
std. deviation: [0.1052, 0.10881, 0.1271, 0.13533, 0.14082, 0.10578, 0.13518]

Mean Diversity per Generation across Runs (genotype_diversity):
mean: [1.0, 0.88, 0.86532, 0.85921, 0.85866, 0.86278, 0.8587]
std. deviation: [0.0, 0.03664, 0.02852, 0.02772, 0.0286, 0.03183, 0.02291]

Finished execution, total elapsed time: 6333.72189 secs (mean: 253.34887, std: 58.74377)
"""

THYROID_SHARING_DIVERSITY06 = copy.deepcopy(THYROID_DEFAULT)
THYROID_SHARING_DIVERSITY06['advanced_training_parameters']['diversity']['fitness_sharing'] = True
THYROID_SHARING_DIVERSITY06['advanced_training_parameters']['diversity_configs']['fitness_sharing']['p_value'] = 0.6
"""
#################### OVERALL RESULTS ####################

Test Score per Run: [0.89466, 0.87316, 0.97243, 0.89466, 0.9001, 0.65246, 0.93698, 0.95091, 0.72753, 0.91988, 0.96639, 0.88882, 0.86702, 0.94538, 0.85252, 0.89267, 0.92503, 0.95121, 0.89466, 0.87102, 0.9754, 0.87164, 0.95918, 0.96849, 0.88773]
mean: 0.89759
std. deviation: 0.07216
best run: 21

Train Score per Generation across Runs:
mean: [0.49666, 0.78633, 0.873, 0.87633, 0.90733, 0.91, 0.90633]
std. deviation: [0.10739, 0.11082, 0.09569, 0.08758, 0.06754, 0.05421, 0.06281]

Test Score per Generation across Runs:
mean: [0.49248, 0.7775, 0.84941, 0.86337, 0.88598, 0.89054, 0.8976]
std. deviation: [0.10777, 0.11426, 0.09474, 0.09654, 0.0698, 0.0674, 0.07216]

Mean Diversity per Generation across Runs (fitness_sharing_diversity):
mean: [0.01202, 0.01199, 0.01215, 0.01207, 0.01211, 0.01206, 0.01214]
std. deviation: [1e-05, 0.00027, 0.00011, 0.00023, 0.00021, 0.00028, 0.0001]

Finished execution, total elapsed time: 7343.52135 secs (mean: 293.74085, std: 97.699)
"""

THYROID_SHARING_DIVERSITY07 = copy.deepcopy(THYROID_DEFAULT)
THYROID_SHARING_DIVERSITY07['advanced_training_parameters']['diversity']['fitness_sharing'] = True
THYROID_SHARING_DIVERSITY07['advanced_training_parameters']['diversity_configs']['fitness_sharing']['p_value'] = 0.7
"""
#################### OVERALL RESULTS ####################

Test Score per Run: [0.89466, 0.85219, 0.89788, 0.94418, 0.85554, 0.85949, 0.91752, 0.89653, 0.94055, 0.91376, 0.7359, 0.64715, 0.64663, 0.89466, 0.89466, 0.89267, 0.88354, 0.86837, 0.9206, 0.97379, 0.9416, 0.93322, 0.88967, 0.91543, 0.87569]
mean: 0.87543
std. deviation: 0.08025
best run: 20

Train Score per Generation across Runs:
mean: [0.49633, 0.76066, 0.83433, 0.855, 0.87933, 0.88766, 0.89466]
std. deviation: [0.10767, 0.11947, 0.09903, 0.09312, 0.07699, 0.07468, 0.08484]

Test Score per Generation across Runs:
mean: [0.48978, 0.7437, 0.82295, 0.83837, 0.8664, 0.87518, 0.87543]
std. deviation: [0.11035, 0.12828, 0.09695, 0.09364, 0.07626, 0.07252, 0.08025]

Mean Diversity per Generation across Runs (fitness_sharing_diversity):
mean: [0.01202, 0.01192, 0.012, 0.01208, 0.01213, 0.01212, 0.01215]
std. deviation: [1e-05, 0.00035, 0.00034, 0.00013, 9e-05, 0.00014, 0.0001]

Finished execution, total elapsed time: 7578.76377 secs (mean: 303.15055, std: 90.7192)
"""

THYROID_SHARING_DIVERSITY08 = copy.deepcopy(THYROID_DEFAULT)
THYROID_SHARING_DIVERSITY08['advanced_training_parameters']['diversity']['fitness_sharing'] = True
THYROID_SHARING_DIVERSITY08['advanced_training_parameters']['diversity_configs']['fitness_sharing']['p_value'] = 0.8
"""
#################### OVERALL RESULTS ####################

Test Score per Run: [0.89466, 0.97157, 0.92811, 0.86981, 0.93104, 0.95577, 0.89471, 0.94771, 0.9375, 0.82867, 0.89384, 0.89466, 0.96302, 0.89466, 0.8609, 0.8794, 0.84089, 0.95901, 0.89466, 0.92733, 0.97215, 0.66839, 0.75032, 0.74233, 0.89466]
mean: 0.88783
std. deviation: 0.07373
best run: 21

Train Score per Generation across Runs:
mean: [0.49633, 0.72533, 0.807, 0.83499, 0.86966, 0.86833, 0.90366]
std. deviation: [0.10767, 0.15021, 0.1034, 0.09231, 0.09094, 0.10118, 0.07295]

Test Score per Generation across Runs:
mean: [0.48978, 0.70915, 0.80114, 0.82421, 0.84397, 0.85173, 0.88783]
std. deviation: [0.11035, 0.1421, 0.10511, 0.08885, 0.09607, 0.09728, 0.07373]

Mean Diversity per Generation across Runs (fitness_sharing_diversity):
mean: [0.01202, 0.01193, 0.012, 0.01206, 0.01207, 0.01201, 0.01211]
std. deviation: [1e-05, 0.00036, 0.00037, 0.00021, 0.00028, 0.00032, 0.00016]

Finished execution, total elapsed time: 7592.03471 secs (mean: 303.68138, std: 106.43692)
"""

THYROID_SHARING_DIVERSITY09 = copy.deepcopy(THYROID_DEFAULT)
THYROID_SHARING_DIVERSITY09['advanced_training_parameters']['diversity']['fitness_sharing'] = True
THYROID_SHARING_DIVERSITY09['advanced_training_parameters']['diversity_configs']['fitness_sharing']['p_value'] = 0.9
"""
#################### OVERALL RESULTS ####################

Test Score per Run: [0.89466, 0.96367, 0.89937, 0.89466, 0.89466, 0.87259, 0.94372, 0.90276, 0.79882, 0.88459, 0.92589, 0.9383, 0.94016, 0.95765, 0.81288, 0.96386, 0.65387, 0.89466, 0.90428, 0.95675, 0.64961, 0.8738, 0.86199, 0.84642, 0.90223]
mean: 0.88127
std. deviation: 0.0797
best run: 16

Train Score per Generation across Runs:
mean: [0.49033, 0.70666, 0.81099, 0.83966, 0.86366, 0.88566, 0.89233]
std. deviation: [0.11371, 0.15038, 0.11694, 0.10675, 0.09198, 0.09505, 0.08663]

Test Score per Generation across Runs:
mean: [0.48482, 0.70006, 0.79872, 0.82444, 0.84674, 0.87067, 0.88127]
std. deviation: [0.11454, 0.1425, 0.11152, 0.10672, 0.0959, 0.08489, 0.0797]

Mean Diversity per Generation across Runs (fitness_sharing_diversity):
mean: [0.01202, 0.01198, 0.01211, 0.01211, 0.01214, 0.01217, 0.01217]
std. deviation: [1e-05, 0.00039, 9e-05, 0.00016, 9e-05, 9e-05, 9e-05]

Finished execution, total elapsed time: 6935.35173 secs (mean: 277.41406, std: 88.32331)
"""

THYROID_SHARING_DIVERSITY10 = copy.deepcopy(THYROID_DEFAULT)
THYROID_SHARING_DIVERSITY10['advanced_training_parameters']['diversity']['fitness_sharing'] = True
THYROID_SHARING_DIVERSITY10['advanced_training_parameters']['diversity_configs']['fitness_sharing']['p_value'] = 1.0
"""
#################### OVERALL RESULTS ####################

Test Score per Run: [0.65586, 0.86302, 0.93127, 0.56096, 0.88317, 0.64663, 0.95976, 0.64485, 0.93175, 0.93077, 0.72893, 0.96166, 0.9538, 0.90621, 0.93639, 0.75723, 0.96117, 0.96375, 0.86071, 0.60098, 0.84101, 0.97578, 0.94138, 0.96592, 0.90386]
mean: 0.85067
std. deviation: 0.13006
best run: 22

Train Score per Generation across Runs:
mean: [0.486, 0.74499, 0.813, 0.84866, 0.87966, 0.86, 0.86666]
std. deviation: [0.1163, 0.16122, 0.12108, 0.10864, 0.10317, 0.1211, 0.12909]

Test Score per Generation across Runs:
mean: [0.484, 0.73297, 0.79484, 0.82622, 0.86067, 0.83874, 0.85067]
std. deviation: [0.11461, 0.15254, 0.1201, 0.12136, 0.09935, 0.12007, 0.13006]

Mean Diversity per Generation across Runs (fitness_sharing_diversity):
mean: [0.01202, 0.01218, 0.0122, 0.01221, 0.01222, 0.01223, 0.01223]
std. deviation: [1e-05, 5e-05, 5e-05, 5e-05, 4e-05, 4e-05, 4e-05]

Finished execution, total elapsed time: 6979.74256 secs (mean: 279.1897, std: 78.45992)
"""

THYROID_MAX_INSTRUCTIONS40 = copy.deepcopy(THYROID_DEFAULT)
THYROID_MAX_INSTRUCTIONS40['training_parameters']['program_size']['max'] = 40
"""
#################### OVERALL RESULTS ####################

Test Score per Run: [0.97661, 0.89466, 0.89455, 0.88542, 0.65366, 0.90831, 0.85835, 0.88786, 0.87316, 0.88919, 0.7122, 0.97808, 0.93718, 0.87244, 0.92218, 0.91411, 0.85571, 0.87191, 0.86986, 0.93752, 0.86839, 0.93777, 0.86616, 0.88222, 0.89392]
mean: 0.88165
std. deviation: 0.06764
best run: 12

Train Score per Generation across Runs:
mean: [0.54233, 0.82433, 0.843, 0.89166, 0.88366, 0.89566, 0.89766]
std. deviation: [0.07256, 0.11537, 0.11052, 0.0667, 0.08132, 0.06464, 0.06902]

Test Score per Generation across Runs:
mean: [0.53451, 0.79538, 0.82735, 0.86887, 0.87145, 0.87983, 0.88166]
std. deviation: [0.07021, 0.11419, 0.10156, 0.0679, 0.07048, 0.06889, 0.06764]

Finished execution, total elapsed time: 16533.10621 secs (mean: 661.32424, std: 174.642)
"""

THYROID_WITH_PARETOS_MAX_INSTRUCTIONS40 = copy.deepcopy(THYROID_WITH_PARETOS)
THYROID_WITH_PARETOS_MAX_INSTRUCTIONS40['training_parameters']['program_size']['max'] = 40
"""
#################### OVERALL RESULTS ####################

Test Score per Run: [0.98223, 0.96887, 0.90371, 0.98232, 0.97226, 0.95214, 0.94654, 0.98593, 0.96368, 0.76645, 0.96187, 0.90572, 0.9165, 0.74196, 0.85634, 0.95395, 0.97335, 0.9754, 0.95854, 0.95506, 0.93794, 0.94148, 0.91306, 0.91946, 0.84695]
mean: 0.92726
std. deviation: 0.0623
best run: 8

Train Score per Generation across Runs:
mean: [0.54233, 0.78233, 0.836, 0.85033, 0.868, 0.87733, 0.88233]
std. deviation: [0.07256, 0.07361, 0.0634, 0.06597, 0.06353, 0.05965, 0.05973]

Test Score per Generation across Runs:
mean: [0.53451, 0.81498, 0.87786, 0.89318, 0.91023, 0.91964, 0.92727]
std. deviation: [0.07021, 0.08698, 0.0854, 0.07631, 0.07172, 0.06288, 0.0623]

Finished execution, total elapsed time: 27447.74921 secs (mean: 1097.90996, std: 137.78078)
"""

THYROID_REGISTERS2 = copy.deepcopy(THYROID_DEFAULT)
THYROID_REGISTERS2['advanced_training_parameters']['extra_registers'] = 2
"""

"""

THYROID_WITH_PARETOS_REGISTERS2 = copy.deepcopy(THYROID_WITH_PARETOS)
THYROID_WITH_PARETOS_REGISTERS2['advanced_training_parameters']['extra_registers'] = 2
"""

"""