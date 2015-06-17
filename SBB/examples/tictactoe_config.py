import copy

"""
##### Results using Mann-Whitney U-Test (http://www.socscistatistics.com/tests/mannwhitney/Default2.aspx):



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
        'print_matches': False, # use this option to debug
    },

    'training_parameters': {
        'runs_total': 10,
        'generations_total': 500,
        'validate_after_each_generation': 50,
        'populations': {
            'teams': 100,
            'points': 100,
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
#################### OVERALL RESULTS #################### teams = 60, generations = 300

Test Score per Run: [0.7015, 0.66675, 0.70375, 0.69325, 0.6795, 0.71975, 0.73325, 0.72225, 0.68075, 0.65475]
mean: 0.69554
std. deviation: 0.02408
best run: 7

Train Score per Generation across Runs:
mean: [0.40791, 0.61541, 0.66375, 0.67791, 0.695, 0.69375, 0.6975]
std. deviation: [0.03024, 0.05287, 0.05728, 0.03151, 0.03105, 0.04327, 0.02893]

Test Score per Generation across Runs:
mean: [0.3963, 0.60967, 0.6521, 0.67597, 0.6831, 0.68625, 0.69554]
std. deviation: [0.00992, 0.01799, 0.02679, 0.02847, 0.02617, 0.0232, 0.02408]

Finished execution, total elapsed time: 9863.88489 secs (mean: 986.38848, std: 178.24815)

#################### OVERALL RESULTS #################### teams = 100, generations = 500, max: 18, points: 60 (HERE)

Test Score per Run: [0.73975, 0.70775, 0.7075, 0.72975, 0.707, 0.71475, 0.69675, 0.71725, 0.72125, 0.67475]
mean: 0.71165
std. deviation: 0.01699
best run: 1

Train Score per Generation across Runs:
mean: [0.39416, 0.64125, 0.66458, 0.70416, 0.71333, 0.69916, 0.70708, 0.71666, 0.70416, 0.71166, 0.71375]
std. deviation: [0.04278, 0.03245, 0.04591, 0.04018, 0.03881, 0.03077, 0.02116, 0.0268, 0.03195, 0.01898, 0.03891]

Test Score per Generation across Runs:
mean: [0.39727, 0.631, 0.6713, 0.68824, 0.69767, 0.70275, 0.7069, 0.71069, 0.71145, 0.71152, 0.71165]
std. deviation: [0.01097, 0.01699, 0.02619, 0.02753, 0.02205, 0.01793, 0.02164, 0.01868, 0.01884, 0.01744, 0.01699]

Finished execution, total elapsed time: 28757.88647 secs (mean: 2875.78864, std: 923.07447)

#################### OVERALL RESULTS #################### teams = 80, generations = 300

Test Score per Run: [0.674, 0.675, 0.7295, 0.70375, 0.65775, 0.676, 0.716, 0.72775, 0.6635, 0.68175]
mean: 0.6905
std. deviation: 0.02516
best run: 3

Train Score per Generation across Runs:
mean: [0.39916, 0.61541, 0.66875, 0.68541, 0.6825, 0.69833, 0.70208]
std. deviation: [0.04436, 0.0375, 0.05343, 0.03391, 0.02647, 0.02629, 0.03376]

Test Score per Generation across Runs:
mean: [0.4012, 0.63184, 0.66635, 0.67587, 0.68382, 0.68552, 0.6905]
std. deviation: [0.0073, 0.02225, 0.02368, 0.02074, 0.02087, 0.0256, 0.02516]

Finished execution, total elapsed time: 10422.17372 secs (mean: 1042.21737, std: 296.35298)

#################### OVERALL RESULTS #################### teams = 60, generations = 500
Test Score per Run: [0.7045, 0.6645, 0.70375, 0.701, 0.686, 0.73625, 0.7315, 0.742, 0.68325, 0.675]
mean: 0.70277
std. deviation: 0.02527
best run: 8

Train Score per Generation across Runs:
mean: [0.40791, 0.61541, 0.66375, 0.67791, 0.695, 0.69375, 0.6975, 0.68, 0.71125, 0.71041, 0.68791]
std. deviation: [0.03024, 0.05287, 0.05728, 0.03151, 0.03105, 0.04327, 0.02893, 0.03849, 0.03302, 0.05512, 0.03888]

Test Score per Generation across Runs:
mean: [0.3963, 0.60967, 0.6521, 0.67597, 0.6831, 0.68625, 0.69554, 0.6963, 0.69705, 0.7004, 0.70277]
std. deviation: [0.00992, 0.01799, 0.02679, 0.02847, 0.02617, 0.0232, 0.02408, 0.02667, 0.02484, 0.0216, 0.02527]

Finished execution, total elapsed time: 17603.03488 secs (mean: 1760.30348, std: 362.7728)

#################### OVERALL RESULTS #################### teams = 100, generations = 500, team_size, max: 12, points: 60 (HERE)


#################### OVERALL RESULTS #################### teams = 100, generations = 500, team_size, max: 18, points: 100 (HERE)

"""