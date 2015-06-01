THYROID_DEFAULT = {
    'task': 'classification',
    'classification_parameters': { # only used if 'task' is 'classification'
        'dataset': 'thyroid', # must have a .train and a .test file in the pSBB/datasets folder
    }, 

    'training_parameters': {
        'runs_total': 25,
        'generations_total': 300,
        'validate_after_each_generation': 50,
        'populations': {
            'programs': 120,
            'teams': 60,
            'points': 120, # may not be used by some environments (eg.: tictactoe)
        },
        'replacement_rate': {
            'teams': 0.7,
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
            'max': 9,
        },
        'program_size': {
            'initial': 10,
            'min': 2,
            'max': 20,
        },
    },

    'advanced_training_parameters': {
        'seed': 1, # default = None
        'use_pareto_for_team_population_selection': False, # if False, will select solutions by best fitness
        'use_pareto_for_point_population_selection': False, # if False, will select points using uniform probability
        'use_operations': ['+', '-', '*', '/', 'ln', 'exp', 'cos', 'if_lesser_than', 'if_equal_or_higher_than'],
        'extra_registers': 1,
        'diversity': {
            'genotype_fitness_maintanance': False,
            'fitness_sharing': False,
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
"""
#################### OVERALL RESULTS ####################


"""


THYROID_WITH_PARETO = dict(THYROID_DEFAULT)
THYROID_WITH_PARETO['advanced_training_parameters']['use_pareto_for_team_population_selection'] = True
THYROID_WITH_PARETO['advanced_training_parameters']['use_pareto_for_point_population_selection'] = True
"""
#################### OVERALL RESULTS ####################

Test Score per Run: [0.9359, 0.92688, 0.80415, 0.93901, 0.89512, 0.90193, 0.97541, 0.9493, 0.88491, 0.89903, 0.91519, 0.8951, 0.848, 0.95963, 0.92072, 0.97645, 0.95148, 0.9625, 0.91999, 0.86205, 0.94975, 0.89287, 0.88386, 0.86669, 0.79967]
mean: 0.9086236, std: 0.0466395722004

Mean Score per Generation across Runs: [0.5468, 0.81044, 0.85383, 0.87804, 0.89105, 0.91254, 0.90862]
Std. Deviation Score per Generation across Runs: [0.09441, 0.09349, 0.07772, 0.05945, 0.05571, 0.03456, 0.04663]

Finished execution, total elapsed time: 20266.50399 secs (mean: 810.66015, std: 70.06622)

##### Result using Mann-Whitney U-Test (http://www.socscistatistics.com/tests/mannwhitney/Default2.aspx):

"""