import copy
from ..environments.poker.poker_opponents import (PokerAlwaysCallOpponent, PokerAlwaysRaiseOpponent, PokerAlwaysFoldOpponent,
    PokerLooseAgressiveOpponent, PokerLoosePassiveOpponent, PokerTightAgressiveOpponent, PokerTightPassiveOpponent,
    PokerBayesianOpponent, PokerRandomOpponent)

# How to use: Either copy and paste this on config.py, or uncomment the last line in config.py

SEED = 1

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
            'opponents': 2,
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
            'only_novelty': False,
            'use_novelty_archive': False,
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

POKER_LAYER1 = copy.deepcopy(POKER_CONFIG3)

POKER_LAYER_VAL0 = copy.deepcopy(POKER_CONFIG3)
POKER_LAYER_VAL0['training_parameters']['generations_total'] = 1
POKER_LAYER_VAL0['training_parameters']['validate_after_each_generation'] = 1
POKER_LAYER_VAL0['training_parameters']['runs_total'] = 25
POKER_LAYER_VAL0['reinforcement_parameters']['hall_of_fame']['enabled'] = False
POKER_LAYER_VAL0['reinforcement_parameters']['hall_of_fame']['use_as_opponents'] = False
POKER_LAYER_VAL0['reinforcement_parameters']['validation_population'] = 100
POKER_LAYER_VAL0['reinforcement_parameters']['champion_population'] = 100
POKER_LAYER_VAL0['reinforcement_parameters']['opponents'] = [PokerAlwaysFoldOpponent]
POKER_LAYER_VAL0['training_parameters']['team_size']['min'] = 3
POKER_LAYER_VAL0['advanced_training_parameters']['diversity']['use_and_show'] = []
# POKER_LAYER_VAL0['advanced_training_parameters']['run_initialization_step2'] = True

POKER_LAYER1_WITH_BAYES = copy.deepcopy(POKER_LAYER1)
POKER_LAYER1_WITH_BAYES['reinforcement_parameters']['opponents'] = [PokerLooseAgressiveOpponent, PokerLoosePassiveOpponent, PokerTightAgressiveOpponent, PokerTightPassiveOpponent, PokerBayesianOpponent, PokerBayesianOpponent, PokerBayesianOpponent, PokerBayesianOpponent]

POKER_LAYER2 = copy.deepcopy(POKER_CONFIG3)
POKER_LAYER2['training_parameters']['generations_total'] = 200
POKER_LAYER2['advanced_training_parameters']['second_layer']['enabled'] = True
POKER_LAYER2['advanced_training_parameters']['seed'] += 10
# POKER_LAYER2['advanced_training_parameters']['second_layer']['path'] = 'actions_reference/baseline_poker_paper/without_bayes/seed'+str(SEED)+'_run[run_id]/top10_overall_subcats/actions.json'
POKER_LAYER2['advanced_training_parameters']['second_layer']['path'] = "../outputs/outputs_for_paper/config_layer1_without_bayes_seed"+str(SEED)+"/run[run_id]/second_layer_files/actions_all_teams.json"

POKER_LAYER2_WITH_BAYES = copy.deepcopy(POKER_LAYER2)
# POKER_LAYER2_WITH_BAYES['advanced_training_parameters']['second_layer']['path'] = 'actions_reference/baseline_poker_paper/with_bayes/seed'+str(SEED)+'_run[run_id]/top10_overall_subcats/actions.json'
POKER_LAYER2_WITH_BAYES['advanced_training_parameters']['second_layer']['path'] = "../outputs/outputs_for_paper/config_layer1_with_bayes_seed"+str(SEED)+"/run[run_id]/second_layer_files/actions_all_teams.json"
POKER_LAYER2_WITH_BAYES['reinforcement_parameters']['opponents'] = [PokerLooseAgressiveOpponent, PokerLoosePassiveOpponent, PokerTightAgressiveOpponent, PokerTightPassiveOpponent, PokerBayesianOpponent, PokerBayesianOpponent, PokerBayesianOpponent, PokerBayesianOpponent]

POKER_LAYER1_NO_DIVERSITY = copy.deepcopy(POKER_LAYER1)
POKER_LAYER1_NO_DIVERSITY['advanced_training_parameters']['diversity']['use_and_show'] = []
POKER_LAYER1_NO_DIVERSITY['advanced_training_parameters']['use_profiling'] = False

POKER_LAYER1_WITH_DIVERSITY = copy.deepcopy(POKER_LAYER1)
POKER_LAYER1_WITH_DIVERSITY['training_parameters']['runs_total'] = 25
POKER_LAYER1_WITH_DIVERSITY['advanced_training_parameters']['diversity']['use_and_show'] = ['ncd_c4', 'genotype']
POKER_LAYER1_WITH_DIVERSITY['advanced_training_parameters']['use_profiling'] = True

POKER_LAYER1_NO_DIVERSITY_WITH_PROFILING = copy.deepcopy(POKER_LAYER1)
POKER_LAYER1_NO_DIVERSITY_WITH_PROFILING['advanced_training_parameters']['diversity']['use_and_show'] = []
POKER_LAYER1_NO_DIVERSITY_WITH_PROFILING['advanced_training_parameters']['use_profiling'] = True

POKER_LAYER1_WITH_DIVERSITY_NO_PROFILING = copy.deepcopy(POKER_LAYER1)
POKER_LAYER1_WITH_DIVERSITY_NO_PROFILING['advanced_training_parameters']['diversity']['use_and_show'] = ['ncd_c4', 'genotype']
POKER_LAYER1_WITH_DIVERSITY_NO_PROFILING['advanced_training_parameters']['use_profiling'] = False

POKER_LAYER1_ONLY_DIVERSITY = copy.deepcopy(POKER_LAYER1)
POKER_LAYER1_ONLY_DIVERSITY['advanced_training_parameters']['diversity']['use_and_show'] = ['ncd_c4']
POKER_LAYER1_ONLY_DIVERSITY['advanced_training_parameters']['diversity']['only_novelty'] = True

POKER_LAYER1_NCD = copy.deepcopy(POKER_LAYER1)
POKER_LAYER1_NCD['advanced_training_parameters']['diversity']['use_and_show'] = ['ncd_c4']

POKER_LAYER1_WITH_HAMMING_NO_PROFILING = copy.deepcopy(POKER_LAYER1)
POKER_LAYER1_WITH_HAMMING_NO_PROFILING['advanced_training_parameters']['diversity']['use_and_show'] = ['hamming_c3']
POKER_LAYER1_WITH_HAMMING_NO_PROFILING['advanced_training_parameters']['use_profiling'] = False

POKER_LAYER1_WITH_GENOTYPE_NO_PROFILING = copy.deepcopy(POKER_LAYER1)
POKER_LAYER1_WITH_GENOTYPE_NO_PROFILING['advanced_training_parameters']['diversity']['use_and_show'] = ['genotype']
POKER_LAYER1_WITH_GENOTYPE_NO_PROFILING['advanced_training_parameters']['use_profiling'] = False

POKER_LAYER1_ONLY_NOVELTY_NO_PROFILING = copy.deepcopy(POKER_LAYER1)
POKER_LAYER1_ONLY_NOVELTY_NO_PROFILING['training_parameters']['runs_total'] = 2
POKER_LAYER1_ONLY_NOVELTY_NO_PROFILING['advanced_training_parameters']['diversity']['use_and_show'] = ['ncd_c4']
POKER_LAYER1_ONLY_NOVELTY_NO_PROFILING['advanced_training_parameters']['diversity']['only_novelty'] = True
POKER_LAYER1_ONLY_NOVELTY_NO_PROFILING['advanced_training_parameters']['use_profiling'] = False
POKER_LAYER1_ONLY_NOVELTY_NO_PROFILING['advanced_training_parameters']['diversity']['use_novelty_archive'] = True

POKER_LAYER1_NOVELTY_AND_FITNESS_NO_PROFILING = copy.deepcopy(POKER_LAYER1)
POKER_LAYER1_NOVELTY_AND_FITNESS_NO_PROFILING['training_parameters']['runs_total'] = 1
POKER_LAYER1_NOVELTY_AND_FITNESS_NO_PROFILING['advanced_training_parameters']['diversity']['use_and_show'] = ['ncd_c4']
POKER_LAYER1_NOVELTY_AND_FITNESS_NO_PROFILING['advanced_training_parameters']['diversity']['only_novelty'] = False
POKER_LAYER1_NOVELTY_AND_FITNESS_NO_PROFILING['advanced_training_parameters']['use_profiling'] = False
POKER_LAYER1_NOVELTY_AND_FITNESS_NO_PROFILING['advanced_training_parameters']['diversity']['use_novelty_archive'] = True

# from config_examples import tictactoe_config, poker_config, classification_config, tictactoe_for_sockets_config
# from environments.poker.poker_opponents import (PokerAlwaysCallOpponent, PokerAlwaysRaiseOpponent, 
#     PokerLooseAgressiveOpponent, PokerLoosePassiveOpponent, PokerTightAgressiveOpponent, PokerTightPassiveOpponent,
#     PokerBayesianOpponent)

    #     'task': 'reinforcement',
    #     'classification_parameters': { # only used if 'task' is 'classification'
    #         'dataset': 'thyroid', # must have a .train and a .test file
    #         'working_path': "/home/jpbonson/Dropbox/MCS/SBBReinforcementLearner/SBB/datasets/",
    #     },
    #     'reinforcement_parameters': { # only used if 'task' is 'reinforcement'
    #         'environment': 'poker', # edit _initialize_environment() in SBB and RESTRICTIONS['environment_types'] to add new environments (they must implement DefaultEnvironment)
    #         'validation_population': 1200, # at a validated generation, all the teams with be tested against this population, the best one is the champion
    #         'champion_population': 2400, # at a validated generation, these are the points the champion team will play against to obtain the metrics
    #         'hall_of_fame': {
    #             'size': 20,
    #             'enabled': True,
    #             'use_as_opponents': True,
    #             'diversity': 'ncd_c4', # if None, use the fitness as the criteria to remove teams when the Hall of Fame is full
    #             'opponents': 2,
    #             'wait_generations': 100,
    #         },
    #         'debug': {
    #             'print': False,
    #             'matches': False,
    #             'output_path': 'SBB/environments/poker/logs/',
    #         },
    #         'poker': {
    #             'opponents': [PokerLooseAgressiveOpponent, PokerLoosePassiveOpponent, PokerTightAgressiveOpponent, PokerTightPassiveOpponent], # PokerBayesianOpponent, PokerBayesianOpponent, PokerBayesianOpponent, PokerBayesianOpponent], #[PokerLooseAgressiveOpponent],
    #             'river_round_only': False,
    #             'river_only_to_fullgame': False, # changed from one to another in half the generations, ignores 'river_round_only'
    #             'maximum_bets': 4,
    #         },
    #         'save_partial_files_per_validation': False,
    #     },

    #     'training_parameters': {
    #         'runs_total': 5,
    #         'generations_total': 300,
    #         'validate_after_each_generation': 50,
    #         'populations': {
    #             'teams': 100,
    #             'points': 600,
    #         },
    #         'replacement_rate': {
    #             'teams': 0.5,
    #             'points': 0.2,
    #         },
    #         'mutation': {
    #             'team': {
    #                 'remove_program': 0.7,
    #                 'add_program': 0.7,
    #                 'mutate_program': 0.2, # is applied to all programs in the team, until at least one program is mutated
    #             },
    #             'program': {
    #                 'remove_instruction': 0.5,
    #                 'add_instruction': 0.5,
    #                 'change_instruction': 1.0,
    #                 'swap_instructions': 1.0,
    #                 'change_action': 0.1,
    #             },
    #         },
    #         'team_size': { # the min and initial size are the total number of actions
    #             'min': 2,
    #             'max': 16,
    #         },
    #         'program_size': {
    #             'min': 5,
    #             'max': 40,
    #         },
    #     },

    #     'advanced_training_parameters': {
    #         'seed': 1, # default = None, it can be a single seed for all runs, or an array of seeds per run, WARNING: It not ensures that runs with the same seed will have the same result, just increases the chance
    #         'use_pareto_for_point_population_selection': False, # if False, will select points using age
    #         'use_operations': ['+', '-', '*', '/', 'ln', 'exp', 'cos', 'if_lesser_than', 'if_equal_or_higher_than', 'if_lesser_than_for_signal', 'if_equal_or_higher_than_for_signal'],
    #         'extra_registers': 4,
    #         'diversity': {
    #             'use_and_show': ['ncd_c4', 'genotype'], # will be applied to fitness and show in the outputs
    #             'only_show': [], # will be only show in the outputs
    #             'k': 10,
    #             'only_novelty': False,
    #             'use_novelty_archive': False,
    #         },
    #         'run_initialization_step2': False,
    #         'use_weighted_probability_selection': False, # if False, uniform probability will be used
    #         'use_agressive_mutations': True,
    #         'use_profiling': True,
    #         'second_layer': {
    #             'enabled': False,
    #             'path': 'actions_reference/baseline3_without_bayes/run[run_id]/second_layer_files/top10_overall/actions.json',
    #         },

    #         'sockets_parameters': {
    #             'debug': False,
    #             'timeout': 60,
    #             'buffer': 5000,
    #             'port': 7800,
    #             'host': 'localhost',
    #             'requests_timeout': 120,
    #         },
    #     },
    # }