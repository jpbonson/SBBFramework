DEBUG_PROGRAM_STEADY_TOURNAMENT = False
DEBUG_PROGRAM_PROPORTIONAL_SELECTION = False
DEBUG_PROGRAM_EXECUTION = False
DEBUG_PROGRAM_CROSSOVER = False
DEBUG_PROGRAM_MUTATION = False

USE_MSE3 = False
USE_ACC_MR = False


CURRENT_DIR = "C:/Users/jpbonson/Dropbox/Dalhousie Winter 2015/Genetic Algorithms/GeneticProgrammingSandbox/"
# CURRENT_DIR = ""

CONFIG = {
    'population_size': 200,
    'max_generation_total': 20,
    'use_proportional_selection': True,  # if False, use steady tournament
    'crossover_rate': 0.1,
    'mutation_rate': 0.9,
    'runs_total': 2,
    'initial_program_size': 32,
    'max_program_size': 64,
    'total_calculation_registers': 2,
    'sampling': {
        'use_sampling': True,
        'use_probability_per_class': True, # or general probability
        'sampling_size': 420,
    }
}