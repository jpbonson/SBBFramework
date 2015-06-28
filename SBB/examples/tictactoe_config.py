import copy

"""
##### Results using Mann-Whitney U-Test (http://www.socscistatistics.com/tests/mannwhitney/Default2.aspx):

### COMPARISON REGARDING STEP2 IN INITIALIZATION

TICTACTOE_DEFAULT == TICTACTOE_WITH_INIT2
The U-value is 255.5. The distribution is approximately normal. Therefore, the Z-value can be used.
The Z-Score is -1.0963. The p-value is 0.27134. The result is not significant at p <= 0.05.

Results: Increases runtime without increasing performance.

### COMPARISON REGARDING 1000 GENS

TICTACTOE_DEFAULT < TICTACTOE_MORE_GENERATIONS
The U-value is 197. The distribution is approximately normal. Therefore, the Z-value can be used.
The Z-Score is -2.2313. The p-value is 0.02574. The result is significant at p <= 0.05.

Results: From 500 to 1000 generations the default configuration improved from (mean: 0.70573
std. deviation: 0.02134) to (mean: 0.71866 std. deviation: 0.01797). So it indeed improved but 
the extra runtime wasn't really worth it.

### COMPARISON REGARDING PARETO

TICTACTOE_DEFAULT < TICTACTOE_WITH_PARETOS
The U-value is 143.5. The distribution is approximately normal. Therefore, the Z-value can be used.
The Z-Score is -3.2694. The p-value is 0.00108. The result is significant at p <= 0.05.

TICTACTOE_DEFAULT == TICTACTOE_WITH_PARETO_FOR_TEAM_ONLY
The U-value is 251.5. The distribution is approximately normal. Therefore, the Z-value can be used.
The Z-Score is -1.1739. The p-value is 0.242. The result is not significant at p <= 0.05.

TICTACTOE_DEFAULT < TICTACTOE_WITH_PARETO_FOR_POINT_ONLY
The U-value is 180.5. The distribution is approximately normal. Therefore, the Z-value can be used.
The Z-Score is -2.5515. The p-value is 0.01078. The result is significant at p <= 0.05.

TICTACTOE_WITH_PARETOS > TICTACTOE_WITH_PARETO_FOR_TEAM_ONLY
The U-value is 193. The distribution is approximately normal. Therefore, the Z-value can be used.
The Z-Score is 2.3089. The p-value is 0.02088. The result is significant at p <= 0.05.

TICTACTOE_WITH_PARETOS == TICTACTOE_WITH_PARETO_FOR_POINT_ONLY
The U-value is 294. The distribution is approximately normal. Therefore, the Z-value can be used.
The Z-Score is 0.3493. The p-value is 0.72634. The result is not significant at p <= 0.05.

TICTACTOE_WITH_PARETO_FOR_TEAM_ONLY == TICTACTOE_WITH_PARETO_FOR_POINT_ONLY
The U-value is 221. The distribution is approximately normal. Therefore, the Z-value can be used.
The Z-Score is -1.7657. The p-value is 0.07672. The result is not significant at p <= 0.05.

Results: The pareto for the teams didn't improved the performance significantly, while the pareto 
for the points improved the performance. It is worth noting that the opposite occured for the 
thyroid dataset. Since the runtime didn't change significantly, I think it is worth to keep both 
paretos to try to improve results.

### COMPARISON REGARDING MORE REGISTERS

TICTACTOE_DEFAULT == TICTACTOE_MORE_REGISTERS2
Got the exact same results.

### COMPARISON REGARDING GENOTYPE DIVERSITY

TICTACTOE_WITH_PARETOS > TICTACTOE_WITH_PARETO_GENOTYPE_DIVERSITY03
The U-value is 113.5. The distribution is approximately normal. Therefore, the Z-value can be used.
The Z-Score is 3.8515. The p-value is 0.00012. The result is significant at p <= 0.05.

### COMPARISON REGARDING FITNESS SHARING DIVERSITY


"""

TICTACTOE_DEFAULT = {
    'task': 'reinforcement',
    'reinforcement_parameters': { # only used if 'task' is 'reinforcement'
        'environment': 'tictactoe', # edit _initialize_environment() in SBB and RESTRICTIONS['environment_types'] to add new environments (they must implement DefaultEnvironment)
        'validation_population': 100, # at a validated generation, all the teams with be tested against this population, the best one is the champion
        'champion_population': 1000, # at a validated generation, these are the points the champion team will play against to obtain the metrics
        'opponents_pool': 'only_coded',
        'balanced_opponent_populations': True, # if false, the opponent populations will be swapped instead of mixed
        'hall_of_fame': {
            'enabled': False,
            'use_genotype_diversity': True, # if False, use the fitness as the criteria to remove teams when the Hall of Fame is full
        },
        'debug_matches': False, # use this option to debug
    },

    'training_parameters': {
        'runs_total': 25,
        'generations_total': 500,
        'validate_after_each_generation': 50,
        'populations': {
            'teams': 100,
            'points': 60,
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
            'max': 18,
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
#################### OVERALL RESULTS #################### (rerun, to get the runtime)

Test Score per Run: [0.73975, 0.70775, 0.7075, 0.72975, 0.707, 0.71475, 0.69675, 0.71725, 0.72125, 0.67475, 0.7, 0.6975, 0.69225, 0.7485, 0.6775, 0.6655, 0.71075, 0.69875, 0.70625, 0.70725, 0.7095, 0.716, 0.687, 0.74425, 0.66575]
mean: 0.70573
std. deviation: 0.02134
best run: 14

Train Score per Generation across Runs:
mean: [0.39883, 0.64133, 0.669, 0.693, 0.69566, 0.69849, 0.70416, 0.70083, 0.70216, 0.71116, 0.712]
std. deviation: [0.04157, 0.04189, 0.037, 0.03633, 0.03722, 0.02712, 0.02988, 0.03636, 0.02944, 0.0257, 0.03812]

Test Score per Generation across Runs:
mean: [0.4018, 0.62317, 0.66476, 0.68204, 0.68957, 0.69345, 0.69827, 0.70035, 0.70354, 0.70459, 0.70573]
std. deviation: [0.01183, 0.01776, 0.01979, 0.02299, 0.01989, 0.02239, 0.0218, 0.02332, 0.02354, 0.0218, 0.02134]

Finished execution, total elapsed time: 73960.5714 secs (20.54 hours) (mean: 2958.42285, std: 764.88837)

#################### OVERALL RESULTS #################### (running in the NIMS server)

Test Score per Run: [0.73975, 0.70775, 0.7075, 0.72975, 0.707, 0.71475, 0.69675, 0.71725, 0.72125, 0.67475, 0.7, 0.6975, 0.69225, 0.7485, 0.6775, 0.6655, 0.71075, 0.69875, 0.70625, 0.70725, 0.7095, 0.716, 0.687, 0.74425, 0.66575]
mean: 0.70573
std. deviation: 0.02134
best run: 14

Train Score per Generation across Runs:
mean: [0.39883, 0.64133, 0.669, 0.693, 0.69566, 0.69849, 0.70416, 0.70083, 0.70216, 0.71116, 0.712]
std. deviation: [0.04157, 0.04189, 0.037, 0.03633, 0.03722, 0.02712, 0.02988, 0.03636, 0.02944, 0.0257, 0.03812]

Test Score per Generation across Runs:
mean: [0.4018, 0.62317, 0.66476, 0.68204, 0.68957, 0.69345, 0.69827, 0.70035, 0.70354, 0.70459, 0.70573]
std. deviation: [0.01183, 0.01776, 0.01979, 0.02299, 0.01989, 0.02239, 0.0218, 0.02332, 0.02354, 0.0218, 0.02134]

Finished execution, total elapsed time: 168980.20979 secs (mean: 6759.20839, std: 1768.90253)
"""

TICTACTOE_WITH_INIT2 = copy.deepcopy(TICTACTOE_DEFAULT)
TICTACTOE_WITH_INIT2['advanced_training_parameters']['run_initialization_step2'] = True
"""
#################### OVERALL RESULTS ####################

Test Score per Run: [0.7055, 0.72025, 0.711, 0.71075, 0.71625, 0.72025, 0.68625, 0.6795, 0.6875, 0.718, 0.7155, 0.69675, 0.6915, 0.71625, 0.736, 0.71225, 0.706, 0.72425, 0.72675, 0.70425, 0.71625, 0.73975, 0.7155, 0.68325, 0.7285]
mean: 0.71071
std. deviation: 0.01566
best run: 22

Train Score per Generation across Runs:
mean: [0.529, 0.6635, 0.68283, 0.69016, 0.696, 0.7045, 0.7055, 0.72466, 0.71516, 0.71933, 0.72333]
std. deviation: [0.05542, 0.04472, 0.04076, 0.03124, 0.04932, 0.04813, 0.03666, 0.02793, 0.03479, 0.0451, 0.03867]

Test Score per Generation across Runs:
mean: [0.52298, 0.65516, 0.67585, 0.68552, 0.69154, 0.69758, 0.70072, 0.70123, 0.70528, 0.70719, 0.71071]
std. deviation: [0.04688, 0.02739, 0.02559, 0.02493, 0.02226, 0.01906, 0.01728, 0.01729, 0.01882, 0.01905, 0.01566]

Finished execution, total elapsed time: 176251.19767 secs (mean: 7050.0479, std: 1366.09781)
"""

TICTACTOE_MORE_GENERATIONS = copy.deepcopy(TICTACTOE_DEFAULT)
TICTACTOE_MORE_GENERATIONS['training_parameters']['generations_total'] = 1000
"""
#################### OVERALL RESULTS ####################

Test Score per Run: [0.74075, 0.71175, 0.7175, 0.73725, 0.70675, 0.7205, 0.72775, 0.72475, 0.7315, 0.718, 0.70925, 0.69425, 0.69425, 0.74775, 0.6835, 0.708, 0.744, 0.73375, 0.7185, 0.7175, 0.71125, 0.7375, 0.7005, 0.74375, 0.68625]
mean: 0.71866
std. deviation: 0.01797
best run: 14

Train Score per Generation across Runs:
mean: [0.39883, 0.64133, 0.669, 0.693, 0.69566, 0.69849, 0.70416, 0.70083, 0.70216, 0.71116, 0.712, 0.69783, 0.71849, 0.71516, 0.72416, 0.71066, 0.717, 0.7175, 0.727, 0.73233, 0.722]
std. deviation: [0.04157, 0.04189, 0.037, 0.03633, 0.03722, 0.02712, 0.02988, 0.03636, 0.02944, 0.0257, 0.03812, 0.03426, 0.03574, 0.03117, 0.03553, 0.02891, 0.03106, 0.0406, 0.0368, 0.03296, 0.04637]

Test Score per Generation across Runs:
mean: [0.4018, 0.62317, 0.66476, 0.68204, 0.68957, 0.69345, 0.69827, 0.70035, 0.70354, 0.70459, 0.70573, 0.70668, 0.70813, 0.70849, 0.71223, 0.71294, 0.71369, 0.71464, 0.71649, 0.71876, 0.71866]
std. deviation: [0.01183, 0.01776, 0.01979, 0.02299, 0.01989, 0.02239, 0.0218, 0.02332, 0.02354, 0.0218, 0.02134, 0.02043, 0.01991, 0.02049, 0.01982, 0.01896, 0.01927, 0.01902, 0.01747, 0.0188, 0.01797]

Finished execution, total elapsed time: 366270.24336 secs (mean: 14650.80973, std: 4126.0743)
"""

TICTACTOE_WITH_PARETOS = copy.deepcopy(TICTACTOE_DEFAULT)
TICTACTOE_WITH_PARETOS['advanced_training_parameters']['use_pareto_for_team_population_selection'] = True
TICTACTOE_WITH_PARETOS['advanced_training_parameters']['use_pareto_for_point_population_selection'] = True
"""
#################### OVERALL RESULTS ####################

Test Score per Run: [0.72275, 0.727, 0.761, 0.701, 0.72525, 0.671, 0.73575, 0.71525, 0.743, 0.71075, 0.71125, 0.7245, 0.76, 0.731, 0.72075, 0.737, 0.7205, 0.73175, 0.70675, 0.722, 0.7235, 0.713, 0.733, 0.72475, 0.71975]
mean: 0.72369
std. deviation: 0.0176
best run: 3

Train Score per Generation across Runs:
mean: [0.40183, 0.58866, 0.63416, 0.65083, 0.65883, 0.665, 0.66483, 0.67983, 0.68866, 0.68633, 0.68666]
std. deviation: [0.03314, 0.0385, 0.03853, 0.03749, 0.04531, 0.02513, 0.03844, 0.03045, 0.03656, 0.0341, 0.02974]

Test Score per Generation across Runs:
mean: [0.3994, 0.63549, 0.66534, 0.68267, 0.69463, 0.70086, 0.71284, 0.71159, 0.71767, 0.72099, 0.72369]
std. deviation: [0.01369, 0.02178, 0.02907, 0.02752, 0.02583, 0.02569, 0.02045, 0.01991, 0.01735, 0.01949, 0.0176]

Finished execution, total elapsed time: 175879.44134 secs (mean: 7035.17765, std: 1449.83035)
"""

TICTACTOE_WITH_PARETO_FOR_TEAM_ONLY = copy.deepcopy(TICTACTOE_DEFAULT)
TICTACTOE_WITH_PARETO_FOR_TEAM_ONLY['advanced_training_parameters']['use_pareto_for_team_population_selection'] = True
TICTACTOE_WITH_PARETO_FOR_TEAM_ONLY['advanced_training_parameters']['use_pareto_for_point_population_selection'] = False
"""
#################### OVERALL RESULTS ####################

Test Score per Run: [0.716, 0.7155, 0.72425, 0.694, 0.71875, 0.7305, 0.72475, 0.668, 0.7165, 0.726, 0.7025, 0.71375, 0.718, 0.71, 0.689, 0.71075, 0.69425, 0.68725, 0.69875, 0.685, 0.70525, 0.7265, 0.734, 0.73925, 0.73075]
mean: 0.71117
std. deviation: 0.01734
best run: 24

Train Score per Generation across Runs:
mean: [0.40666, 0.634, 0.669, 0.69, 0.7015, 0.70366, 0.7055, 0.70983, 0.72416, 0.70849, 0.7185]
std. deviation: [0.03756, 0.03363, 0.03519, 0.04043, 0.03068, 0.03846, 0.0332, 0.03263, 0.03197, 0.02851, 0.0414]

Test Score per Generation across Runs:
mean: [0.40335, 0.62671, 0.67012, 0.68827, 0.6947, 0.70146, 0.7066, 0.70884, 0.70885, 0.70577, 0.71117]
std. deviation: [0.0098, 0.02209, 0.02705, 0.02126, 0.02542, 0.02626, 0.01849, 0.02415, 0.02195, 0.02083, 0.01734]

Finished execution, total elapsed time: 166642.0459 secs (mean: 6665.68183, std: 1377.27169)
"""

TICTACTOE_WITH_PARETO_FOR_POINT_ONLY = copy.deepcopy(TICTACTOE_DEFAULT)
TICTACTOE_WITH_PARETO_FOR_POINT_ONLY['advanced_training_parameters']['use_pareto_for_team_population_selection'] = False
TICTACTOE_WITH_PARETO_FOR_POINT_ONLY['advanced_training_parameters']['use_pareto_for_point_population_selection'] = True
"""
#################### OVERALL RESULTS ####################

Test Score per Run: [0.706, 0.724, 0.7485, 0.73075, 0.75925, 0.71625, 0.7215, 0.711, 0.69725, 0.727, 0.65975, 0.7275, 0.742, 0.6945, 0.70375, 0.73725, 0.7085, 0.7565, 0.70875, 0.73825, 0.723, 0.7385, 0.71, 0.73575, 0.71275]
mean: 0.72152
std. deviation: 0.0213
best run: 5

Train Score per Generation across Runs:
mean: [0.4, 0.608, 0.63566, 0.65716, 0.67466, 0.67133, 0.68116, 0.67983, 0.6825, 0.68116, 0.68666]
std. deviation: [0.04043, 0.04821, 0.02813, 0.0355, 0.03108, 0.03669, 0.02749, 0.03361, 0.0336, 0.02925, 0.02254]

Test Score per Generation across Runs:
mean: [0.39702, 0.62181, 0.65783, 0.67619, 0.6915, 0.69893, 0.70365, 0.7122, 0.71674, 0.71986, 0.72152]
std. deviation: [0.01453, 0.02565, 0.03063, 0.0339, 0.03252, 0.02879, 0.02758, 0.0238, 0.02237, 0.02053, 0.0213]

Finished execution, total elapsed time: 182552.65461 secs (mean: 7302.10618, std: 1520.57008)
"""

TICTACTOE_MORE_REGISTERS2 = copy.deepcopy(TICTACTOE_DEFAULT)
TICTACTOE_MORE_REGISTERS2['advanced_training_parameters']['extra_registers'] = 2
"""
#################### OVERALL RESULTS ####################

Test Score per Run: [0.73975, 0.70775, 0.7075, 0.72975, 0.707, 0.71475, 0.69675, 0.71725, 0.72125, 0.67475, 0.7, 0.6975, 0.69225, 0.7485, 0.6775, 0.6655, 0.71075, 0.69875, 0.70625, 0.70725, 0.7095, 0.716, 0.687, 0.74425, 0.66575]
mean: 0.70573
std. deviation: 0.02134
best run: 14

Train Score per Generation across Runs:
mean: [0.39883, 0.64133, 0.669, 0.693, 0.69566, 0.69849, 0.70416, 0.70083, 0.70216, 0.71116, 0.712]
std. deviation: [0.04157, 0.04189, 0.037, 0.03633, 0.03722, 0.02712, 0.02988, 0.03636, 0.02944, 0.0257, 0.03812]

Test Score per Generation across Runs:
mean: [0.4018, 0.62317, 0.66476, 0.68204, 0.68957, 0.69345, 0.69827, 0.70035, 0.70354, 0.70459, 0.70573]
std. deviation: [0.01183, 0.01776, 0.01979, 0.02299, 0.01989, 0.02239, 0.0218, 0.02332, 0.02354, 0.0218, 0.02134]

Finished execution, total elapsed time: 154101.3175 secs (mean: 6164.0527, std: 1606.06511)
"""

TICTACTOE_WITH_PARETO_GENOTYPE_DIVERSITY03 = copy.deepcopy(TICTACTOE_WITH_PARETOS)
TICTACTOE_WITH_PARETO_GENOTYPE_DIVERSITY03['advanced_training_parameters']['diversity']['genotype_fitness_maintanance'] = True
TICTACTOE_WITH_PARETO_GENOTYPE_DIVERSITY03['advanced_training_parameters']['diversity_configs']['genotype_fitness_maintanance']['p_value'] = 0.3
"""
#################### OVERALL RESULTS ####################

Test Score per Run: [0.713, 0.69925, 0.7305, 0.701, 0.718, 0.6945, 0.706, 0.72725, 0.6965, 0.68275, 0.705, 0.6935, 0.69925, 0.71725, 0.68325, 0.694, 0.73875, 0.67925, 0.6005, 0.698, 0.731, 0.70325, 0.686, 0.697, 0.69725]
mean: 0.69968
std. deviation: 0.02548
best run: 17

Train Score per Generation across Runs:
mean: [0.40466, 0.57716, 0.59933, 0.62483, 0.64233, 0.64516, 0.65499, 0.6565, 0.65766, 0.66733, 0.68149]
std. deviation: [0.03243, 0.05728, 0.04063, 0.03152, 0.03235, 0.03406, 0.02715, 0.03259, 0.02817, 0.03429, 0.0305]

Test Score per Generation across Runs:
mean: [0.40141, 0.60236, 0.61795, 0.63972, 0.65726, 0.67632, 0.67794, 0.68878, 0.69205, 0.69821, 0.69968]
std. deviation: [0.01445, 0.01948, 0.02377, 0.0258, 0.02487, 0.02444, 0.0329, 0.0263, 0.01713, 0.02446, 0.02548]

Mean Diversity per Generation across Runs (genotype_diversity):
mean: [1.0, 0.8451, 0.82691, 0.80471, 0.79436, 0.7787, 0.76995, 0.7594, 0.7628, 0.75722, 0.76222]
std. deviation: [0.0, 0.0245, 0.02647, 0.02743, 0.02443, 0.01782, 0.03221, 0.02059, 0.01944, 0.021, 0.01494]

Finished execution, total elapsed time: 166426.18607 secs (mean: 6657.04744, std: 1545.1153)
"""

TICTACTOE_WITH_PARETO_SHARING_DIVERSITY03 = copy.deepcopy(TICTACTOE_WITH_PARETOS)
TICTACTOE_WITH_PARETO_SHARING_DIVERSITY03['advanced_training_parameters']['diversity']['fitness_sharing'] = True
TICTACTOE_WITH_PARETO_SHARING_DIVERSITY03['advanced_training_parameters']['diversity_configs']['fitness_sharing']['p_value'] = 0.3
"""
32469, nohup4.out
"""