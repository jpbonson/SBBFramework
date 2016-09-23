import unittest
import os
import subprocess
from collections import deque
from ...config import Config
from ...sbb import SBB
from ...environments.poker.poker_opponents import PokerRandomOpponent

TEST_CONFIG = {
    'task': 'reinforcement',
    'classification_parameters': { # only used if 'task' is 'classification'
        'dataset': 'thyroid', # must have a .train and a .test file in the pSBB/datasets folder
    },
    'reinforcement_parameters': { # only used if 'task' is 'reinforcement'
        'environment': 'poker', # edit _initialize_environment() in SBB and RESTRICTIONS['environment_types'] to add new environments (they must implement DefaultEnvironment)
        'validation_population': 18, # at a validated generation, all the teams with be tested against this population, the best one is the champion
        'champion_population': 18, # at a validated generation, these are the points the champion team will play against to obtain the metrics
        'hall_of_fame': {
            'size': 20,
            'enabled': False,
            'use_as_opponents': False,
            'diversity': 'ncd_c4', # if None, use the fitness as the criteria to remove teams when the Hall of Fame is full
            'max_opponents_per_generation': 2,
            'wait_generations': 100,
        },
        'poker': {
            'opponents': [PokerRandomOpponent],
            'river_round_only': False,
            'river_only_to_fullgame': False, # changed from one to another in half the generations, ignores 'river_round_only'
            'maximum_bets': 4,
        },
        'save_partial_files_per_validation': False,
    },

    'training_parameters': {
        'runs_total': 1,
        'generations_total': 5,
        'validate_after_each_generation': 5,
        'populations': {
            'teams': 10,
            'points': 18,
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
            'max': 8,
        },
        'program_size': {
            'min': 5,
            'max': 20,
        },
    },

    'advanced_training_parameters': {
        'seed': 1, # default = None, it can be a single seed for all runs, or an array of seeds per run, WARNING: It not ensures that runs with the same seed will have the same result, just increases the chance
        'use_pareto_for_point_population_selection': False, # if False, will select points using age
        'use_operations': ['+', '-', '*', '/', 'if_lesser_than', 'if_equal_or_higher_than'],
        'extra_registers': 4,
        'diversity': {
            'use_and_show': [], # will be applied to fitness and show in the outputs
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

    "debug": {
        "enabled": False,
        "output_path": "logs/",
    },
}

class TictactoeWithSocketsTests(unittest.TestCase):
    def setUp(self):
        Config.RESTRICTIONS['write_output_files'] = False
        Config.RESTRICTIONS['novelty_archive']['samples'] = deque(maxlen=int(TEST_CONFIG['training_parameters']['populations']['teams']*1.0))

        config = dict(TEST_CONFIG)
        Config.USER = config

    def test_reinforcement_for_poker(self):
        sbb = SBB()
        sbb.run()
        result = len(sbb.best_scores_per_runs_)
        expected = 1
        self.assertEqual(expected, result)

if __name__ == '__main__':
    unittest.main()