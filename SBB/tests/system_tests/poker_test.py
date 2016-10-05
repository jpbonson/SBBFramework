import unittest
import os
import subprocess
from collections import deque
from ...config import Config
from ...sbb import SBB

TEST_CONFIG = {
    'task': 'reinforcement',

    'reinforcement_parameters': { 
        'environment': 'poker', 
        'validation_population': 40, 
        'champion_population': 40,
        'hall_of_fame': {
            'size': 20,
            'enabled': False,
            'diversity': 'ncd',
            'opponents': 0,
        },
        "environment_parameters": {
            "actions_total": 3, # for poker: fold, call, raise
            "weights_per_action": [0.0, 0.5, 1.0],
            "inputs_total": 14, # for poker: hand strength, hand potential, opponent model, etc...
            "point_labels_total": 9, # for poker: combinations of [weak, intermediate, strong] for player's and opponent's hands
            "training_opponents_labels": ["loose_agressive", "loose_passive", "tight_agressive", "tight_passive"],
            "validation_opponents_labels": ["loose_agressive", "loose_passive", "tight_agressive", "tight_passive"],
        },
    },

    'training_parameters': {
        'runs_total': 1,
        'generations_total': 5,
        'validate_after_each_generation': 5,
        'populations': {
            'teams': 10,
            'points': 40,
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
        'use_operations': ['+', '-', '*', '/', 'if_lesser_than', 'if_equal_or_higher_than'],
        'extra_registers': 4,
        'diversity': {
            'metrics': [],
            'k': 10,
        },
        "novelty": {
            "enabled": False,
            "use_fitness": True,
        },
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
        config['training_parameters']['populations']['points'] = 40
        config['reinforcement_parameters']['validation_population'] = 40
        config['reinforcement_parameters']['champion_population'] = 40
        config['advanced_training_parameters']['diversity']['metrics'] = []
        config['advanced_training_parameters']['novelty']['enabled'] = False
        config['reinforcement_parameters']['environment_parameters']['training_opponents_labels'] = ["loose_agressive", "loose_passive", "tight_agressive", "tight_passive"]
        config['reinforcement_parameters']['environment_parameters']['validation_opponents_labels'] = ["loose_agressive", "loose_passive", "tight_agressive", "tight_passive"]
        Config.USER = config

    def test_reinforcement_for_poker(self):
        Config.check_parameters()
        sbb = SBB()
        sbb.run()
        result = len(sbb.best_scores_per_runs_)
        expected = 1
        self.assertEqual(expected, result)

    def test_reinforcement_for_poker_with_novelty(self):
        Config.USER['advanced_training_parameters']['diversity']['metrics'] = ['ncd']
        Config.USER['advanced_training_parameters']['novelty']['enabled'] = True
        Config.check_parameters()
        sbb = SBB()
        sbb.run()
        result = len(sbb.best_scores_per_runs_)
        expected = 1
        self.assertEqual(expected, result)

    def test_reinforcement_for_poker_with_ncd_custom_diversity(self):
        Config.USER['advanced_training_parameters']['diversity']['metrics'] = ['ncd_custom']
        Config.check_parameters()
        sbb = SBB()
        sbb.run()
        result = len(sbb.best_scores_per_runs_)
        expected = 1
        self.assertEqual(expected, result)

    def test_reinforcement_for_poker_with_hamming_diversity(self):
        Config.USER['advanced_training_parameters']['diversity']['metrics'] = ['hamming']
        Config.check_parameters()
        sbb = SBB()
        sbb.run()
        result = len(sbb.best_scores_per_runs_)
        expected = 1
        self.assertEqual(expected, result)

    def test_reinforcement_for_poker_with_euclidean_diversity(self):
        Config.USER['advanced_training_parameters']['diversity']['metrics'] = ['euclidean']
        Config.check_parameters()
        sbb = SBB()
        sbb.run()
        result = len(sbb.best_scores_per_runs_)
        expected = 1
        self.assertEqual(expected, result)

    def test_reinforcement_for_poker_with_dumb_opponents(self):
        opponents = ["random", "always_raise", "always_call", "always_fold"]
        Config.USER['reinforcement_parameters']['environment_parameters']['training_opponents_labels'] = opponents
        Config.USER['reinforcement_parameters']['environment_parameters']['validation_opponents_labels'] = opponents
        Config.check_parameters()
        sbb = SBB()
        sbb.run()
        result = len(sbb.best_scores_per_runs_)
        expected = 1
        self.assertEqual(expected, result)

    def test_reinforcement_for_poker_with_smart_opponents(self):
        opponents = ["bayesian_opponent"]
        Config.USER['reinforcement_parameters']['environment_parameters']['training_opponents_labels'] = opponents
        Config.USER['reinforcement_parameters']['environment_parameters']['validation_opponents_labels'] = opponents
        Config.check_parameters()
        sbb = SBB()
        sbb.run()
        result = len(sbb.best_scores_per_runs_)
        expected = 1
        self.assertEqual(expected, result)

    def test_file_content_for_poker_point(self):
        Config.check_parameters()
        sbb = SBB()
        sbb.run()
        content = str(sbb.environment_.point_population_[-1])
        self.assertTrue(content)

if __name__ == '__main__':
    unittest.main()