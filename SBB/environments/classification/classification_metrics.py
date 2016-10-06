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
        msg += "\n\nChampion Recall per Action per Validation: "+str(run_info.recall_per_validation_)
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

    def generate_overall_metrics_output(self, run_infos):  
        msg = super(ClassificationMetrics, self).generate_overall_metrics_output(run_infos)
        msg += self._generate_summary(run_infos)
        return msg

    def _generate_summary(self, run_infos): # Obs.: Everything here is duplicated code
        msg = "\n\n\n\n######### SUMMARY:"

        msg += "\n\n\n### Summary Per Run"

        best_scores = [run.global_mean_fitness_per_generation_[-1] for run in run_infos]
        msg += "\n\nGlobal Mean Fitness Score per Training per Run:"
        msg += "\n"+str(best_scores)
        msg += "\nmean: "+str(round_value(numpy.mean(best_scores)))

        best_scores = [run.global_max_fitness_per_generation_[-1] for run in run_infos]
        msg += "\n\nGlobal Max. Fitness Score per Training per Run:"
        msg += "\n"+str(best_scores)
        msg += "\nmean: "+str(round_value(numpy.mean(best_scores)))

        best_scores = [round_value(run.best_team_.score_champion_) for run in run_infos]
        msg += "\n\nChampion Score per Validation per Run:"
        msg += "\n"+str(best_scores)
        msg += "\nmean: "+str(round_value(numpy.mean(best_scores)))
        return msg