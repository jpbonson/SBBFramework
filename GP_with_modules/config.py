USE_MSE3 = False

CURRENT_DIR = "C:/Users/jpbonson/Dropbox/Dalhousie Winter 2015/Genetic Algorithms/GeneticProgrammingSandbox/"
# CURRENT_DIR = ""

CONFIG = {
    'program_population_size': 200,
    'team_population_size': 100, # must be half the population_size
    'max_generation_total': 40, # 20 ou 40?
    'mutation_single_instruction_rate': 0.9,
    'mutation_instruction_set_rate': 0.9,
    'mutation_team_rate': 0.9,
    'max_mutations_per_program': 10,
    'runs_total': 5,
    'minimum_program_size': 20,
    'initial_program_size': 40,
    'max_program_size': 80,
    'minimum_team_size': 2,
    'initial_team_size': 7,
    'max_team_size': 14,
    'total_calculation_registers': 3, # [3, 2, 1, 3 with 10, 2 with 10, 1 with 10]
    'replacement_rate': 0.1,
    'sampling': {
        'use_sampling': True,
        'sampling_size': 420,
    }
}