import sys
import numpy
from collections import deque
from config_examples import tictactoe_config, poker_config, classification_config, tictactoe_for_sockets_config
from environments.poker.poker_opponents import (PokerAlwaysCallOpponent, PokerAlwaysRaiseOpponent, 
    PokerLooseAgressiveOpponent, PokerLoosePassiveOpponent, PokerTightAgressiveOpponent, PokerTightPassiveOpponent,
    PokerBayesianOpponent)

class Config():
    """
    This class contain all the configurations and restrictions that will be used by SBB.
    You may change the attribute USER to run SBB with different configurations, but it 
    is not recommended to modify the attribute RESTRICTIONS.
    """

    # user configurable options
    USER = {
        'task': 'reinforcement',
        'classification_parameters': { # only used if 'task' is 'classification'
            'dataset': 'thyroid', # must have a .train and a .test file
            'working_path': "/home/jpbonson/Dropbox/MCS/SBBReinforcementLearner/SBB/datasets/",
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
            'seed': 1, # default = None, it can be a single seed for all runs, or an array of seeds per run, WARNING: It not ensures that runs with the same seed will have the same result, just increases the chance
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
            'use_profiling': True,
            'second_layer': {
                'enabled': False,
                'path': 'actions_reference/baseline3_without_bayes/run[run_id]/second_layer_files/top10_overall/actions.json',
            },
        },
    }

    # restrictions used to validate CONFIG and to control the system low-level configurations
    RESTRICTIONS = {
        'task_types': ['classification', 'reinforcement'],
        'environment_types': ['tictactoe', 'poker', 'sockets'],
        'round_to_decimals': 5, # if you change this value, you must update the unit tests
        'max_seed': numpy.iinfo(numpy.int32).max + abs(numpy.iinfo(numpy.int32).min), # so it works for both Windows and Ubuntu
        'is_nearly_equal_threshold': 0.0001,
        'genotype_options': {
            'modes': ['read-register', 'read-input'],
            'simple_operations': ['+', '-', '*', '/'],
            'complex_operations': ['ln', 'exp', 'cos', 'sin', 'if_lesser_than', 'if_equal_or_higher_than', 'if_lesser_than_for_signal', 'if_equal_or_higher_than_for_signal'],
            'one-operand-instructions': ['ln', 'exp', 'cos', 'sin'],
            'if-instructions': ['if_lesser_than', 'if_equal_or_higher_than'],
            'if-instructions-for-signal': ['if_lesser_than_for_signal', 'if_equal_or_higher_than_for_signal'],
            'instruction_size': 4,
            'output_registers': 1,
            'total_registers': None, # initialized by sbb.py
        },
        'total_actions': -1, # initialized by the environment, can be meta or atomic actions
        'total_raw_actions': -1, # initialized by the environment, are the atomic actions performed in the environment
        'total_inputs': -1, # initialized by the environment
        'action_mapping': {}, # initialized by the environment
        'use_memmory_for_actions': False, # initialized by the environment
        'write_output_files': True, # used by the test cases
        'mode': {
            'training': 'training',
            'validation': 'validation',
            'champion': 'champion',
        },
        'used_diversities': None, # initialized by sbb.py
        'multiply_normalization_by': 10.0,
        'profile': {
            'samples': deque(maxlen=int(USER['training_parameters']['populations']['points']*2.0)),
            'update_chance': 0.05,
        },
        'novelty_archive':{
            'samples': deque(maxlen=int(USER['training_parameters']['populations']['teams']*1.0)),
            'threshold': 10,
        },
        'diversity': {
            'options': ['genotype', 'fitness_sharing', 'entropy_c2', 'hamming_c3', 'ncd_c3', 'entropy_c3', 'ncd_c4', 'euclidean'], # must have the same name as the methods in DiversityMaintenance
            'total_bins': 3, # used to quantize the distances for the diversity metrics
            'max_ncd': 1.2,
        },
        'second_layer': {
            'action_mapping': {}, # initialized by sbb.py
            'short_action_mapping': {}, # initialized by sbb.py
        },
    }

    @staticmethod
    def check_parameters():
        """
        Check if the parameters in CONFIG are valid using RESTRICTIONS
        """
        if Config.USER['task'] not in Config.RESTRICTIONS['task_types']:
            sys.stderr.write("Error: Invalid 'task' in CONFIG! The valid values are "+str(Config.RESTRICTIONS['task_types'])+"\n")
            raise SystemExit

        diversities = Config.USER['advanced_training_parameters']['diversity']['use_and_show'] + Config.USER['advanced_training_parameters']['diversity']['only_show']
        
        for diversity in diversities:
            if diversity not in Config.RESTRICTIONS['diversity']['options']:
                sys.stderr.write("Error: Invalid '"+diversity+"' diversity in CONFIG! The valid values are "+str(Config.RESTRICTIONS['diversity']['options'])+"\n")
                raise SystemExit

        if Config.USER['task'] == 'classification':
            if 'ncd_c1' in diversities or 'entropy_c2' in diversities or 'hamming_c3' in diversities or 'ncd_c3' in diversities or 'entropy_c3' in diversities or 'ncd_c4' in diversities or 'euclidean' in diversities:
                sys.stderr.write("Error: Can't calculate this diversity for a classification task!\n")
                raise SystemExit

        if Config.USER['task'] == 'reinforcement':
            if Config.USER['reinforcement_parameters']['hall_of_fame']['diversity']:
                if Config.USER['reinforcement_parameters']['hall_of_fame']['diversity'] not in Config.RESTRICTIONS['diversity']['options']:
                    sys.stderr.write("Error: Invalid 'diversity' for 'hall_of_fame' in CONFIG! The valid values are "+str(Config.RESTRICTIONS['diversity']['options'])+"\n")
                    raise SystemExit
            if not Config.USER['reinforcement_parameters']['hall_of_fame']['enabled'] and Config.USER['reinforcement_parameters']['hall_of_fame']['use_as_opponents']:
                sys.stderr.write("Error: For hall of fame, 'use_as_opponents' can't be True if 'enabled' is False\n")
                raise SystemExit

        if Config.USER['task'] == 'reinforcement' and Config.USER['reinforcement_parameters']['environment'] not in Config.RESTRICTIONS['environment_types']:
            sys.stderr.write("Error: Invalid 'environment' in CONFIG! The valid values are "+str(Config.RESTRICTIONS['environment_types'])+"\n")
            raise SystemExit

        valid_operations = Config.RESTRICTIONS['genotype_options']['simple_operations'] + Config.RESTRICTIONS['genotype_options']['complex_operations']
        for op in Config.USER['advanced_training_parameters']['use_operations']:  
            if op not in valid_operations:
                sys.stderr.write("Error: Invalid 'use_operations' in CONFIG! The valid values are "+str(valid_operations)+"\n")
                raise SystemExit

        if Config.USER['training_parameters']['generations_total'] % Config.USER['training_parameters']['validate_after_each_generation'] != 0:
            sys.stderr.write("Error: 'validate_after_each_generation' should be a multiple for 'generations_total', in order to ensure validation of the last generation.\n")
            raise SystemExit

        if isinstance(Config.USER['advanced_training_parameters']['seed'], list):
            if len(Config.USER['advanced_training_parameters']['seed']) != Config.USER['training_parameters']['runs_total']:
                sys.stderr.write("Error: If you are using an array of seeds, the size of the array must be equal to the total of runs.\n")
                raise SystemExit

# To run SBB with a predefined parameter set, uncomment the next line. More defaults are available in /config_examples

Config.USER = tictactoe_for_sockets_config.TICTACTOE_QUICK

# Config.USER = tictactoe_config.TICTACTOE_DEFAULT
# Config.USER = tictactoe_config.TICTACTOE_QUICK

# Config.USER = poker_config.POKER_LAYER1
# Config.USER = poker_config.POKER_LAYER1_WITH_BAYES
# Config.USER = poker_config.POKER_LAYER2
# Config.USER = poker_config.POKER_LAYER2_WITH_BAYES
# Config.USER = poker_config.POKER_LAYER1_WITH_DIVERSITY
# Config.USER = poker_config.POKER_LAYER1_NO_DIVERSITY_WITH_PROFILING
# Config.USER = poker_config.POKER_LAYER1_NOVELTY_AND_FITNESS_NO_PROFILING

# Config.USER = classification_config.CLASS_CONFIG
# Config.USER = classification_config.THYROID_CONFIG
# Config.USER = classification_config.SHUTTLE_CONFIG