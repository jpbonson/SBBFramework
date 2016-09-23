import unittest
import os
import subprocess
from collections import deque
from ...config import Config
from ...sbb import SBB
from ...environments.poker.poker_opponents import PokerRandomOpponent

TEST_CONFIG = {
    'task': 'reinforcement',
    'classification_parameters': { 
        'dataset': 'thyroid', 
    },
    'reinforcement_parameters': { 
        'environment': 'poker', 
        'validation_population': 18, 
        'champion_population': 18, 
        'hall_of_fame': {
            'size': 20,
            'enabled': False,
            'use_as_opponents': False,
            'diversity': 'ncd_c4',
            'max_opponents_per_generation': 2,
            'wait_generations': 100,
        },
        'poker': {
            'opponents': [PokerRandomOpponent],
            'river_round_only': False,
            'river_only_to_fullgame': False, 
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
                'mutate_program': 0.2, 
            },
            'program': {
                'remove_instruction': 0.5,
                'add_instruction': 0.5,
                'change_instruction': 1.0,
                'swap_instructions': 1.0,
                'change_action': 0.1,
            },
        },
        'team_size': { 
            'min': 2,
            'max': 8,
        },
        'program_size': {
            'min': 5,
            'max': 20,
        },
    },

    'advanced_training_parameters': {
        'seed': 1, 
        'use_pareto_for_point_population_selection': False, 
        'use_operations': ['+', '-', '*', '/', 'if_lesser_than', 'if_equal_or_higher_than'],
        'extra_registers': 4,
        'diversity': {
            'use_and_show': [], 
            'only_show': [], 
            'k': 10,
            'only_novelty': False,
            'use_novelty_archive': False,
        },
        'run_initialization_step2': False,
        'use_weighted_probability_selection': False, 
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