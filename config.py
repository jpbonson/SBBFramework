USE_MSE3 = False

CURRENT_DIR = "C:/Users/jpbonson/Dropbox/Dalhousie Winter 2015/Genetic Algorithms/GeneticProgrammingSandbox/"
# CURRENT_DIR = ""

DEFAULT_CONFIG = {
    'program_population_size': 400,
    'team_population_size': 200, # must be half the population_size
    'max_generation_total': 20,
    'mutation_single_instruction_rate': 0.9,
    'mutation_instruction_set_rate': 0.9,
    'mutation_team_rate': 0.9,
    'max_mutations_per_program': 5,
    'runs_total': 30, # !
    'minimum_program_size': 1,
    'initial_program_size': 10,
    'max_program_size': 20,
    'minimum_team_size': 2,
    'initial_team_size': 3,
    'max_team_size': 6,
    'total_calculation_registers': 1,
    'replacement_rate': 0.2,
    'sampling': {
        'use_sampling': True,
        'sampling_size': 200,
    },
    'remove_introns': False,
    'use_complex_functions': False,
    'print_recall_per_generation_for_best_run': True,
    'use_diversity': True,
    'diversity': {
        'fitness_sharing': False,
        'classwise_fitness_sharing': True,
    },
}

CONFIG = DEFAULT_CONFIG

CONFIG['runs_total'] = 30
CONFIG['sampling']['sampling_size'] = 200
DATA_FILE = "gisette"

# CONFIG['runs_total'] = 20
# CONFIG['sampling']['sampling_size'] = 420
# DATA_FILE = "shuttle"