import copy

"""
##### Results using Mann-Whitney U-Test (http://www.socscistatistics.com/tests/mannwhitney/Default2.aspx):

pareto point
program size
oponentes
inputs
diversity
equity groups

"""

POKER_DEFAULT = {
    'task': 'reinforcement',
    'reinforcement_parameters': { # only used if 'task' is 'reinforcement'
        'environment': 'poker', # edit _initialize_environment() in SBB and RESTRICTIONS['environment_types'] to add new environments (they must implement DefaultEnvironment)
        'validation_population': 240, # at a validated generation, all the teams with be tested against this population, the best one is the champion
        'champion_population': 800, # at a validated generation, these are the points the champion team will play against to obtain the metrics
        'hall_of_fame': {
            'size': 10,
            'enabled': True,
            'diversity': 'normalized_compression_distance', # if False, use the fitness as the criteria to remove teams when the Hall of Fame is full
        },
        'debug_matches': False, # use this option to debug
    },

    'training_parameters': {
        'runs_total': 1,
        'generations_total': 150,
        'validate_after_each_generation': 25,
        'populations': {
            'teams': 80,
            'points': 80,
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
            'max': 10,
        },
    },

    'advanced_training_parameters': {
        'seed': 1, # default = None
        'use_pareto_for_point_population_selection': False, # if False, will select points using uniform probability
        'use_operations': ['+', '-', '*', '/', 'ln', 'exp', 'cos', 'if_lesser_than', 'if_equal_or_higher_than'],
        'extra_registers': 1,
        'diversity': {
            'use_and_show': ['normalized_compression_distance', 'genotype_distance'], # will be applied to fitness and show in the outputs
            'only_show': [], # will be only show in the outputs
            'k': 10,
        },
        'run_initialization_step2': False,
    },
}
POKER_DEFAULT_1 = copy.deepcopy(POKER_DEFAULT)
POKER_DEFAULT_1['advanced_training_parameters']['seed'] = 1
# 31282, nohup1 - 2 opps
# 19189, nohup3 - 4 opps

POKER_DEFAULT_2 = copy.deepcopy(POKER_DEFAULT)
POKER_DEFAULT_2['advanced_training_parameters']['seed'] = 2
# 

POKER_DEFAULT_ENTROPY_1 = copy.deepcopy(POKER_DEFAULT)
POKER_DEFAULT_ENTROPY_1['advanced_training_parameters']['seed'] = 1
POKER_DEFAULT_ENTROPY_1['reinforcement_parameters']['hall_of_fame']['diversity'] = 'relative_entropy_distance'
POKER_DEFAULT_ENTROPY_1['advanced_training_parameters']['diversity']['use_and_show'] = ['relative_entropy_distance', 'genotype_distance']
# 2984, nohup2 - 2 opps
# 12956, nohup6 - 4 opps

# ncd, 2 opps / ncd, 4 opps / entropy, 4 opps
