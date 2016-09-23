import copy
# How to use: Either copy and paste this on config.py, or uncomment the last line in config.py

SEED = 1

CLASS_CONFIG = {
    'task': 'classification',
    'classification_parameters': { # only used if 'task' is 'classification'
        'dataset': 'iris', # must have a .train and a .test file
        'working_path': "SBB/datasets/",
    },

    'training_parameters': {
        'runs_total': 25,
        'generations_total': 300,
        'validate_after_each_generation': 50,
        'populations': {
            'teams': 100,
            'points': 600,
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
            'max': 16,
        },
        'program_size': {
            'min': 5,
            'max': 40,
        },
    },

    'advanced_training_parameters': {
        'seed': SEED, # default = None, it can be a single seed for all runs, or an array of seeds per run, WARNING: It not ensures that runs with the same seed will have the same result, just increases the chance
        'use_pareto_for_point_population_selection': False, # if False, will select points using age
        'use_operations': ['+', '-', '*', '/', 'ln', 'exp', 'cos', 'if_lesser_than', 'if_equal_or_higher_than', 'if_lesser_than_for_signal', 'if_equal_or_higher_than_for_signal'],
        'extra_registers': 4,
        'diversity': {
            'use_and_show': ['genotype'], # will be applied to fitness and show in the outputs
            'only_show': [], # will be only show in the outputs
            'k': 10,
        },
        'run_initialization_step2': False,
        'use_weighted_probability_selection': False, # if False, uniform probability will be used
        'use_agressive_mutations': True,
        'second_layer': {
            'enabled': False,
            'path': 'actions_reference/baseline3_without_bayes/run[run_id]/second_layer_files/top10_overall/actions.json',
        },
    },
}

CLASS_CONFIG = copy.deepcopy(CLASS_CONFIG)
THYROID_CONFIG = copy.deepcopy(CLASS_CONFIG)
THYROID_CONFIG['classification_parameters']['dataset'] = 'thyroid'
SHUTTLE_CONFIG = copy.deepcopy(CLASS_CONFIG)
SHUTTLE_CONFIG['classification_parameters']['dataset'] = 'shuttle'