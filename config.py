USE_MSE3 = False

CURRENT_DIR = "C:/Users/jpbonson/Dropbox/Dalhousie Winter 2015/Genetic Algorithms/GeneticProgrammingSandbox/"
# CURRENT_DIR = ""

CONFIG = {
    'program_population_size': 200,
    'team_population_size': 100, # must be half the population_size
    'max_generation_total': 20,
    'mutation_single_instruction_rate': 0.9,
    'mutation_instruction_set_rate': 0.9,
    'mutation_team_rate': 0.9,
    'runs_total': 10,
    'minimum_program_size': 16,
    'initial_program_size': 32, # 32
    'max_program_size': 64, # 64
    'minimum_team_size': 2,
    'initial_team_size': 3,
    'max_team_size': 6,
    'total_calculation_registers': 3,
    'replacement_rate': 0.2,
    'sampling': {
        'use_sampling': True,
        'sampling_size': 420,
    }
}