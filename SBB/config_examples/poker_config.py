import copy
from ..environments.poker.poker_opponents import (PokerAlwaysCallOpponent, PokerAlwaysRaiseOpponent, 
    PokerLooseAgressiveOpponent, PokerLoosePassiveOpponent, PokerTightAgressiveOpponent, PokerTightPassiveOpponent,
    PokerBayesianOpponent)

# How to use: Either copy and paste this on config.py, or uncomment the last line in config.py

SEED = 2

POKER_CONFIG3 = {
    'task': 'reinforcement',
    'classification_parameters': { # only used if 'task' is 'classification'
        'dataset': 'thyroid', # must have a .train and a .test file in the pSBB/datasets folder
    },
    'reinforcement_parameters': { # only used if 'task' is 'reinforcement'
        'environment': 'poker', # edit _initialize_environment() in SBB and RESTRICTIONS['environment_types'] to add new environments (they must implement DefaultEnvironment)
        'validation_population': 1200, # at a validated generation, all the teams with be tested against this population, the best one is the champion
        'champion_population': 2400, # at a validated generation, these are the points the champion team will play against to obtain the metrics
        'hall_of_fame': {
            'size': 20,
            'enabled': True,
            'use_as_opponents': True,
            'diversity': 'ncd_c4', # if None, use the fitness as the criteria to remove teams when the Hall of Fame is full
            'max_opponents_per_generation': 2,
            'wait_generations': 100,
        },
        'debug': {
            'print': False,
            'matches': False,
            'output_path': 'SBB/environments/poker/logs/',
        },
        'poker': {
            'opponents': [PokerLooseAgressiveOpponent, PokerLoosePassiveOpponent, PokerTightAgressiveOpponent, PokerTightPassiveOpponent], # PokerBayesianOpponent, PokerBayesianOpponent, PokerBayesianOpponent, PokerBayesianOpponent], #[PokerLooseAgressiveOpponent],
            'river_round_only': False,
            'river_only_to_fullgame': False, # changed from one to another in half the generations, ignores 'river_round_only'
            'maximum_bets': 4,
        },
        'save_partial_files_per_validation': False,
    },

    'training_parameters': {
        'runs_total': 5,
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
            'use_and_show': ['ncd_c4', 'genotype'], # will be applied to fitness and show in the outputs
            'only_show': [], # will be only show in the outputs
            'k': 10,
        },
        'run_initialization_step2': False,
        'use_weighted_probability_selection': False, # if False, uniform probability will be used
        'use_agressive_mutations': True,
        'use_profiling': True,
        'second_layer': {
            'enabled': False,
            'use_atomic_actions': False,
            'path': 'actions_reference/baseline3_without_bayes/run[run_id]/second_layer_files/top10_overall/actions.json',
        },
    },
}

POKER_LAYER1 = copy.deepcopy(POKER_CONFIG3)

POKER_LAYER1_WITH_BAYES = copy.deepcopy(POKER_LAYER1)
POKER_LAYER1_WITH_BAYES['reinforcement_parameters']['poker']['opponents'] = [PokerLooseAgressiveOpponent, PokerLoosePassiveOpponent, PokerTightAgressiveOpponent, PokerTightPassiveOpponent, PokerBayesianOpponent, PokerBayesianOpponent, PokerBayesianOpponent, PokerBayesianOpponent]

POKER_LAYER2 = copy.deepcopy(POKER_CONFIG3)
POKER_LAYER2['training_parameters']['generations_total'] = 200
POKER_LAYER2['advanced_training_parameters']['second_layer']['enabled'] = True
POKER_LAYER2['advanced_training_parameters']['seed'] += 10

POKER_LAYER2_WITH_SUBCATS = copy.deepcopy(POKER_LAYER2)
POKER_LAYER2_WITH_SUBCATS['advanced_training_parameters']['second_layer']['path'] = 'actions_reference/baseline3_without_bayes/run[run_id]/second_layer_files/top10_overall_subcats/actions.json'