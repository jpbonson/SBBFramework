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

Finished execution, total elapsed time: 73960.5714 secs (20.54 hours) (mean: 2958.42285, std: 764.88837)
"""

TICTACTOE_DEFAULT = copy.deepcopy(TICTACTOE_DEFAULT)
TICTACTOE_DEFAULT['advanced_training_parameters']['run_initialization_step2'] = True
"""
Running on server
"""

TICTACTOE_DEFAULT = copy.deepcopy(TICTACTOE_DEFAULT)
TICTACTOE_DEFAULT['training_parameters']['generations_total'] = 1000
"""
Running on server
"""