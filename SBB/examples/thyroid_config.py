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

THYROID_WITH_PARETOS == THYROID_WITH_PARETOS_SHARING_DIVERSITY03
The U-value is 245. The distribution is approximately normal. Therefore, the Z-value can be used.
The Z-Score is -1.3. The p-value is 0.1936. The result is not significant at p <= 0.05.

THYROID_WITH_PARETOS > THYROID_WITH_PARETOS_SHARING_DIVERSITY05
The U-value is 194. The distribution is approximately normal. Therefore, the Z-value can be used.
The Z-Score is 2.2895. The p-value is 0.02202. The result is significant at p <= 0.05.

THYROID_WITH_PARETOS == THYROID_WITH_PARETOS_SHARING_DIVERSITY02
The U-value is 278. The distribution is approximately normal. Therefore, the Z-value can be used.
The Z-Score is 0.6597. The p-value is 0.50926. The result is not significant at p <= 0.05.

THYROID_WITH_PARETOS == THYROID_WITH_PARETOS_SHARING_DIVERSITY04
The U-value is 277. The distribution is approximately normal. Therefore, the Z-value above can be used.
The Z-Score is -0.6791. The p-value is 0.4965. The result is not significant at p <= 0.05.

Result: Fitness sharing wasn't very useful for this dataset and configuration, for p values equal or 
lower than 0.4 the diversity didn't decrease the performance. Further tests, for more generations, may 
improve the performance.


### COMPARISON REGARDING GENOTYPE DIVERSITY WITHOUT PARETO


### COMPARISON REGARDING FITNESS SHARING DIVERSITY WITHOUT PARETO


### COMPARISON REGARDING PROGRAM SIZE


### COMPARISON REGARDING DIVERSITY FOR MORE GENERATIONS


### COMPARISON REGARDING MORE REGISTERS


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
THYROID_WITH_PARETOS_GENOTYPE_DIVERSITY01['advanced_training_parameters']['diversity']['genotype_fitness_maintanance'] = True
THYROID_WITH_PARETOS_GENOTYPE_DIVERSITY01['advanced_training_parameters']['diversity_configs']['genotype_fitness_maintanance']['p_value'] = 0.1
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
THYROID_GENOTYPE_DIVERSITY03['advanced_training_parameters']['diversity']['genotype_fitness_maintanance'] = True
"""

"""

THYROID_SHARING_DIVERSITY03 = copy.deepcopy(THYROID_DEFAULT)
THYROID_SHARING_DIVERSITY03['advanced_training_parameters']['diversity']['fitness_sharing'] = True
"""

"""