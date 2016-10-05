import numpy
from ..default_metrics import DefaultMetrics
from ...utils.helpers import round_value

class ClassificationMetrics(DefaultMetrics):

    def __init__(self, environment):
        self.environment_ = environment

    def metrics_for_team(self, team):
        msg = ""
        if team.extra_metrics_:
            msg += "\n\n### Classification-specific metrics for the best team:"
            msg += "\nrecall per action: "+str(team.extra_metrics_['recall_per_action'])
            msg += "\n\naccuracy: "+str(round_value(team.extra_metrics_['accuracy']))
            msg += "\n\nconfusion matrix:\n"+str(team.extra_metrics_['confusion_matrix'])
            if team.diversity_:
                msg += "\n\ndiversities:"
                for key, value in team.diversity_.iteritems():
                    msg += "\n - "+str(key)+": "+str(value)
        return msg

    def initialize_attributes_for_run_info(self, run_info):
        run_info.recall_per_validation_ = []

    def generate_output_for_attributes_for_run_info(self, run_info):
        msg = ""
        msg += "\n\n\n\n#################### Classification-specific Metrics:"
        msg += "\n\nBest Team Recall per Action per Validation: "+str(run_info.recall_per_validation_)
        return msg

    def quick_metrics(self):
        msg = ""
        msg += "\n### Dataset Info:"
        msg += "\ntotal inputs: "+str(self.environment_.total_inputs_)
        msg += "\ntotal actions: "+str(self.environment_.total_actions_)
        msg += "\nactions mapping: "+str(self.environment_.action_mapping_)
        msg += ("\nclass distribution (train set, "+str(len(self.environment_.train_population_))+" "
            "samples): "+str(self.environment_.trainset_class_distribution_))
        msg += ("\nclass distribution (test set, "+str(len(self.environment_.test_population_))+" "
            "samples): "+str(self.environment_.testset_class_distribution_))
        return msg

    def store_per_validation_metrics(self, run_info, best_team, teams_population, programs_population, 
        current_generation):
        super(ClassificationMetrics, self).store_per_validation_metrics(run_info, best_team, 
            teams_population, programs_population, current_generation)
        
        run_info.recall_per_validation_.append(best_team.extra_metrics_['recall_per_action'])

        older_teams = [team for team in teams_population if team.generation != current_generation]
        validation_score_mean = round_value(numpy.mean([team.score_testset_ for team in older_teams]))
        run_info.global_mean_validation_score_per_validation_.append(validation_score_mean)
        run_info.temp_info_['validation_score_mean'] = validation_score_mean