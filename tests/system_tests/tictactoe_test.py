import unittest
from collections import deque
from pSBB.SBB.config import Config
from pSBB.SBB.sbb import SBB

TEST_CONFIG = {
    'task': 'reinforcement',
    'reinforcement_parameters': { # only used if 'task' is 'reinforcement'
        'environment': 'tictactoe', # edit _initialize_environment() in SBB and RESTRICTIONS['environment_types'] to add new environments (they must implement DefaultEnvironment)
        'validation_population': 20, # at a validated generation, all the teams with be tested against this population, the best one is the champion
        'champion_population': 30, # at a validated generation, these are the points the champion team will play against to obtain the metrics
        'hall_of_fame': {
            'size': 6,
            'enabled': False,
            'use_as_opponents': False,
            'diversity': None,
        },
        'debug_matches': False, # use this option to debug
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
        'team_size': { # the min size is the total number of actions
            'min': 2,
            'max': 12,
        },
        'program_size': {
            'min': 2,
            'max': 12,
        },
    },

    'advanced_training_parameters': {
        'seed': 1, # default = None
        'use_pareto_for_point_population_selection': False, # if False, will select points using uniform probability
        'use_operations': ['+', '-', '*', '/', 'ln', 'exp', 'cos', 'if_lesser_than', 'if_equal_or_higher_than'],
        'extra_registers': 1,
        'diversity': {
            'use_and_show': [], # will be applied to fitness and show in the outputs
            'only_show': [], # will be only show in the outputs
            'k': 8,
            'total_bins': 5, # used to quantize the distances for the diversity metrics
        },
        'run_initialization_step2': False,
        'use_weighted_probability_selection': False, # if False, uniform probability will be used
    },
}

class ClassificationTests(unittest.TestCase):
    def setUp(self):
        Config.RESTRICTIONS['write_output_files'] = False
        Config.RESTRICTIONS['profile']['samples'] = deque(maxlen=int(TEST_CONFIG['training_parameters']['populations']['points']*1.0))

    def test_reinforcement_for_ttt_without_pareto_and_without_diversity_maintenance_for_only_coded_opponents_for_two_runs(self):
        """ Checking if everything for classification is still working and producing the same result. """
        config = dict(TEST_CONFIG)
        config['advanced_training_parameters']['use_pareto_for_point_population_selection'] = False
        config['advanced_training_parameters']['diversity']['use_and_show'] = []
        config['advanced_training_parameters']['diversity']['only_show'] = []
        config['reinforcement_parameters']['hall_of_fame']['enabled'] = False
        config['reinforcement_parameters']['hall_of_fame']['use_as_opponents'] = False
        config['reinforcement_parameters']['hall_of_fame']['diversity'] = None
        config['training_parameters']['runs_total'] = 2
        config['advanced_training_parameters']['seed'] = 1
        config['advanced_training_parameters']['use_operations'] = ['+', '-', '*', '/', 'ln', 'exp', 'cos', 'if_lesser_than', 'if_equal_or_higher_than']
        Config.USER['advanced_training_parameters']['run_initialization_step2'] = False
        Config.USER['advanced_training_parameters']['use_weighted_probability_selection'] = False
        Config.USER = config
        sbb = SBB()
        sbb.run()
        result = len(sbb.best_scores_per_runs_)
        expected = 2
        self.assertEqual(expected, result)

    def test_reinforcement_for_ttt_without_pareto_and_without_diversity_maintenance_for_only_coded_opponents(self):
        """ Checking if everything for classification is still working and producing the same result. """
        config = dict(TEST_CONFIG)
        config['advanced_training_parameters']['use_pareto_for_point_population_selection'] = False
        config['advanced_training_parameters']['diversity']['use_and_show'] = []
        config['advanced_training_parameters']['diversity']['only_show'] = []
        config['reinforcement_parameters']['hall_of_fame']['enabled'] = False
        config['reinforcement_parameters']['hall_of_fame']['use_as_opponents'] = False
        config['reinforcement_parameters']['hall_of_fame']['diversity'] = None
        config['training_parameters']['runs_total'] = 1
        config['advanced_training_parameters']['seed'] = [1]
        config['advanced_training_parameters']['use_operations'] = ['+', '-', '*', '/', 'ln', 'exp', 'cos', 'if_lesser_than', 'if_equal_or_higher_than']
        Config.USER['advanced_training_parameters']['run_initialization_step2'] = False
        Config.USER['advanced_training_parameters']['use_weighted_probability_selection'] = False
        Config.USER = config
        sbb = SBB()
        sbb.run()
        result = len(sbb.best_scores_per_runs_)
        expected = 1
        self.assertEqual(expected, result)

    def test_reinforcement_for_ttt_with_weighted_selection(self):
        """ Checking if everything for classification is still working and producing the same result. """
        config = dict(TEST_CONFIG)
        config['advanced_training_parameters']['use_pareto_for_point_population_selection'] = False
        config['advanced_training_parameters']['diversity']['use_and_show'] = []
        config['advanced_training_parameters']['diversity']['only_show'] = []
        config['reinforcement_parameters']['hall_of_fame']['enabled'] = False
        config['reinforcement_parameters']['hall_of_fame']['use_as_opponents'] = False
        config['reinforcement_parameters']['hall_of_fame']['diversity'] = None
        config['training_parameters']['runs_total'] = 1
        config['advanced_training_parameters']['seed'] = [1]
        config['advanced_training_parameters']['use_operations'] = ['+', '-', '*', '/', 'ln', 'exp', 'cos', 'if_lesser_than', 'if_equal_or_higher_than']
        Config.USER['advanced_training_parameters']['run_initialization_step2'] = False
        Config.USER['advanced_training_parameters']['use_weighted_probability_selection'] = True
        Config.USER = config
        sbb = SBB()
        sbb.run()
        result = len(sbb.best_scores_per_runs_)
        expected = 1
        self.assertEqual(expected, result)

    def test_reinforcement_for_ttt_with_run_initialization_step2(self):
        """ Checking if everything for classification is still working and producing the same result. """
        config = dict(TEST_CONFIG)
        config['advanced_training_parameters']['use_pareto_for_point_population_selection'] = False
        config['advanced_training_parameters']['diversity']['use_and_show'] = []
        config['advanced_training_parameters']['diversity']['only_show'] = []
        config['reinforcement_parameters']['hall_of_fame']['enabled'] = False
        config['reinforcement_parameters']['hall_of_fame']['use_as_opponents'] = False
        config['reinforcement_parameters']['hall_of_fame']['diversity'] = None
        config['training_parameters']['runs_total'] = 1
        config['advanced_training_parameters']['seed'] = [1]
        config['advanced_training_parameters']['use_operations'] = ['+', '-', '*', '/', 'ln', 'exp', 'cos', 'if_lesser_than', 'if_equal_or_higher_than']
        Config.USER['advanced_training_parameters']['run_initialization_step2'] = True
        Config.USER['advanced_training_parameters']['use_weighted_probability_selection'] = False
        Config.USER = config
        sbb = SBB()
        sbb.run()
        result = len(sbb.best_scores_per_runs_)
        expected = 1
        self.assertEqual(expected, result)

    def test_reinforcement_for_ttt_without_pareto_and_without_diversity_maintenance_for_only_sbb_opponents_showing_diversity(self):
        """ Checking if everything for classification is still working and producing the same result. """
        config = dict(TEST_CONFIG)
        config['advanced_training_parameters']['use_pareto_for_point_population_selection'] = False
        config['advanced_training_parameters']['diversity']['use_and_show'] = []
        config['advanced_training_parameters']['diversity']['only_show'] = ['genotype', 'fitness_sharing']
        config['reinforcement_parameters']['hall_of_fame']['enabled'] = False
        config['reinforcement_parameters']['hall_of_fame']['use_as_opponents'] = False
        config['reinforcement_parameters']['hall_of_fame']['diversity'] = None
        config['training_parameters']['runs_total'] = 1
        config['advanced_training_parameters']['seed'] = [1]
        config['advanced_training_parameters']['use_operations'] = ['+', '-', '*', '/', 'ln', 'exp', 'cos', 'if_lesser_than', 'if_equal_or_higher_than']
        Config.USER['advanced_training_parameters']['run_initialization_step2'] = False
        Config.USER['advanced_training_parameters']['use_weighted_probability_selection'] = False
        Config.USER = config
        sbb = SBB()
        sbb.run()
        result = len(sbb.best_scores_per_runs_)
        expected = 1
        self.assertEqual(expected, result)

    def test_reinforcement_for_ttt_without_pareto_and_with_genotype_diversity_maintenance(self):
        """ Checking if everything for classification is still working and producing the same result. """
        config = dict(TEST_CONFIG)
        config['advanced_training_parameters']['use_pareto_for_point_population_selection'] = False
        config['advanced_training_parameters']['diversity']['use_and_show'] = ['genotype']
        config['advanced_training_parameters']['diversity']['only_show'] = []
        config['reinforcement_parameters']['hall_of_fame']['enabled'] = False
        config['reinforcement_parameters']['hall_of_fame']['use_as_opponents'] = False
        config['reinforcement_parameters']['hall_of_fame']['diversity'] = None
        config['training_parameters']['runs_total'] = 1
        config['advanced_training_parameters']['seed'] = [1]
        config['advanced_training_parameters']['use_operations'] = ['+', '-', '*', '/', 'ln', 'exp', 'cos', 'if_lesser_than', 'if_equal_or_higher_than']
        Config.USER['advanced_training_parameters']['run_initialization_step2'] = False
        Config.USER['advanced_training_parameters']['use_weighted_probability_selection'] = False
        Config.USER = config
        sbb = SBB()
        sbb.run()
        result = len(sbb.best_scores_per_runs_)
        expected = 1
        self.assertEqual(expected, result)

    def test_reinforcement_for_ttt_without_pareto_and_with_sharing_diversity_maintenance(self):
        """ Checking if everything for classification is still working and producing the same result. """
        config = dict(TEST_CONFIG)
        config['advanced_training_parameters']['use_pareto_for_point_population_selection'] = False
        config['advanced_training_parameters']['diversity']['use_and_show'] = ['fitness_sharing']
        config['advanced_training_parameters']['diversity']['only_show'] = []
        config['reinforcement_parameters']['hall_of_fame']['enabled'] = False
        config['reinforcement_parameters']['hall_of_fame']['use_as_opponents'] = False
        config['reinforcement_parameters']['hall_of_fame']['diversity'] = None
        config['training_parameters']['runs_total'] = 1
        config['advanced_training_parameters']['seed'] = [1]
        config['advanced_training_parameters']['use_operations'] = ['+', '-', '*', '/', 'ln', 'exp', 'cos', 'if_lesser_than', 'if_equal_or_higher_than']
        Config.USER['advanced_training_parameters']['run_initialization_step2'] = False
        Config.USER['advanced_training_parameters']['use_weighted_probability_selection'] = False
        Config.USER = config
        sbb = SBB()
        sbb.run()
        result = len(sbb.best_scores_per_runs_)
        expected = 1
        self.assertEqual(expected, result)

    def test_reinforcement_for_ttt_without_pareto_and_with_ncd_c1_diversity_maintenance(self):
        """ Checking if everything for classification is still working and producing the same result. """
        config = dict(TEST_CONFIG)
        config['advanced_training_parameters']['use_pareto_for_point_population_selection'] = False
        config['advanced_training_parameters']['diversity']['use_and_show'] = ['ncd_c1']
        config['advanced_training_parameters']['diversity']['only_show'] = []
        config['reinforcement_parameters']['hall_of_fame']['enabled'] = False
        config['reinforcement_parameters']['hall_of_fame']['use_as_opponents'] = False
        config['reinforcement_parameters']['hall_of_fame']['diversity'] = None
        config['training_parameters']['runs_total'] = 1
        config['advanced_training_parameters']['seed'] = [1]
        config['advanced_training_parameters']['use_operations'] = ['+', '-', '*', '/', 'ln', 'exp', 'cos', 'if_lesser_than', 'if_equal_or_higher_than']
        Config.USER['advanced_training_parameters']['run_initialization_step2'] = False
        Config.USER['advanced_training_parameters']['use_weighted_probability_selection'] = False
        Config.USER = config
        sbb = SBB()
        sbb.run()
        result = len(sbb.best_scores_per_runs_)
        expected = 1
        self.assertEqual(expected, result)

    def test_reinforcement_for_ttt_without_pareto_and_with_entropy_c2_diversity_maintenance(self):
        """ Checking if everything for classification is still working and producing the same result. """
        config = dict(TEST_CONFIG)
        config['advanced_training_parameters']['use_pareto_for_point_population_selection'] = False
        config['advanced_training_parameters']['diversity']['use_and_show'] = ['entropy_c2']
        config['advanced_training_parameters']['diversity']['only_show'] = []
        config['reinforcement_parameters']['hall_of_fame']['enabled'] = False
        config['reinforcement_parameters']['hall_of_fame']['use_as_opponents'] = False
        config['reinforcement_parameters']['hall_of_fame']['diversity'] = None
        config['training_parameters']['runs_total'] = 1
        config['advanced_training_parameters']['seed'] = [1]
        config['advanced_training_parameters']['use_operations'] = ['+', '-', '*', '/', 'ln', 'exp', 'cos', 'if_lesser_than', 'if_equal_or_higher_than']
        Config.USER['advanced_training_parameters']['run_initialization_step2'] = False
        Config.USER['advanced_training_parameters']['use_weighted_probability_selection'] = False
        Config.USER = config
        sbb = SBB()
        sbb.run()
        result = len(sbb.best_scores_per_runs_)
        expected = 1
        self.assertEqual(expected, result)

    def test_reinforcement_for_ttt_without_pareto_and_with_hamming_c3_diversity_maintenance(self):
        """ Checking if everything for classification is still working and producing the same result. """
        config = dict(TEST_CONFIG)
        config['advanced_training_parameters']['use_pareto_for_point_population_selection'] = False
        config['advanced_training_parameters']['diversity']['use_and_show'] = ['hamming_c3']
        config['advanced_training_parameters']['diversity']['only_show'] = []
        config['reinforcement_parameters']['hall_of_fame']['enabled'] = False
        config['reinforcement_parameters']['hall_of_fame']['use_as_opponents'] = False
        config['reinforcement_parameters']['hall_of_fame']['diversity'] = None
        config['training_parameters']['runs_total'] = 1
        config['advanced_training_parameters']['seed'] = [1]
        config['advanced_training_parameters']['use_operations'] = ['+', '-', '*', '/', 'ln', 'exp', 'cos', 'if_lesser_than', 'if_equal_or_higher_than']
        Config.USER['advanced_training_parameters']['run_initialization_step2'] = False
        Config.USER['advanced_training_parameters']['use_weighted_probability_selection'] = False
        Config.USER = config
        sbb = SBB()
        sbb.run()
        result = len(sbb.best_scores_per_runs_)
        expected = 1
        self.assertEqual(expected, result)

    def test_reinforcement_for_ttt_without_pareto_and_with_ncd_c3_diversity_maintenance(self):
        """ Checking if everything for classification is still working and producing the same result. """
        config = dict(TEST_CONFIG)
        config['advanced_training_parameters']['use_pareto_for_point_population_selection'] = False
        config['advanced_training_parameters']['diversity']['use_and_show'] = ['ncd_c3']
        config['advanced_training_parameters']['diversity']['only_show'] = []
        config['reinforcement_parameters']['hall_of_fame']['enabled'] = False
        config['reinforcement_parameters']['hall_of_fame']['use_as_opponents'] = False
        config['reinforcement_parameters']['hall_of_fame']['diversity'] = None
        config['training_parameters']['runs_total'] = 1
        config['advanced_training_parameters']['seed'] = [1]
        config['advanced_training_parameters']['use_operations'] = ['+', '-', '*', '/', 'ln', 'exp', 'cos', 'if_lesser_than', 'if_equal_or_higher_than']
        Config.USER['advanced_training_parameters']['run_initialization_step2'] = False
        Config.USER['advanced_training_parameters']['use_weighted_probability_selection'] = False
        Config.USER = config
        sbb = SBB()
        sbb.run()
        result = len(sbb.best_scores_per_runs_)
        expected = 1
        self.assertEqual(expected, result)

    def test_reinforcement_for_ttt_without_pareto_and_with_entropy_c3_diversity_maintenance(self):
        """ Checking if everything for classification is still working and producing the same result. """
        config = dict(TEST_CONFIG)
        config['advanced_training_parameters']['use_pareto_for_point_population_selection'] = False
        config['advanced_training_parameters']['diversity']['use_and_show'] = ['entropy_c3']
        config['advanced_training_parameters']['diversity']['only_show'] = []
        config['reinforcement_parameters']['hall_of_fame']['enabled'] = False
        config['reinforcement_parameters']['hall_of_fame']['use_as_opponents'] = False
        config['reinforcement_parameters']['hall_of_fame']['diversity'] = None
        config['training_parameters']['runs_total'] = 1
        config['advanced_training_parameters']['seed'] = [1]
        config['advanced_training_parameters']['use_operations'] = ['+', '-', '*', '/', 'ln', 'exp', 'cos', 'if_lesser_than', 'if_equal_or_higher_than']
        Config.USER['advanced_training_parameters']['run_initialization_step2'] = False
        Config.USER['advanced_training_parameters']['use_weighted_probability_selection'] = False
        Config.USER = config
        sbb = SBB()
        sbb.run()
        result = len(sbb.best_scores_per_runs_)
        expected = 1
        self.assertEqual(expected, result)

    def test_reinforcement_for_ttt_without_pareto_and_with_ncd_c4_diversity_maintenance(self):
        """ Checking if everything for classification is still working and producing the same result. """
        config = dict(TEST_CONFIG)
        config['advanced_training_parameters']['use_pareto_for_point_population_selection'] = False
        config['advanced_training_parameters']['diversity']['use_and_show'] = ['ncd_c4']
        config['advanced_training_parameters']['diversity']['only_show'] = []
        config['reinforcement_parameters']['hall_of_fame']['enabled'] = False
        config['reinforcement_parameters']['hall_of_fame']['use_as_opponents'] = False
        config['reinforcement_parameters']['hall_of_fame']['diversity'] = None
        config['training_parameters']['runs_total'] = 1
        config['advanced_training_parameters']['seed'] = [1]
        config['advanced_training_parameters']['use_operations'] = ['+', '-', '*', '/', 'ln', 'exp', 'cos', 'if_lesser_than', 'if_equal_or_higher_than']
        Config.USER['advanced_training_parameters']['run_initialization_step2'] = False
        Config.USER['advanced_training_parameters']['use_weighted_probability_selection'] = False
        Config.USER = config
        sbb = SBB()
        sbb.run()
        result = len(sbb.best_scores_per_runs_)
        expected = 1
        self.assertEqual(expected, result)

    def test_reinforcement_for_ttt_without_pareto_and_with_euclidean_diversity_maintenance(self):
        """ Checking if everything for classification is still working and producing the same result. """
        config = dict(TEST_CONFIG)
        config['advanced_training_parameters']['use_pareto_for_point_population_selection'] = False
        config['advanced_training_parameters']['diversity']['use_and_show'] = ['euclidean']
        config['advanced_training_parameters']['diversity']['only_show'] = []
        config['reinforcement_parameters']['hall_of_fame']['enabled'] = False
        config['reinforcement_parameters']['hall_of_fame']['use_as_opponents'] = False
        config['reinforcement_parameters']['hall_of_fame']['diversity'] = None
        config['training_parameters']['runs_total'] = 1
        config['advanced_training_parameters']['seed'] = [1]
        config['advanced_training_parameters']['use_operations'] = ['+', '-', '*', '/', 'ln', 'exp', 'cos', 'if_lesser_than', 'if_equal_or_higher_than']
        Config.USER['advanced_training_parameters']['run_initialization_step2'] = False
        Config.USER['advanced_training_parameters']['use_weighted_probability_selection'] = False
        Config.USER = config
        sbb = SBB()
        sbb.run()
        result = len(sbb.best_scores_per_runs_)
        expected = 1
        self.assertEqual(expected, result)

    def test_reinforcement_for_ttt_without_pareto_and_with_two_diversity_maintenance(self):
        """ Checking if everything for classification is still working and producing the same result. """
        config = dict(TEST_CONFIG)
        config['advanced_training_parameters']['use_pareto_for_point_population_selection'] = False
        config['advanced_training_parameters']['diversity']['use_and_show'] = ['genotype', 'fitness_sharing']
        config['advanced_training_parameters']['diversity']['only_show'] = []
        config['reinforcement_parameters']['hall_of_fame']['enabled'] = False
        config['reinforcement_parameters']['hall_of_fame']['use_as_opponents'] = False
        config['reinforcement_parameters']['hall_of_fame']['diversity'] = None
        config['training_parameters']['runs_total'] = 1
        config['advanced_training_parameters']['seed'] = [1]
        config['advanced_training_parameters']['use_operations'] = ['+', '-', '*', '/', 'ln', 'exp', 'cos', 'if_lesser_than', 'if_equal_or_higher_than']
        Config.USER['advanced_training_parameters']['run_initialization_step2'] = False
        Config.USER['advanced_training_parameters']['use_weighted_probability_selection'] = False
        Config.USER = config
        sbb = SBB()
        sbb.run()
        result = len(sbb.best_scores_per_runs_)
        expected = 1
        self.assertEqual(expected, result)

    def test_reinforcement_for_ttt_with_signal_if_instructions(self):
        """ Checking if everything for classification is still working and producing the same result. """
        config = dict(TEST_CONFIG)
        config['advanced_training_parameters']['use_pareto_for_point_population_selection'] = False
        config['advanced_training_parameters']['diversity']['use_and_show'] = ['ncd_c4']
        config['advanced_training_parameters']['diversity']['only_show'] = []
        config['reinforcement_parameters']['hall_of_fame']['enabled'] = False
        config['reinforcement_parameters']['hall_of_fame']['use_as_opponents'] = False
        config['reinforcement_parameters']['hall_of_fame']['diversity'] = None
        config['training_parameters']['runs_total'] = 1
        config['advanced_training_parameters']['seed'] = [1]
        config['advanced_training_parameters']['use_operations'] = ['+', '-', '*', '/', 'ln', 'exp', 'cos', 'if_lesser_than_for_signal', 'if_equal_or_higher_than_for_signal']
        Config.USER['advanced_training_parameters']['run_initialization_step2'] = False
        Config.USER['advanced_training_parameters']['use_weighted_probability_selection'] = False
        Config.USER = config
        sbb = SBB()
        sbb.run()
        result = len(sbb.best_scores_per_runs_)
        expected = 1
        self.assertEqual(expected, result)

    def test_reinforcement_for_ttt_without_pareto_and_without_diversity_maintenance_for_only_coded_opponents_with_hall_of_fame(self):
        """ Checking if everything for classification is still working and producing the same result. """
        config = dict(TEST_CONFIG)
        config['advanced_training_parameters']['use_pareto_for_point_population_selection'] = False
        config['advanced_training_parameters']['diversity']['use_and_show'] = []
        config['advanced_training_parameters']['diversity']['only_show'] = []
        config['reinforcement_parameters']['hall_of_fame']['enabled'] = True
        config['reinforcement_parameters']['hall_of_fame']['use_as_opponents'] = True
        config['reinforcement_parameters']['hall_of_fame']['diversity'] = None
        config['training_parameters']['runs_total'] = 1
        config['advanced_training_parameters']['seed'] = [1]
        config['advanced_training_parameters']['use_operations'] = ['+', '-', '*', '/', 'ln', 'exp', 'cos', 'if_lesser_than', 'if_equal_or_higher_than']
        Config.USER['advanced_training_parameters']['run_initialization_step2'] = False
        Config.USER['advanced_training_parameters']['use_weighted_probability_selection'] = False
        Config.USER = config
        sbb = SBB()
        sbb.run()
        result = len(sbb.best_scores_per_runs_)
        expected = 1
        self.assertEqual(expected, result)

    def test_reinforcement_for_ttt_without_pareto_and_without_diversity_maintenance_for_only_coded_opponents_with_hall_of_fame_not_used_as_opponents(self):
        """ Checking if everything for classification is still working and producing the same result. """
        config = dict(TEST_CONFIG)
        config['advanced_training_parameters']['use_pareto_for_point_population_selection'] = False
        config['advanced_training_parameters']['diversity']['use_and_show'] = []
        config['advanced_training_parameters']['diversity']['only_show'] = []
        config['reinforcement_parameters']['hall_of_fame']['enabled'] = True
        config['reinforcement_parameters']['hall_of_fame']['use_as_opponents'] = False
        config['reinforcement_parameters']['hall_of_fame']['diversity'] = None
        config['training_parameters']['runs_total'] = 1
        config['advanced_training_parameters']['seed'] = [1]
        config['advanced_training_parameters']['use_operations'] = ['+', '-', '*', '/', 'ln', 'exp', 'cos', 'if_lesser_than', 'if_equal_or_higher_than']
        Config.USER['advanced_training_parameters']['run_initialization_step2'] = False
        Config.USER['advanced_training_parameters']['use_weighted_probability_selection'] = False
        Config.USER = config
        sbb = SBB()
        sbb.run()
        result = len(sbb.best_scores_per_runs_)
        expected = 1
        self.assertEqual(expected, result)

    def test_reinforcement_for_ttt_without_pareto_and_without_diversity_maintenance_for_only_coded_opponents_with_hall_of_fame_with_diversity(self):
        """ Checking if everything for classification is still working and producing the same result. """
        config = dict(TEST_CONFIG)
        config['advanced_training_parameters']['use_pareto_for_point_population_selection'] = False
        config['advanced_training_parameters']['diversity']['use_and_show'] = []
        config['advanced_training_parameters']['diversity']['only_show'] = []
        config['reinforcement_parameters']['hall_of_fame']['enabled'] = True
        config['reinforcement_parameters']['hall_of_fame']['use_as_opponents'] = True
        config['reinforcement_parameters']['hall_of_fame']['diversity'] = 'ncd_c1'
        config['training_parameters']['runs_total'] = 1
        config['advanced_training_parameters']['seed'] = [1]
        config['advanced_training_parameters']['use_operations'] = ['+', '-', '*', '/', 'ln', 'exp', 'cos', 'if_lesser_than', 'if_equal_or_higher_than']
        Config.USER['advanced_training_parameters']['run_initialization_step2'] = False
        Config.USER['advanced_training_parameters']['use_weighted_probability_selection'] = False
        Config.USER = config
        sbb = SBB()
        sbb.run()
        result = len(sbb.best_scores_per_runs_)
        expected = 1
        self.assertEqual(expected, result)

if __name__ == '__main__':
    unittest.main()