import copy

"""
##### Results using Mann-Whitney U-Test (http://www.socscistatistics.com/tests/mannwhitney/Default2.aspx):

### COMPARISON REGARDING STEP2 IN INITIALIZATION

TICTACTOE_DEFAULT == TICTACTOE_WITH_INIT2
The U-value is 255.5. The distribution is approximately normal. Therefore, the Z-value can be used.
The Z-Score is -1.0963. The p-value is 0.27134. The result is not significant at p <= 0.05.

Results: Increases runtime without increasing performance.

### COMPARISON REGARDING PARETO

TICTACTOE_DEFAULT < TICTACTOE_WITH_PARETOS
The U-value is 143.5. The distribution is approximately normal. Therefore, the Z-value can be used.
The Z-Score is -3.2694. The p-value is 0.00108. The result is significant at p <= 0.05.

TICTACTOE_WITH_PARETOS ? TICTACTOE_WITH_PARETO_FOR_TEAM_ONLY


TICTACTOE_WITH_PARETOS ? TICTACTOE_WITH_PARETO_FOR_POINT_ONLY


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
Running on server (26881 nohup.out) - check if the Config is ok when finished
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
28247, nohup3
"""

TICTACTOE_WITH_PARETO_FOR_POINT_ONLY = copy.deepcopy(TICTACTOE_DEFAULT)
TICTACTOE_WITH_PARETO_FOR_POINT_ONLY['advanced_training_parameters']['use_pareto_for_team_population_selection'] = False
TICTACTOE_WITH_PARETO_FOR_POINT_ONLY['advanced_training_parameters']['use_pareto_for_point_population_selection'] = True
"""
28249, nohup4
"""