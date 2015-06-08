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
        'print_matches': False, # use this option to debug
    },

    'training_parameters': {
        'runs_total': 5,
        'generations_total': 200,
        'validate_after_each_generation': 50,
        'populations': {
            'programs': 120,
            'teams': 60,
            'points': 60,
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
            'max': 18,
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
#################### OVERALL RESULTS #################### point_population = 90 (old)

Test Score per Run: [0.68175, 0.6755, 0.71575, 0.6755, 0.69725]
mean: 0.68915
std. deviation: 0.01549

Train Score per Generation across Runs:
mean: [0.52388, 0.67666, 0.68, 0.71666, 0.68]
std. deviation: [0.05498, 0.04569, 0.0311, 0.02971, 0.03614]

Test Score per Generation across Runs:
mean: [0.4969, 0.66485, 0.67045, 0.68739, 0.68915]
std. deviation: [0.04828, 0.01884, 0.0151, 0.01643, 0.01549]

Finished execution, total elapsed time: 16958.914 secs (mean: 3391.7828, std: 214.35365)

#################### OVERALL RESULTS #################### point_population = 30

Test Score per Run: [0.6745, 0.672, 0.64249, 0.68725, 0.6745]
mean: 0.67014
std. deviation: 0.01482

Train Score per Generation across Runs:
mean: [0.48166, 0.66833, 0.64333, 0.67833, 0.66166]
std. deviation: [0.05807, 0.05436, 0.04755, 0.01943, 0.07257]

Test Score per Generation across Runs:
mean: [0.48605, 0.63205, 0.63849, 0.67005, 0.67015]
std. deviation: [0.04427, 0.02169, 0.02574, 0.0117, 0.01482]

Finished execution, total elapsed time: 6237.51399 secs (mean: 1247.50279, std: 154.82678)
"""