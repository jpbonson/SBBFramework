from collections import defaultdict
from helpers import round_array
from ..config import Config

class RunInfo:
    """
    Stores metrics for the runs.
    """

    def __init__(self, run_id, seed):
        self.run_id = run_id
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
        self.recall_per_validation = [] # only for classification task
        self.actions_distribution_per_validation = []
        self.inputs_distribution_per_instruction_per_validation = []
        self.inputs_distribution_per_team_per_validation = []
        self.global_diversity_per_validation = defaultdict(list)
        self.global_fitness_score_per_validation = []
        self.global_validation_score_per_validation = []
        self.global_opponent_results_per_validation = []
        self.info_per_team_per_generation = []
        self.global_fitness_per_generation = []
        self.global_fitness_per_diversity_per_generation = defaultdict(list)
        self.global_fitness_per_opponent_per_generation = defaultdict(list)
        self.global_diversity_per_generation = defaultdict(list)
        self.novelty_type_per_generation = []
        self.opponent_type_per_generation = []
        self.validation_population_distribution_per_validation = {}
        self.champion_population_distribution_per_validation = {}
        self.global_result_per_validation = defaultdict(dict)
        self.point_population_distribution_per_validation = defaultdict(dict)
        self.hall_of_fame_per_validation = []
        self.mean_team_size_per_validation = []
        self.mean_program_size_with_introns_per_validation = []
        self.mean_program_size_without_introns_per_validation = []
        self.final_teams_validations = []
        
    def __str__(self):
        msg = "RUN "+str(self.run_id)+"\n"
        msg += "seed: "+str(self.seed)

        msg += "\n\n\n##### BEST TEAM METRICS PER VALIDATION"
        msg += "\n\nBest Team Fitness per Validation: "+str(round_array(self.train_score_per_validation))
        msg += "\n\nBest Team Validation Score per Validation (champion): "+str(round_array(self.test_score_per_validation))
        if Config.USER['task'] == 'classification':
            msg += "\n\nBest Team Recall per Action per Validation: "+str(self.recall_per_validation)

        msg += "\n\n\n##### GLOBAL METRICS PER VALIDATION"
        msg += "\n\nGlobal Fitness Score per Validation: "+str(self.global_fitness_score_per_validation)
        msg += "\n\nGlobal Validation Score per Validation: "+str(self.global_validation_score_per_validation)
        if Config.USER['task'] == 'reinforcement':
            msg += "\n\nGlobal Opponent Results per Validation"
            for key in self.global_opponent_results_per_validation[-1]:
                msg += "\n"+str(key)+": "+str([item[key] if key in item else 0.0 for item in self.global_opponent_results_per_validation])
            msg += "\n\nFinal Teams Validations: "+str(self.final_teams_validations)
        if len(Config.RESTRICTIONS['used_diversities']) > 0:
            msg += "\n\nGlobal Diversities per Validation"
            for key in self.global_diversity_per_validation:
                msg += "\n"+str(key)+": "+str(self.global_diversity_per_validation[key])
        if Config.USER['task'] == 'reinforcement' and Config.USER['reinforcement_parameters']['environment'] == 'poker':
            msg += "\n\nGlobal Team Results per Validation" # Global Results per Validation
            for attribute in self.global_result_per_validation:
                msg += "\n"+str(attribute)+":"
                for key in self.global_result_per_validation[attribute]:
                    msg += "\n- "+str(key)+": "+str(self.global_result_per_validation[attribute][key])

        msg += "\n\n\n##### DISTRIBUTION METRICS PER VALIDATION"
        msg += "\n\nDistribution of Actions per Validation: "+str(self.actions_distribution_per_validation)
        msg += "\n\nDistribution of Inputs per Validation (per instruction): "+str(self.inputs_distribution_per_instruction_per_validation)
        msg += "\n\nDistribution of Inputs per Validation (per team): "+str(self.inputs_distribution_per_team_per_validation)
        if Config.USER['task'] == 'reinforcement' and Config.USER['reinforcement_parameters']['environment'] == 'poker':
            msg += "\n\nPoints Distribution for the Validation Population: "+str(self.validation_population_distribution_per_validation) # Validation Population Distribution per Validation
            msg += "\n\nPoints Distribution for the Champion Population: "+str(self.champion_population_distribution_per_validation) # Champion Population Distribution per Validation
            msg += "\n\nPoints Distribution for the Training Population per Validation" # Training Population Distribution per Validation
            for attribute in self.point_population_distribution_per_validation:
                msg += "\n"+str(attribute)+":"
                for key in self.point_population_distribution_per_validation[attribute]:
                    msg += "\n- "+str(key)+": "+str(self.point_population_distribution_per_validation[attribute][key])
        if Config.USER['task'] == 'reinforcement' and Config.USER['reinforcement_parameters']['hall_of_fame']['enabled']:
            msg += "\n\nHall of Fame per Validation: "+str(self.hall_of_fame_per_validation)

        msg += "\n\n\n##### METRICS FOR SIZES PER VALIDATION"
        msg += "\n\nMean Team Sizes: "+str(self.mean_team_size_per_validation)
        msg += "\n\nMean Program Sizes (with introns): "+str(self.mean_program_size_with_introns_per_validation)
        msg += "\n\nMean Program Sizes (without introns): "+str(self.mean_program_size_without_introns_per_validation)

        msg += "\n\n\n##### GLOBAL METRICS PER TRAINING"
        msg += "\n\nGlobal Fitness Score per Training: "+str(self.global_fitness_per_generation)
        msg += "\n\nGlobal Fitness Score per Training (per diversity):"
        if len(Config.RESTRICTIONS['used_diversities']) > 1:
            for key in self.global_fitness_per_diversity_per_generation:
                msg += "\n"+str(key)+": "+str(self.global_fitness_per_diversity_per_generation[key])
        msg += "\n\nGlobal Fitness Score per Training (per opponent):"
        if Config.USER['task'] == 'reinforcement':
            for key in self.global_fitness_per_opponent_per_generation:
                msg += "\n"+str(key)+": "+str(self.global_fitness_per_opponent_per_generation[key])
        if Config.USER['task'] == 'reinforcement':
            msg += "\n\nOpponent Types per Training: "+str(self.opponent_type_per_generation)
        if len(Config.RESTRICTIONS['used_diversities']) > 0:
            msg += "\n\nGlobal Diversities per Training"
            for key in self.global_diversity_per_generation:
                msg += "\n"+str(key)+": "+str(self.global_diversity_per_generation[key])
            if len(Config.RESTRICTIONS['used_diversities']) > 1:
                msg += "\n\nDiversity Type per Training: "+str(self.novelty_type_per_generation)
        
        if Config.USER['task'] == 'reinforcement' and Config.USER['reinforcement_parameters']['environment'] == 'poker':
            msg += "\n\n\n##### ACCUMULATIVE PERFORMANCE"
            for metric in self.individual_performance_in_last_generation:
                msg += "\n\n==="
                msg += "\nOverall Accumulative Results ("+str(metric)+"):"
                msg += "\n- Individual Team Performance: "+str(self.individual_performance_in_last_generation[metric])
                msg += "\n- Accumulative Team Performance: "+str(self.accumulative_performance_in_last_generation[metric])
                msg += "\n- Team ids: "+str(self.ids_for_acc_performance_in_last_generation[metric])
                
                for subdivision in self.individual_performance_per_label_in_last_generation[metric]:
                    msg += "\n---"
                    msg += "\nAccumulative Results ("+str(subdivision)+"):"
                    for key in self.individual_performance_per_label_in_last_generation[metric][subdivision]:
                        msg += "\n"+str(key)+":"
                        msg += "\n- Individual Team Performance: "+str(self.individual_performance_per_label_in_last_generation[metric][subdivision][key])
                        msg += "\n- Accumulative Team Performance: "+str(self.accumulative_performance_per_label_in_last_generation[metric][subdivision][key])
                        msg += "\n- Team ids: "+str(self.ids_for_acc_performance_per_label_in_last_generation[metric][subdivision][key])

        return msg