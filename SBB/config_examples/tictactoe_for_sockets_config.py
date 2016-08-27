import copy

# How to use: Either copy and paste this on config.py, or uncomment the last line in config.py

# takes around 1 min, the best teams have around 0.7 win ratio
TICTACTOE_QUICK = {
    'task': 'reinforcement',
    'reinforcement_parameters': { # only used if 'task' is 'reinforcement'
        'environment': 'sockets', # edit _initialize_environment() in SBB and RESTRICTIONS['environment_types'] to add new environments (they must implement DefaultEnvironment)
        'validation_population': 20, # at a validated generation, all the teams with be tested against this population, the best one is the champion
        'champion_population': 40, # at a validated generation, these are the points the champion team will play against to obtain the metrics
        'hall_of_fame': {
            'size': 20,
            'enabled': False,
            'use_as_opponents': False,
            'diversity': 'genotype', # if None, use the fitness as the criteria to remove teams when the Hall of Fame is full
            'max_opponents_per_generation': 2,
            'wait_generations': 100,
        },
        'debug': {
            'print': False,
            'matches': False,
            'players': False,
            'debug_output_path': '',
        },
        'save_partial_files_per_validation': False,
    },
    'training_parameters': {
        'runs_total': 1,
        'generations_total': 20,
        'validate_after_each_generation': 20,
        'populations': {
            'teams': 10,
            'points': 10,
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
        'team_size': { # the min and initial size are the total number of actions
            'min': 2,
            'max': 9,
        },
        'program_size': {
            'min': 2,
            'max': 20,
        },
    },

    'advanced_training_parameters': {
        'seed': 1, # default = None, it can be a single seed for all runs, or an array of seeds per run, WARNING: It not ensures that runs with the same seed will have the same result, just increases the chance
        'use_pareto_for_point_population_selection': False, # if False, will select points using age
        'use_operations': ['+', '-', '*', '/', 'ln', 'exp', 'cos', 'if_lesser_than', 'if_equal_or_higher_than', 'if_lesser_than_for_signal', 'if_equal_or_higher_than_for_signal'],
        'extra_registers': 4,
        'diversity': {
            'use_and_show': ['genotype'], # will be applied to fitness and show in the outputs
            'only_show': [], # will be only show in the outputs
            'k': 10,
            'only_novelty': False,
            'use_novelty_archive': False,
        },
        'run_initialization_step2': False,
        'use_weighted_probability_selection': False, # if False, uniform probability will be used
        'use_agressive_mutations': True,
        'use_profiling': True,
        'second_layer': {
            'enabled': False,
            'path': 'actions_reference/baseline/run[run_id]/second_layer_files/hall_of_fame+top10_overall_subcats/actions.json',
        },
    },
}

# takes around 1h30, the best teams have around 0.85 win ratio
TICTACTOE_DEFAULT = {
    'task': 'reinforcement',
    'reinforcement_parameters': { # only used if 'task' is 'reinforcement'
        'environment': 'sockets', # edit _initialize_environment() in SBB and RESTRICTIONS['environment_types'] to add new environments (they must implement DefaultEnvironment)
        'validation_population': 200, # at a validated generation, all the teams with be tested against this population, the best one is the champion
        'champion_population': 400, # at a validated generation, these are the points the champion team will play against to obtain the metrics
        'hall_of_fame': {
            'size': 20,
            'enabled': False,
            'use_as_opponents': False,
            'diversity': 'genotype', # if None, use the fitness as the criteria to remove teams when the Hall of Fame is full
            'max_opponents_per_generation': 2,
            'wait_generations': 100,
        },
        'debug': {
            'print': False,
            'matches': False,
            'players': False,
            'debug_output_path': '',
        },
        'save_partial_files_per_validation': True,
    },
    'training_parameters': {
        'runs_total': 1,
        'generations_total': 50,
        'validate_after_each_generation': 25,
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
        'team_size': { # the min and initial size are the total number of actions
            'min': 2,
            'max': 12,
        },
        'program_size': {
            'min': 5,
            'max': 20,
        },
    },

    'advanced_training_parameters': {
        'seed': 1, # default = None, it can be a single seed for all runs, or an array of seeds per run, WARNING: It not ensures that runs with the same seed will have the same result, just increases the chance
        'use_pareto_for_point_population_selection': False, # if False, will select points using age
        'use_operations': ['+', '-', '*', '/', 'ln', 'exp', 'cos', 'if_lesser_than', 'if_equal_or_higher_than', 'if_lesser_than_for_signal', 'if_equal_or_higher_than_for_signal'],
        'extra_registers': 4,
        'diversity': {
            'use_and_show': ['genotype'], # will be applied to fitness and show in the outputs
            'only_show': [], # will be only show in the outputs
            'k': 10,
            'only_novelty': False,
            'use_novelty_archive': False,
        },
        'run_initialization_step2': False,
        'use_weighted_probability_selection': False, # if False, uniform probability will be used
        'use_agressive_mutations': True,
        'use_profiling': True,
        'second_layer': {
            'enabled': False,
            'path': 'actions_reference/baseline/run[run_id]/second_layer_files/hall_of_fame+top10_overall_subcats/actions.json',
        },
    },
}

TICTACTOE_RESEARCH = copy.deepcopy(TICTACTOE_DEFAULT)
TICTACTOE_RESEARCH['training_parameters']['runs_total'] = 20

TICTACTOE_RESEARCH_2 = copy.deepcopy(TICTACTOE_RESEARCH)
TICTACTOE_RESEARCH_2['advanced_training_parameters']['use_profiling'] = True
TICTACTOE_RESEARCH_2['advanced_training_parameters']['diversity']['use_and_show'] = []
TICTACTOE_RESEARCH_2['advanced_training_parameters']['diversity']['only_show'] = ['genotype']
TICTACTOE_RESEARCH_3 = copy.deepcopy(TICTACTOE_RESEARCH)
TICTACTOE_RESEARCH_3['advanced_training_parameters']['use_profiling'] = True
TICTACTOE_RESEARCH_3['advanced_training_parameters']['diversity']['use_and_show'] = ['genotype']
TICTACTOE_RESEARCH_3['advanced_training_parameters']['diversity']['only_show'] = []

# TICTACTOE_RESEARCH_2_LAYER2 = copy.deepcopy(TICTACTOE_RESEARCH_2)
# TICTACTOE_RESEARCH_2_LAYER2['advanced_training_parameters']['second_layer']['enabled'] = True
# TICTACTOE_RESEARCH_2_LAYER2['advanced_training_parameters']['seed'] += 10
# TICTACTOE_RESEARCH_2_LAYER2['advanced_training_parameters']['second_layer']['path'] = 'actions_reference/ttt_config2/run[run_id]_all_actions.json'

# TICTACTOE_RESEARCH_3_LAYER2 = copy.deepcopy(TICTACTOE_RESEARCH_3)
# TICTACTOE_RESEARCH_3_LAYER2['advanced_training_parameters']['second_layer']['enabled'] = True
# TICTACTOE_RESEARCH_3_LAYER2['advanced_training_parameters']['seed'] += 10
# TICTACTOE_RESEARCH_3_LAYER2['advanced_training_parameters']['second_layer']['path'] = 'actions_reference/ttt_config3/run[run_id]_all_actions.json'

TICTACTOE_RESEARCH_2_LAYER2 = copy.deepcopy(TICTACTOE_RESEARCH_2)
TICTACTOE_RESEARCH_2_LAYER2['advanced_training_parameters']['second_layer']['enabled'] = True
TICTACTOE_RESEARCH_2_LAYER2['advanced_training_parameters']['seed'] += 10
TICTACTOE_RESEARCH_2_LAYER2['advanced_training_parameters']['second_layer']['path'] = 'actions_reference/ttt_new_config2/val5/run[run_id]_all_actions.json'

TICTACTOE_RESEARCH_3_LAYER2 = copy.deepcopy(TICTACTOE_RESEARCH_3)
TICTACTOE_RESEARCH_3_LAYER2['advanced_training_parameters']['second_layer']['enabled'] = True
TICTACTOE_RESEARCH_3_LAYER2['advanced_training_parameters']['seed'] += 10
TICTACTOE_RESEARCH_3_LAYER2['advanced_training_parameters']['second_layer']['path'] = 'actions_reference/ttt_new_config3/val5/run[run_id]_all_actions.json'