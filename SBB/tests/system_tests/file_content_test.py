import unittest
import os
import subprocess
from collections import deque
from ...config import Config
from ...sbb import SBB

TEST_CONFIG = {
    'task': 'reinforcement',
    'reinforcement_parameters': { 
        'environment': 'tictactoe', 
        'validation_population': 20,
        'champion_population': 30,
        'hall_of_fame': {
            'size': 6,
            'enabled': True,
            'diversity': None,
            'opponents': 2,
        },
        "environment_parameters": {
            "actions_total": 9, # for tictactoe: spaces in the board
            "weights_per_action": [],
            "inputs_total": 9, # for tictactoe: spaces in the board
            "point_labels_total": 1, # for tictactoe: since no labels are being used
            "training_opponents_labels": ["random", "smart"],
            "validation_opponents_labels": ["random", "smart"],
        },
    },
    'training_parameters': {
        'runs_total': 2,
        'generations_total': 30,
        'validate_after_each_generation': 30,
        'populations': {
            'teams': 12,
            'points': 12,
        },
        'replacement_rate': {
            'teams': 0.5,
            'points': 0.2,
        },
        'mutation': {
            'team': {
                'remove_program': 0.7,
                'add_program': 0.8,
                'mutate_program': 0.2,
            },
            'program': {
                'remove_instruction': 0.7,
                'add_instruction': 0.8,
                'change_instruction': 0.8,
                'swap_instructions': 0.8,
                'change_action': 0.1,
            },
        },
        'team_size': { 
            'min': 2,
            'max': 12,
        },
        'program_size': {
            'min': 2,
            'max': 12,
        },
    },

    'advanced_training_parameters': {
        'seed': 1,
        'use_operations': ['+', '-', '*', '/', 'if_lesser_than', 'if_equal_or_higher_than'],
        'extra_registers': 4,
        'diversity': {
            'metrics': [],
            'k': 8,
        },
        "novelty": {
            "enabled": False,
            "use_fitness": True,
        },
        'use_weighted_probability_selection': False,
        'use_agressive_mutations': False,
        'second_layer': {
            'enabled': False,
            'path': 'SBB/tests/system_tests/actions_reference/run[run_id]/second_layer_files/hall_of_fame/actions.json',
        },
    },

    "debug": {
        "enabled": False,
        "output_path": "logs/",
    },
}

class FileContentTests(unittest.TestCase):
    def setUp(self):
        Config.RESTRICTIONS['write_output_files'] = False
        Config.RESTRICTIONS['novelty_archive']['samples'] = deque(maxlen=int(TEST_CONFIG['training_parameters']['populations']['teams']*1.0))
        config = dict(TEST_CONFIG)
        Config.USER = config

    def test_file_content_for_run_info(self):
        Config.check_parameters()
        sbb = SBB()
        sbb.run()
        content = str(sbb.run_infos_[-1])
        self.assertTrue(content)

    def test_file_content_for_team(self):
        Config.check_parameters()
        sbb = SBB()
        sbb.run()
        content = str(sbb.environment_.hall_of_fame()[-1])
        self.assertTrue(content)

if __name__ == '__main__':
    unittest.main()