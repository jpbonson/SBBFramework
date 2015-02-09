USE_MSE3 = False

CURRENT_DIR = "C:/Users/jpbonson/Dropbox/Dalhousie Winter 2015/Genetic Algorithms/GeneticProgrammingSandbox/"
# CURRENT_DIR = ""

CONFIG = {
    'population_size': 200,
    'max_generation_total': 20,
    'mutation_single_instruction_rate': 0.9,
    'mutation_instruction_set_rate': 0.9,
    'runs_total': 2,
    'initial_program_size': 3, # 32
    'max_program_size': 6, # 64
    'total_calculation_registers': 2,
    'removal_rate': 0.2,
    'sampling': {
        'use_sampling': True,
        'sampling_size': 420,
    }
}