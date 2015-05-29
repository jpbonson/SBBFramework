import unittest
from pSBB.SBB.config import set_config
from pSBB.SBB.sbb import SBB

TEST_CONFIG = {
    'task': 'classification',
    'classification_parameters': { # only used if 'task' is 'classification'
        'dataset': 'iris', # must have a .train and a .test file in the pSBB/datasets folder
    },
    'training_parameters': {
        'runs_total': 5,
        'generations_total': 20,
        'validate_after_each_generation': 5,
        'populations': {
            'programs': 60,
            'teams': 30,
            'points': 120, # may not be used by some environments (eg.: tictactoe)
        },
        'replacement_rate': {
            'teams': 0.8,
            'points': 0.2,  # may not be used by some environments (eg.: tictactoe)
        },
        'mutation': {
            'team': {
                'remove_program': 0.7,
                'add_program': 0.8,
            },
            'program': {
                'remove_instruction': 0.7,
                'add_instruction': 0.8,
                'change_instruction': 0.8,
                'change_action': 0.1,
            },
        },
        'team_size': { # the min size is the total number of actions
            'max': 6,
        },
        'program_size': {
            'initial': 10,
            'min': 2,
            'max': 20,
        },
    },

    'advanced_training_parameters': {
        'seed': 1, # default = None
        'use_pareto_for_team_population_selection': True, # if False, will select solutions by best fitness
        'use_pareto_for_point_population_selection': True, # if False, will select points using uniform probability
        'use_operations': ['+', '-', '*', '/', 'ln', 'exp', 'cos', 'if_lesser_than', 'if_equal_or_higher_than'],
        'extra_registers': 1,
        'diversity': {
            'genotype_fitness_maintanance': True,
            'fitness_sharing': True,
        },
        'diversity_configs': { # p_value is with how much strenght this diversity metric will be applied to the fitness
            'genotype_fitness_maintanance': {
                'p_value': 0.1,
                'k': 8,
            },
            'fitness_sharing': {
                'p_value': 0.1,
            },       
        },
    },
}

class ClassificationTests(unittest.TestCase):
    def test_blah(self):
        """  """
        set_config({})
        sbb = SBB()
        sbb.run()
        a = sbb.best_scores_per_runs_
        self.assertEqual(a, a)

if __name__ == '__main__':
    unittest.main()