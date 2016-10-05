import time
from collections import defaultdict
from helpers import round_array, round_value
from ..config import Config

class RunInfo:
    """
    Stores metrics for the runs.
    """

    def __init__(self, run_id, environment, seed):
        self.run_id = run_id
        self.environment = environment
        self.seed = seed

        self.elapsed_time_ = None
        self.best_team_ = None
        self.teams_in_last_generation_ = []
        self.hall_of_fame_in_last_generation_ = []
        self.pareto_front_in_last_generation_ = []
        self.second_layer_files_ = {}
        self.start_time_ = time.time()
        self.temp_info_ = {}
        
        self.global_mean_validation_score_per_validation_ = []
        self.train_score_per_validation_ = []
        self.test_score_per_validation_ = []
        self.global_diversity_per_validation_ = defaultdict(list)
        self.global_mean_fitness_per_generation_ = []
        self.global_max_fitness_per_generation_ = []
        self.global_fitness_per_diversity_per_generation_ = defaultdict(list)
        self.global_diversity_per_generation_ = defaultdict(list)
        self.novelty_type_per_generation_ = []
        self.actions_distribution_per_validation_ = []
        self.inputs_distribution_per_instruction_per_validation_ = []
        self.inputs_distribution_per_team_per_validation_ = []
        self.mean_team_size_per_validation_ = []
        self.mean_program_size_with_introns_per_validation_ = []
        self.mean_program_size_without_introns_per_validation_ = []
        
        self.environment.initialize_attributes_for_run_info(self)

    def end(self):
        self.elapsed_time_ = round_value((time.time() - self.start_time_)/60.0)
        
    def __str__(self):
        msg = "RUN "+str(self.run_id)+"\n"
        msg += "seed: "+str(self.seed)

        msg += "\n\n\n\n#################### General Metrics:"

        msg += "\n\n\n##### GLOBAL METRICS PER VALIDATION"

        msg += "\n\nGlobal Mean Validation Score per Validation: "+str(self.global_mean_validation_score_per_validation_)
        
        msg += "\n\nBest Team Fitness per Validation: "+str(round_array(self.train_score_per_validation_))
        msg += "\nBest Team Validation Score per Validation (champion): "+str(round_array(self.test_score_per_validation_))

        if len(Config.USER['advanced_training_parameters']['diversity']['metrics']) > 0:
            msg += "\n\nGlobal Diversities per Validation"
            for key in self.global_diversity_per_validation_:
                msg += "\n - "+str(key)+": "+str(self.global_diversity_per_validation_[key])


        msg += "\n\n\n##### GLOBAL METRICS PER TRAINING"

        msg += "\n\nGlobal Mean Fitness Score per Training: "+str(self.global_mean_fitness_per_generation_)
        msg += "\nGlobal Max. Fitness Score per Training: "+str(self.global_max_fitness_per_generation_)
        if len(Config.USER['advanced_training_parameters']['diversity']['metrics']) > 1:
            msg += "\n\n\nGlobal Fitness Score per Training (per diversity):"
            for key in self.global_fitness_per_diversity_per_generation_:
                msg += "\n - "+str(key)+": "+str(self.global_fitness_per_diversity_per_generation_[key])

        if len(Config.USER['advanced_training_parameters']['diversity']['metrics']) > 0:
            msg += "\n\nGlobal Diversities per Training"
            for key in self.global_diversity_per_generation_:
                msg += "\n - "+str(key)+": "+str(self.global_diversity_per_generation_[key])
            if len(Config.USER['advanced_training_parameters']['diversity']['metrics']) > 1:
                msg += "\n\nDiversity Type per Training: "+str(self.novelty_type_per_generation_)


        msg += "\n\n\n##### DISTRIBUTION METRICS PER VALIDATION"

        msg += "\n\nDistribution of Actions"
        msg += "\n - last validation: "+str(self.actions_distribution_per_validation_[-1])
        msg += "\n - per validation: "+str(self.actions_distribution_per_validation_)

        msg += "\n\nDistribution of Inputs (per program)"
        msg += "\n - last validation: "+str(self.inputs_distribution_per_instruction_per_validation_[-1])
        msg += "\n - per validation: "+str(self.inputs_distribution_per_instruction_per_validation_)

        msg += "\n\nDistribution of Inputs (per team)"
        msg += "\n - last validation: "+str(self.inputs_distribution_per_team_per_validation_[-1])
        msg += "\n - per validation: "+str(self.inputs_distribution_per_team_per_validation_)
        

        msg += "\n\n\n##### SIZE METRICS PER VALIDATION"

        msg += "\n\nMean Team Sizes"
        msg += "\n - last validation: "+str(self.mean_team_size_per_validation_[-1])
        msg += "\n - per validation: "+str(self.mean_team_size_per_validation_)

        msg += "\n\nMean Program Sizes (with introns)"
        msg += "\n - last validation: "+str(self.mean_program_size_with_introns_per_validation_[-1])
        msg += "\n - per validation: "+str(self.mean_program_size_with_introns_per_validation_)

        msg += "\n\nMean Program Sizes (without introns)"
        msg += "\n - last validation: "+str(self.mean_program_size_without_introns_per_validation_[-1])
        msg += "\n - per validation: "+str(self.mean_program_size_without_introns_per_validation_)


        msg += self.environment.generate_output_for_attributes_for_run_info(self)

        return msg