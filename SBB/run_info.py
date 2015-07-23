from utils.helpers import round_array
from config import Config

class RunInfo:
    """
    Stores metrics for the runs.
    """

    def __init__(self, run_id, seed):
        self.run_id = run_id
        self.seed = seed
        self.elapsed_time = None
        self.best_team = None
        self.actions_distribution_in_last_generation = {}
        self.inputs_distribution_in_last_generation = {}
        self.teams_in_last_generation = []
        self.hall_of_fame_in_last_generation = []
        self.pareto_front_in_last_generation = []
        self.individual_performance_in_last_generation = []
        self.accumulative_performance_in_last_generation = []
        self.worst_points_in_last_generation = []
        self.train_score_per_validation = []
        self.test_score_per_validation = []
        self.diversity_per_validation = []
        self.recall_per_validation = [] # only for classification task
        self.actions_distribution_per_validation = []
        self.info_per_team_per_generation = []
        
    def __str__(self):
        msg = "RUN "+str(self.run_id)+"\n"
        msg += "seed: "+str(self.seed)
        msg += "\n\n\n##### METRICS PER VALIDATION"
        msg += "\n\nFitness per Validation: "+str(round_array(self.train_score_per_validation))
        msg += "\n\nTest Score per Validation: "+str(round_array(self.test_score_per_validation))
        for key in self.diversity_per_validation[0]:
            array = [item[key] for item in self.diversity_per_validation]
            msg += "\n\nGlobal Diversity per Validation ("+str(key)+"): "+str(array)
        if Config.USER['task'] == 'classification':
            msg += "\n\nRecall per Action per Validation: "+str(self.recall_per_validation)
        msg += "\n\nActions Distribution per Validation: "+str(self.actions_distribution_per_validation)
        msg += "\n\n\n##### METRICS FOR THE LAST GENERATION"
        msg += "\n\nActions Distribution: "+str(self.actions_distribution_in_last_generation)
        msg += "\n\nInputs Distribution: "+str(self.inputs_distribution_in_last_generation)

        msg += "\n\nTotal Individual Team Performance: "+str(self.individual_performance_in_last_generation)
        msg += "\n\nTotal Accumulative Team Performance: "+str(self.accumulative_performance_in_last_generation)
        msg += "\n\n10% Worst Performed Against Points: "+str(self.worst_points_in_last_generation)
        return msg