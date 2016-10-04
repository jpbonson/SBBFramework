from collections import defaultdict
from helpers import round_array
from ..config import Config

class RunInfo:
    """
    Stores metrics for the runs.
    """

    def __init__(self, run_id, environment, seed):
        self.run_id = run_id
        self.environment = environment
        self.seed = seed

        self.elapsed_time = None
        self.best_team = None
        self.teams_in_last_generation = []
        self.hall_of_fame_in_last_generation = []
        self.pareto_front_in_last_generation = []
        self.individual_performance_in_last_generation = defaultdict(list)
        self.accumulative_performance_in_last_generation = defaultdict(list)
        self.ids_for_acc_performance_in_last_generation = defaultdict(list)
        self.individual_performance_per_label_in_last_generation = defaultdict(dict)
        self.accumulative_performance_per_label_in_last_generation = defaultdict(dict)
        self.ids_for_acc_performance_per_label_in_last_generation = defaultdict(dict)
        self.train_score_per_validation = []
        self.test_score_per_validation = []
        self.actions_distribution_per_validation = []
        self.inputs_distribution_per_instruction_per_validation = []
        self.inputs_distribution_per_team_per_validation = []
        self.global_diversity_per_validation = defaultdict(list)
        self.global_mean_validation_score_per_validation = []
        self.global_max_validation_score_per_validation = []
        self.global_opponent_results_per_validation = []
        self.global_mean_fitness_per_generation = []
        self.global_max_fitness_per_generation = []
        self.global_fitness_per_diversity_per_generation = defaultdict(list)
        self.global_fitness_per_opponent_per_generation = defaultdict(list)
        self.global_diversity_per_generation = defaultdict(list)
        self.novelty_type_per_generation = []
        self.validation_population_distribution_per_validation = {}
        self.champion_population_distribution_per_validation = {}
        self.global_result_per_validation = defaultdict(dict)
        self.point_population_distribution_per_validation = defaultdict(dict)
        self.hall_of_fame_per_validation = []
        self.mean_team_size_per_validation = []
        self.mean_program_size_with_introns_per_validation = []
        self.mean_program_size_without_introns_per_validation = []
        self.final_teams_validations = []
        self.final_teams_validations_per_subcategory = defaultdict(dict)
        self.final_teams_validations_ids = []
        self.accumulative_performance_summary = {}
        self.second_layer_files = {}
        self.environment.initialize_attributes_for_run_info(self)
        
    def __str__(self):
        msg = "RUN "+str(self.run_id)+"\n"
        msg += "seed: "+str(self.seed)

        msg += "\n\n\n\n#################### General Metrics:"

        msg += "\n\n\n##### GLOBAL METRICS PER VALIDATION"

        msg += "\n\nGlobal Mean Validation Score per Validation: "+str(self.global_mean_validation_score_per_validation)
        
        msg += "\n\nBest Team Fitness per Validation: "+str(round_array(self.train_score_per_validation))
        msg += "\nBest Team Validation Score per Validation (champion): "+str(round_array(self.test_score_per_validation))

        if len(Config.RESTRICTIONS['used_diversities']) > 0:
            msg += "\n\nGlobal Diversities per Validation"
            for key in self.global_diversity_per_validation:
                msg += "\n - "+str(key)+": "+str(self.global_diversity_per_validation[key])


        msg += "\n\n\n##### GLOBAL METRICS PER TRAINING"

        msg += "\n\nGlobal Mean Fitness Score per Training: "+str(self.global_mean_fitness_per_generation)
        msg += "\nGlobal Max. Fitness Score per Training: "+str(self.global_max_fitness_per_generation)
        if len(Config.RESTRICTIONS['used_diversities']) > 1:
            msg += "\n\n\nGlobal Fitness Score per Training (per diversity):"
            for key in self.global_fitness_per_diversity_per_generation:
                msg += "\n - "+str(key)+": "+str(self.global_fitness_per_diversity_per_generation[key])

        if len(Config.RESTRICTIONS['used_diversities']) > 0:
            msg += "\n\nGlobal Diversities per Training"
            for key in self.global_diversity_per_generation:
                msg += "\n - "+str(key)+": "+str(self.global_diversity_per_generation[key])
            if len(Config.RESTRICTIONS['used_diversities']) > 1:
                msg += "\n\nDiversity Type per Training: "+str(self.novelty_type_per_generation)


        msg += "\n\n\n##### DISTRIBUTION METRICS PER VALIDATION"

        msg += "\n\nDistribution of Actions"
        msg += "\n - last validation: "+str(self.actions_distribution_per_validation[-1])
        msg += "\n - per validation: "+str(self.actions_distribution_per_validation)

        msg += "\n\nDistribution of Inputs (per program)"
        msg += "\n - last validation: "+str(self.inputs_distribution_per_instruction_per_validation[-1])
        msg += "\n - per validation: "+str(self.inputs_distribution_per_instruction_per_validation)

        msg += "\n\nDistribution of Inputs (per team)"
        msg += "\n - last validation: "+str(self.inputs_distribution_per_team_per_validation[-1])
        msg += "\n - per validation: "+str(self.inputs_distribution_per_team_per_validation)
        

        msg += "\n\n\n##### SIZE METRICS PER VALIDATION"

        msg += "\n\nMean Team Sizes"
        msg += "\n - last validation: "+str(self.mean_team_size_per_validation[-1])
        msg += "\n - per validation: "+str(self.mean_team_size_per_validation)

        msg += "\n\nMean Program Sizes (with introns)"
        msg += "\n - last validation: "+str(self.mean_program_size_with_introns_per_validation[-1])
        msg += "\n - per validation: "+str(self.mean_program_size_with_introns_per_validation)

        msg += "\n\nMean Program Sizes (without introns)"
        msg += "\n - last validation: "+str(self.mean_program_size_without_introns_per_validation[-1])
        msg += "\n - per validation: "+str(self.mean_program_size_without_introns_per_validation)


        msg += self.environment.generate_output_for_attributes_for_run_info(self)

        return msg