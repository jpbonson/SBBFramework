import numpy
from collections import defaultdict
from ..default_metrics import DefaultMetrics
from ...utils.helpers import round_value
from ...utils.helpers import round_value, round_array, flatten, accumulative_performances, rank_teams_by_accumulative_score
from ...config import Config

class ReinforcementMetrics(DefaultMetrics):

    def __init__(self, environment):
        self.environment_ = environment

    def metrics_for_team(self, team):
        msg = ""
        if team.extra_metrics_:
            msg += "\n\n### Reinforcement Learning-specific metrics for the best team:"
            if 'champion_score' in team.extra_metrics_:
                msg += ("\n\nscore per opponent (except hall of fame) (champion): "
                    ""+str(team.extra_metrics_['champion_score']))
                total_opponents = Config.USER['reinforcement_parameters']['environment_parameters']['validation_opponents_labels']+['hall_of_fame']
                for key in team.extra_metrics_['opponents']:
                    if key in total_opponents:
                        msg += "\n"+key+": "+str(team.extra_metrics_['champion_opponents'][key])

            if 'validation_score' in team.extra_metrics_:
                msg += "\n\nscore per opponent (validation): "+str(team.extra_metrics_['validation_score'])
                for key in team.extra_metrics_['validation_opponents']:
                    msg += "\n"+key+": "+str(team.extra_metrics_['validation_opponents'][key])
                    
            if 'training_opponents' in team.extra_metrics_:
                msg += "\n\nscore per opponent (training): "+str(round_value(team.fitness_))
                total_opponents = Config.USER['reinforcement_parameters']['environment_parameters']['training_opponents_labels']+['hall_of_fame']
                for key in team.extra_metrics_['training_opponents']:
                    if key in total_opponents:
                        msg += "\n"+key+": "+str(team.extra_metrics_['training_opponents'][key])
        return msg

    def initialize_attributes_for_run_info(self, run_info):
        run_info.global_max_validation_score_per_validation_ = []
        run_info.global_opponent_results_per_validation_ = []
        run_info.hall_of_fame_per_validation_ = []
        run_info.global_fitness_per_opponent_per_generation_ = defaultdict(list)
        run_info.final_teams_validations_ = []
        run_info.final_teams_validations_ids_ = []
        run_info.individual_performance_in_last_generation_ = defaultdict(list)
        run_info.accumulative_performance_in_last_generation_ = defaultdict(list)
        run_info.ids_for_acc_performance_in_last_generation_ = defaultdict(list)
        run_info.accumulative_performance_summary_ = {}

    def generate_output_for_attributes_for_run_info(self, run_info):
        msg = ""
        msg += "\n\n\n\n#################### Reinforcement Learning-specific Metrics:"

        msg += "\n\n\n##### GLOBAL METRICS PER VALIDATION"

        msg += "\n\nGlobal Max. Validation Score per Validation: "+str(run_info.global_max_validation_score_per_validation_)
        
        msg += "\n\nGlobal Opponent Results per Validation"
        for key in run_info.global_opponent_results_per_validation_[-1]:
            msg += "\n - "+str(key)+": "+str([item[key] if key in item else 0.0 for item in run_info.global_opponent_results_per_validation_])
        
        if Config.USER['reinforcement_parameters']['hall_of_fame']['enabled']:
            msg += "\n\nHall of Fame per Validation: "+str(run_info.hall_of_fame_per_validation_)


        msg += "\n\n\n##### GLOBAL METRICS PER TRAINING"

        msg += "\n\nGlobal Fitness Score per Training (per opponent):"
        msg += "\n - predefined:"
        for opponent in self.environment_.opponent_names_for_training_:
            msg += "\n    - "+str(opponent)+": "+str(run_info.global_fitness_per_opponent_per_generation_[opponent])

        if Config.USER['reinforcement_parameters']['hall_of_fame']['enabled']:
            msg += "\n - hall of fame:"
            hall_of_fame = [x for x in run_info.global_fitness_per_opponent_per_generation_ if x not in self.environment_.opponent_names_for_training_]
            for key in hall_of_fame:
                msg += "\n    - "+str(key)+": "+str(run_info.global_fitness_per_opponent_per_generation_[key])


        msg += "\n\n\n##### FINAL TEAMS METRICS"

        msg += "\n\nFinal Teams Validations: "+str(run_info.final_teams_validations_)
        msg += "\nFinal Teams Ids: "+str(run_info.final_teams_validations_ids_)
        

        msg += "\n\n\n##### ACCUMULATIVE PERFORMANCES"

        for metric in run_info.individual_performance_in_last_generation_:
            msg += "\n\nOverall Accumulative Results ("+str(metric)+"):"
            msg += "\n- Individual Team Performance: "+str(run_info.individual_performance_in_last_generation_[metric])
            msg += "\n- Accumulative Team Performance: "+str(run_info.accumulative_performance_in_last_generation_[metric])
            msg += "\n- Team ids: "+str(run_info.ids_for_acc_performance_in_last_generation_[metric])

        
        msg += "\n\n\n##### TEAMS RANKED BY ACCUMULATIVE PERFORMANCE"

        msg += "\n\nTeams Ranked by Accumulative Score per Metric"
        for metric in run_info.accumulative_performance_summary_:
            msg += "\n - metric: "+str(metric)+" (len: "+str(len(run_info.accumulative_performance_summary_[metric]['overall']['ids_only']))+"):"
            msg += "\n    - Rank: "+str(run_info.accumulative_performance_summary_[metric]['overall']['rank'])
            msg += "\n    - Team ids: "+str(run_info.accumulative_performance_summary_[metric]['overall']['ids_only'])

        return msg

    def quick_metrics(self):
        msg = ""
        msg += "\n### Environment Info:"
        msg += "\ntotal inputs: "+str(self.environment_.total_inputs_)
        msg += "\ntotal actions: "+str(self.environment_.total_actions_)
        msg += "\ntraining opponents: "+str(self.environment_.opponent_names_for_training_)
        return msg

    def store_per_generation_metrics(self, run_info, teams_population, current_generation, previous_diversity):
        super(ReinforcementMetrics, self).store_per_generation_metrics(run_info, teams_population, current_generation, previous_diversity)
        older_teams = [team for team in teams_population if team.generation != current_generation]
        opponents = older_teams[0].extra_metrics_['training_opponents'].keys()
        for opponent in opponents:
            mean_fitness_per_opponent = round_value(numpy.mean([team.extra_metrics_['training_opponents'][opponent] for team in older_teams]), 3)
            run_info.global_fitness_per_opponent_per_generation_[opponent].append(mean_fitness_per_opponent)

    def store_per_validation_metrics(self, run_info, best_team, teams_population, programs_population, current_generation):
        super(ReinforcementMetrics, self).store_per_validation_metrics(run_info, best_team, teams_population, programs_population, current_generation)
        older_teams = [team for team in teams_population if team.generation != current_generation]
        validation_score_mean = round_value(numpy.mean([team.extra_metrics_['validation_score'] for team in older_teams]))
        run_info.temp_info_['validation_score_mean'] = validation_score_mean
        opponent_means = {}
        for key in older_teams[0].extra_metrics_['validation_opponents']:
            opponent_means[key] = round_value(numpy.mean([t.extra_metrics_['validation_opponents'][key] for t in older_teams]))    
        if 'hall_of_fame' in best_team.extra_metrics_['champion_opponents']:
            opponent_means['hall_of_fame(champion)'] = best_team.extra_metrics_['champion_opponents']['hall_of_fame']
        run_info.global_mean_validation_score_per_validation_.append(validation_score_mean)
        run_info.global_max_validation_score_per_validation_.append(round_value(max([team.extra_metrics_['validation_score'] for team in older_teams])))
        run_info.global_opponent_results_per_validation_.append(opponent_means)               
        run_info.final_teams_validations_ = [team.extra_metrics_['validation_score'] for team in older_teams]

        if Config.USER['reinforcement_parameters']['hall_of_fame']['enabled']:
            run_info.hall_of_fame_per_validation_.append([p.__repr__() for p in self.environment_.hall_of_fame()])

    def print_per_validation_metrics(self, run_info, best_team, current_generation):
        super(ReinforcementMetrics, self).print_per_validation_metrics(run_info, best_team, current_generation)
        if Config.USER['reinforcement_parameters']['hall_of_fame']['enabled']:
            print "\nHall of Fame: "+str(run_info.hall_of_fame_per_validation_[-1])

    def store_per_run_metrics(self, run_info, best_team, teams_population, pareto_front, current_generation):
        super(ReinforcementMetrics, self).store_per_run_metrics(run_info, best_team, teams_population, pareto_front, current_generation)
        
        self._calculate_accumulative_performances(run_info, teams_population, current_generation)
        self._summarize_accumulative_performances(run_info)
        self._generate_second_layer_files(run_info, teams_population)
        
        older_teams = [team for team in teams_population if team.generation != current_generation]
        run_info.final_teams_validations_ids_ = [team.__repr__() for team in older_teams]

        # to ensure validation metrics exist for all teams in the hall of fame
        if Config.USER['reinforcement_parameters']['hall_of_fame']['enabled']:
            print "Validating hall of fame..."
            self.environment_.validate(current_generation, self.environment_.hall_of_fame())

    def _calculate_accumulative_performances(self, run_info, teams_population, current_generation):
        older_teams = [team for team in teams_population if team.generation != current_generation]
        metric = 'score'
        sorting_criteria = lambda x: x.extra_metrics_['validation_score']
        get_results_per_points = lambda x: x.results_per_points_for_validation_
        point_ids = [point.point_id_ for point in self.environment_.validation_point_population_]
        individual_performance, accumulative_performance, teams_ids = accumulative_performances(older_teams, point_ids, sorting_criteria, get_results_per_points)
        run_info.individual_performance_in_last_generation_[metric] = individual_performance
        run_info.accumulative_performance_in_last_generation_[metric] = accumulative_performance
        run_info.ids_for_acc_performance_in_last_generation_[metric] = teams_ids

    def _summarize_accumulative_performances(self, run_info, metrics = ['score']):
        for metric in metrics:
            run_info.accumulative_performance_summary_[metric] = {}
            ind_score = run_info.individual_performance_in_last_generation_[metric]
            acc_score = run_info.accumulative_performance_in_last_generation_[metric]
            ids = run_info.ids_for_acc_performance_in_last_generation_[metric]
            rank = rank_teams_by_accumulative_score(ind_score, acc_score, ids)
            run_info.accumulative_performance_summary_[metric]['overall'] = {}
            run_info.accumulative_performance_summary_[metric]['overall']['rank'] = rank
            run_info.accumulative_performance_summary_[metric]['overall']['ids_only'] = sorted([r[0] for r in rank])

    def _generate_second_layer_files(self, run_info, teams_population):
        top5_overall_ids = [r[0] for r in run_info.accumulative_performance_summary_['score']['overall']['rank'][:5]]
        top10_overall_ids = [r[0] for r in run_info.accumulative_performance_summary_['score']['overall']['rank'][:10]]
        top15_overall_ids = [r[0] for r in run_info.accumulative_performance_summary_['score']['overall']['rank'][:15]]
        if len(top5_overall_ids) == 5:
            run_info.second_layer_files_['top5_overall'] = [t for t in teams_population if t.__repr__() in top5_overall_ids]
        if len(top5_overall_ids) == 10:
            run_info.second_layer_files_['top10_overall'] = [t for t in teams_population if t.__repr__() in top10_overall_ids]
        if len(top5_overall_ids) == 15:
            run_info.second_layer_files_['top15_overall'] = [t for t in teams_population if t.__repr__() in top15_overall_ids]
        run_info.second_layer_files_['all'] = teams_population

    def generate_overall_metrics_output(self, run_infos):  
        msg, best_scores_per_runs = super(ReinforcementMetrics, self).generate_overall_metrics_output(run_infos)

        msg += "\n\n\n###### Reinforcement Learning-specific Metrics:"
        score_means, score_stds = self._process_scores([run.global_max_validation_score_per_validation_ for run in run_infos])
        msg += "\n\nGlobal Max. Validation Score per Validation:"
        msg += "\nmean: "+str(score_means)
        msg += "\nstd. deviation: "+str(score_stds)

        msg += "\n\nGlobal Fitness per Opponent per Training:"
        for key in self.environment_.opponent_names_for_training_:
            score_means, score_stds = self._process_scores([run.global_fitness_per_opponent_per_generation_[key] for run in run_infos])
            msg += "\n- "+str(key)+":"
            msg += "\n- mean: "+str(round_array(score_means, 2))
            msg += "\n- std. deviation: "+str(round_array(score_stds, 2))
        for run_id, run in enumerate(run_infos):
            valid_names = [t.__repr__() for t in run.hall_of_fame_in_last_generation_]
            for key in run.global_fitness_per_opponent_per_generation_.keys():
                if key in valid_names:
                    msg += "\n- run "+str(run_id+1)+", "+str(key)+": "+str(run.global_fitness_per_opponent_per_generation_[key])

        msg += "\n\nFinal Teams Validations: "+str(flatten([round_array(run.final_teams_validations_, 3) for run in run_infos]))

        msg += "\n"
        msg += self._generate_overall_metrics_output_for_acc_curves(run_infos)

        return msg, best_scores_per_runs