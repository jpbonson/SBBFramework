from utils.helpers import round_array
from config import Config

class RunInfo:
    """
    Stores metrics for the runs.
    """

    def __init__(self, run_id):
        self.run_id = run_id
        self.elapsed_time = None
        self.best_team = None
        self.actions_distribution_in_last_generation = None
        self.teams_in_last_generation = []
        self.train_score_per_generation = []
        self.test_score_per_generation = []
        self.diversity_per_generation = []
        self.recall_per_generation = [] # only for classification task
        
    def __str__(self):
        msg = "RUN "+str(self.run_id)
        msg += "\n\n##### METRICS PER GENERATION"
        msg += "\n\nTrain Score per Generation: "+str(round_array(self.train_score_per_generation))
        msg += "\n\nTest Score per Generation: "+str(round_array(self.test_score_per_generation))
        for key in self.diversity_per_generation[0]:
            array = [item[key] for item in self.diversity_per_generation]
            msg += "\n\nGlobal Diversity per Generation ("+str(key)+"): "+str(array)
        if Config.USER['task'] == 'classification':
            msg += "\n\nRecall per Action per Generation: "+str(self.recall_per_generation)
        msg += "\n\n##### METRICS FOR THE LAST GENERATION"
        msg += "\n\nActions Distribution in the Last Generation: "+str(self.actions_distribution_in_last_generation)        
        return msg