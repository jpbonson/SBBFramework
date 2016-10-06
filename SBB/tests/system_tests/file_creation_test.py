import glob
import os
import unittest
import shutil
from collections import deque
from tictactoe_test import TEST_CONFIG
from ...config import Config
from ...sbb import SBB

class FileCreationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        super(FileCreationTests, cls).setUpClass()
        Config.RESTRICTIONS['write_output_files'] = True
        Config.RESTRICTIONS['output_folder'] = "SBB/tests/temp_files/"
        Config.RESTRICTIONS['novelty_archive']['samples'] = deque(maxlen=int(TEST_CONFIG['training_parameters']['populations']['teams']*1.0))
        
        config = dict(TEST_CONFIG)
        config['training_parameters']['runs_total'] = 1
        config['reinforcement_parameters']['hall_of_fame']['enabled'] = True
        config['reinforcement_parameters']['hall_of_fame']['opponents'] = 2
        Config.USER = config

        Config.check_parameters()
        sbb = SBB()
        sbb.run()

    @classmethod
    def tearDownClass(cls):
        super(FileCreationTests, cls).tearDownClass()
        shutil.rmtree("SBB/tests/temp_files/")

    def test_file_creation(self):
        expected = set(["metrics_overall.txt","run1",'last_hall_of_fame','metrics.txt',
            'last_generation_teams','best_team.json','second_layer_files','best_team.txt'])
        result = []
        for name in glob.glob(Config.RESTRICTIONS['output_folder']+'*/*'):
            name = name.split("/")[-1]
            name = name.split("\\")[-1]
            result.append(name)
        for name in glob.glob(Config.RESTRICTIONS['output_folder']+'*/run1/*'):
            name = name.split("/")[-1]
            name = name.split("\\")[-1]
            result.append(name)
        self.assertEquals(expected, set(result))

if __name__ == '__main__':
    unittest.main()

