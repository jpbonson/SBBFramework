USE_MSE3 = False

CURRENT_DIR = "C:/Users/jpbonson/Dropbox/Dalhousie Winter 2015/Genetic Algorithms/GeneticProgrammingSandbox/"
# CURRENT_DIR = ""

DEFAULT_CONFIG = {
    'program_population_size': 400,
    'team_population_size': 200, # must be half the population_size
    'max_generation_total': 20,
    'runs_total': 25,
    'total_calculation_registers': 1,
    'team_replacement_rate': 0.2,
    'point_replacement_rate': 1.0,

    'mutation_program_remove_instruction_rate': 0.8,
    'mutation_program_add_instruction_rate': 0.9,
    'mutation_program_single_instruction_rate': 0.9,
    'mutation_program_action_rate': 0.1,
    'mutation_team_remove_rate': 0.7,
    'mutation_team_add_rate': 0.8,

    'minimum_program_size': 1,
    'initial_program_size': 10,
    'max_program_size': 20,
    'minimum_team_size': 2,
    'initial_team_size': 3,
    'max_team_size': 6,

    'sampling': {
        'use_oversampling': False,
        'sampling_size': 200,
    },
    'remove_introns': False,
    'use_complex_functions': False,
    'enforce_initialize_at_least_one_action_per_class': False,
    'balanced_team_mutation': False,
    'print_recall_per_generation_for_best_run': True,
    'diversity': {
        'fitness_sharing': False,
        'classwise_fitness_sharing': False,
        'genotype_fitness_maintanance': False,
        'genotype_configs': {
            'p_value': 0.1,
            'k': 8,
        },        
    },
}

DEFAULT_CONFIG_V2 = {
    'program_population_size': 100,
    'team_population_size': 50, # must be half the population_size
    'max_generation_total': 200,
    'runs_total': 25,
    'total_calculation_registers': 1,
    'team_replacement_rate': 0.6,
    'point_replacement_rate': 0.3,

    'mutation_program_remove_instruction_rate': 0.8,
    'mutation_program_add_instruction_rate': 0.9,
    'mutation_program_single_instruction_rate': 0.9,
    'mutation_program_action_rate': 0.1,
    'mutation_team_remove_rate': 0.7,
    'mutation_team_add_rate': 0.7,

    'minimum_program_size': 1,
    'initial_program_size': 10,
    'max_program_size': 20,
    'minimum_team_size': 2,
    'initial_team_size': 3,
    'max_team_size': 10,

    'sampling': {
        'use_oversampling': True,
        'sampling_size': 120,
    },
    'remove_introns': False,
    'use_complex_functions': False,
    'enforce_initialize_at_least_one_action_per_class': True,
    'balanced_team_mutation': True,
    'print_recall_per_generation_for_best_run': True,
    'diversity': {
        'fitness_sharing': False,
        'classwise_fitness_sharing': False,
        'genotype_fitness_maintanance': False,
        'genotype_configs': {
            'p_value': 0.1,
            'k': 8,
        },        
    },
}

# CONFIG = DEFAULT_CONFIG
CONFIG = DEFAULT_CONFIG_V2

# CONFIG['max_team_size'] = 6
# DATA_FILE = "gisette"

#CONFIG['max_team_size'] = 14
#DATA_FILE = "shuttle"

CONFIG['max_team_size'] = 9
DATA_FILE = "thyroid"