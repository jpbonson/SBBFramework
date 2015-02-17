USE_MSE3 = False

CURRENT_DIR = "C:/Users/jpbonson/Dropbox/Dalhousie Winter 2015/Genetic Algorithms/GeneticProgrammingSandbox/"
# CURRENT_DIR = ""

DEFAULT_SHUTTLE_CONFIG = {
    'program_population_size': 400,
    'team_population_size': 200, # must be half the population_size
    'max_generation_total': 20,
    'mutation_single_instruction_rate': 0.9,
    'mutation_instruction_set_rate': 0.9,
    'mutation_team_rate': 0.9,
    'max_mutations_per_program': 5,
    'runs_total': 2, # !
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
        'sampling_size': 420, # {0: 11478, 1: 13, 2: 39, 3: 2155, 4: 809, 5: 4, 6: 2} -> {0: 60, 1: 13, 2: 39, 3: 60, 4: 60, 5: 4, 6: 2} -> 238
    },
    'remove_introns': True
}

DEFAULT_GISETTE_CONFIG = {
    'program_population_size': 400,
    'team_population_size': 200, # must be half the population_size
    'max_generation_total': 20,
    'mutation_single_instruction_rate': 0.9,
    'mutation_instruction_set_rate': 0.9,
    'mutation_team_rate': 0.9,
    'max_mutations_per_program': 5,
    'runs_total': 100, # !
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
    'remove_introns': True
}

CONFIG = DEFAULT_SHUTTLE_CONFIG
DATA_FILE = "shuttle"

# CONFIG = DEFAULT_GISETTE_CONFIG
# DATA_FILE = "gisette"