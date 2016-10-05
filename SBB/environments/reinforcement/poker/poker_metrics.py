import math
import numpy
from collections import defaultdict
from poker_config import PokerConfig
from ..reinforcement_metrics import ReinforcementMetrics
from ....utils.helpers import round_value, flatten
from ....config import Config

class PokerMetrics(ReinforcementMetrics):

    def __init__(self, environment):
        self.environment_ = environment

    def metrics_for_team(self, team):
        msg = ""
        msg += super(PokerMetrics, self).metrics_for_team(team)
        msg += "\n\n\n### Poker-specific metrics ###"
        
        if 'total_hands' in team.extra_metrics_:
            if team.extra_metrics_['total_hands']['validation'] > 0:
                msg += self._hand_player_metrics(team, 'validation')
            if 'champion' in team.extra_metrics_:
                if team.extra_metrics_['total_hands']['champion'] > 0:
                    msg += self._hand_player_metrics(team, 'champion')

        if 'agressiveness' in team.extra_metrics_:
            msg += "\n\nagressiveness: "+str(team.extra_metrics_['agressiveness'])
            msg += "\ntight_loose: "+str(team.extra_metrics_['tight_loose'])
            msg += "\npassive_aggressive: "+str(team.extra_metrics_['passive_aggressive'])
            msg += "\nbluffing: "+str(team.extra_metrics_['bluffing'])
            msg += "\nbluffing_only_raise: "+str(team.extra_metrics_['bluffing_only_raise'])
            msg += ("\nnormalized result (mean): "
                ""+str(round_value(numpy.mean(team.results_per_points_for_validation_.values()))))
            msg += ("\nnormalized result (std): "
                ""+str(round_value(numpy.std(team.results_per_points_for_validation_.values()))))

        if 'agressiveness_champion' in team.extra_metrics_:
            msg += ("\n\nagressiveness (champion): "
                ""+str(team.extra_metrics_['agressiveness_champion']))
            msg += "\ntight_loose (champion): "+str(team.extra_metrics_['tight_loose_champion'])
            msg += ("\npassive_aggressive (champion): "
                ""+str(team.extra_metrics_['passive_aggressive_champion']))
            msg += "\nbluffing (champion): "+str(team.extra_metrics_['bluffing_champion'])

        if 'validation_points' in team.extra_metrics_:
            msg += "\n\nscore per point (validation): "
            for key in team.extra_metrics_['validation_points']:
                msg += "\n"+key+": "+str(dict(team.extra_metrics_['validation_points'][key]))

        if 'champion_score' in team.extra_metrics_:
            msg += "\n\nscore per point (champion): "
            for key in team.extra_metrics_['champion_points']:
                msg += "\n"+key+": "+str(dict(team.extra_metrics_['champion_points'][key]))
        return msg

    def _hand_player_metrics(self, team, mode):
        msg = ""
        msg += "\n\nhands ("+mode+"):"
        a = round_value(team.extra_metrics_['hand_played'][mode]/float(team.extra_metrics_['total_hands'][mode]))
        b = None
        if team.extra_metrics_['hand_played'][mode] > 0:
            b = round_value(team.extra_metrics_['won_hands'][mode]/float(team.extra_metrics_['hand_played'][mode]))
        msg += "\ntotal: "+str(team.extra_metrics_['total_hands'][mode])+", played: "+str(a)+", won: "+str(b)
        for metric in team.extra_metrics_['total_hands_per_point_type'][mode]:
            for key in team.extra_metrics_['total_hands_per_point_type'][mode][metric]:
                a = team.extra_metrics_['total_hands_per_point_type'][mode][metric][key]
                b = None
                c = None
                if a > 0:
                    b = round_value(team.extra_metrics_['hand_played_per_point_type'][mode][metric][key]
                        /float(team.extra_metrics_['total_hands_per_point_type'][mode][metric][key]))
                    if team.extra_metrics_['hand_played_per_point_type'][mode][metric][key] > 0:
                        c = round_value(team.extra_metrics_['won_hands_per_point_type'][mode][metric][key]
                            /float(team.extra_metrics_['hand_played_per_point_type'][mode][metric][key]))
                msg += "\n"+str(metric)+", "+str(key)+" ("+str(a)+"): played: "+str(b)+", won: "+str(c)
        return msg

    def initialize_attributes_for_run_info(self, run_info):
        super(PokerMetrics, self).initialize_attributes_for_run_info(run_info)
        run_info.global_result_per_validation_ = defaultdict(dict)
        run_info.final_teams_validations_per_subcategory_ = defaultdict(dict)
        run_info.champion_population_distribution_per_validation_ = {}
        run_info.validation_population_distribution_per_validation_ = {}
        run_info.point_population_distribution_per_validation_ = defaultdict(dict)
        run_info.individual_performance_per_label_in_last_generation_ = defaultdict(dict)
        run_info.accumulative_performance_per_label_in_last_generation_ = defaultdict(dict)
        run_info.ids_for_acc_performance_per_label_in_last_generation_ = defaultdict(dict)

    def generate_output_for_attributes_for_run_info(self, run_info):
        msg = ""
        msg += super(PokerMetrics, self).generate_output_for_attributes_for_run_info(run_info)
        msg += "\n\n\n\n#################### Poker-specific Metrics:"

        msg += "\n\n\n##### GLOBAL METRICS PER VALIDATION"

        msg += "\n\nGlobal Team Results per Validation"
        msg += self._list_run_info_attributes(run_info.global_result_per_validation_)


        msg += "\n\n\n##### FINAL TEAMS METRICS"

        msg += "\n\nFinal Teams Validation per Subcategory"
        msg += self._list_run_info_attributes(run_info.final_teams_validations_per_subcategory_)


        msg += "\n\n\n##### DISTRIBUTION METRICS PER VALIDATION"

        msg += "\n\nPoints Distribution for the Champion Population"
        msg += self._list_run_info_attributes(run_info.champion_population_distribution_per_validation_)

        msg += "\n\nPoints Distribution for the Validation Population"
        msg += self._list_run_info_attributes(run_info.validation_population_distribution_per_validation_)

        msg += "\n\nPoints Distribution for the Training Population per Validation"
        msg += self._list_run_info_attributes(run_info.point_population_distribution_per_validation_)


        msg += "\n\n\n##### ACCUMULATIVE PERFORMANCES"
        for metric in run_info.individual_performance_in_last_generation_:
            msg += "\n\n\n=== metric: "+str(metric)
            for subdivision in run_info.individual_performance_per_label_in_last_generation_[metric]:
                msg += "\n---"
                msg += "\nAccumulative Results ("+str(subdivision)+"):"
                for key in run_info.individual_performance_per_label_in_last_generation_[metric][subdivision]:
                    msg += "\n - "+str(key)+":"
                    msg += "\n    - Individual Team Performance: "+str(run_info.individual_performance_per_label_in_last_generation_[metric][subdivision][key])
                    msg += "\n    - Accumulative Team Performance: "+str(run_info.accumulative_performance_per_label_in_last_generation_[metric][subdivision][key])
                    msg += "\n    - Team ids: "+str(run_info.ids_for_acc_performance_per_label_in_last_generation_[metric][subdivision][key])
        return msg

    def _list_run_info_attributes(self, run_info_attribute):
        msg = ""
        for attribute in run_info_attribute:
            msg += "\n - "+str(attribute)+":"
            for key in run_info_attribute[attribute]:
                msg += "\n    - "+str(key)+": "+str(run_info_attribute[attribute][key])
        return msg

    def quick_metrics(self):
        msg = ""
        msg += "\n### Environment Info:"
        msg += "\ntotal inputs: "+str(self.environment_.total_inputs_)
        msg += "\ninputs: "+str([str(index)+": "+value for index, value in enumerate(PokerConfig.CONFIG['inputs'])])
        msg += "\ntotal actions: "+str(self.environment_.total_actions_)
        msg += "\nactions mapping: "+str(PokerConfig.CONFIG['action_mapping'])
        msg += "\npositions: "+str(PokerConfig.CONFIG['positions'])
        msg += "\ntraining opponents: "+str(self.environment_.opponent_names_for_training_)
        msg += "\nvalidation opponents: "+str(self.environment_.opponent_names_for_validation_)
        if Config.USER['reinforcement_parameters']['hall_of_fame']['enabled']:
            msg += "\nhall of fame size: "+str(Config.USER['reinforcement_parameters']['hall_of_fame']['size'])
        return msg

    def store_per_validation_metrics(self, run_info, best_team, teams_population, programs_population, current_generation):
        super(PokerMetrics, self).store_per_validation_metrics(run_info, best_team, 
            teams_population, programs_population, current_generation)
        self._calculate_point_population_metrics_per_validation(run_info)
        self._calculate_validation_population_metrics_per_validation(run_info)

    def _calculate_point_population_metrics_per_validation(self, run_info):
        self._calculate_point_population_metric_per_validation(run_info, 
            lambda x: x.players['team']['position'], 'position', range(PokerConfig.CONFIG['positions']))
        self._calculate_point_population_metric_per_validation(run_info, 
            lambda x: x.label_, 'sbb_label', PokerConfig.CONFIG['labels_per_subdivision']['sbb_label'])
        self._calculate_point_population_metric_per_validation(run_info, 
            lambda x: x.sbb_sd_label_, 'sd_label', range(3))

    def _calculate_point_population_metric_per_validation(self, run_info, get_attribute, key, labels):
        for label in labels:
            total = len([point for point in self.environment_.point_population() if get_attribute(point) == label])
            if label not in run_info.point_population_distribution_per_validation_[key]:
                run_info.point_population_distribution_per_validation_[key][label] = []
            run_info.point_population_distribution_per_validation_[key][label].append(total)

    def _calculate_validation_population_metrics_per_validation(self, run_info):
        self._calculate_validation_population_metric_per_validation(run_info, 
            lambda x: x.players['team']['position'], 'position', range(PokerConfig.CONFIG['positions']))
        self._calculate_validation_population_metric_per_validation(run_info, 
            lambda x: x.label_, 'sbb_label', PokerConfig.CONFIG['labels_per_subdivision']['sbb_label'])
        self._calculate_validation_population_metric_per_validation(run_info, 
            lambda x: x.sbb_sd_label_, 'sd_label', range(3))

    def _calculate_validation_population_metric_per_validation(self, run_info, get_attribute, key, labels):
        point_per_distribution = {}
        for label in labels:
            point_per_distribution[label] = [point for point in self.environment_.validation_population() if get_attribute(point) == label]
        run_info.validation_population_distribution_per_validation_[key] = {}
        for label in labels:
            run_info.validation_population_distribution_per_validation_[key][label] = len(point_per_distribution[label])

        for label in labels:
            temp = flatten([point.teams_results_ for point in point_per_distribution[label]])
            if len(temp) > 0:
                means_per_position = round_value(numpy.mean(temp))
            else:
                means_per_position = 0.0
            if label not in run_info.global_result_per_validation_[key]:
                run_info.global_result_per_validation_[key][label] = []
            run_info.global_result_per_validation_[key][label].append(means_per_position)

        point_per_distribution = {}
        for label in labels:
            point_per_distribution[label] = [point for point in self.environment_.champion_population() if get_attribute(point) == label]
        run_info.champion_population_distribution_per_validation_[key] = {}
        for label in labels:
            run_info.champion_population_distribution_per_validation_[key][label] = len(point_per_distribution[label])

    def print_per_validation_metrics(self, run_info, best_team, current_generation):
        super(PokerMetrics, self).print_per_validation_metrics(run_info, best_team, current_generation)
        print
        print "Point Population Distribution per Validation (last gen.):"
        for attribute in run_info.point_population_distribution_per_validation_:
            temp = []
            for key in run_info.point_population_distribution_per_validation_[attribute]:
                temp.append(str(key)+": "+str(run_info.point_population_distribution_per_validation_[attribute][key][-1]))
            print "- "+str(attribute)+" = "+", ".join(temp)
        print
        print "Validation Population Distribution per Validation: "+str(run_info.validation_population_distribution_per_validation_)
        print "Global Point Results per Validation: "
        for attribute in run_info.global_result_per_validation_:
            temp = []
            for key in run_info.global_result_per_validation_[attribute]:
                temp.append(str(key)+": "+str(run_info.global_result_per_validation_[attribute][key][-1]))
            print "- "+str(attribute)+" = "+", ".join(temp)
        print
        print "Champion Population Distribution per Validation: "+str(run_info.champion_population_distribution_per_validation_)

    def store_per_run_metrics(self, run_info, best_team, teams_population, pareto_front, current_generation):
        super(PokerMetrics, self).store_per_run_metrics(run_info, best_team, teams_population, 
            pareto_front, current_generation)
        self._get_validation_scores_per_subcategory(run_info, teams_population, current_generation)

    def _get_validation_scores_per_subcategory(self, run_info, teams_population, current_generation):
        older_teams = [team for team in teams_population if team.generation != current_generation]
        run_info.final_teams_validations_ids_ = [team.__repr__() for team in older_teams]
        for subcategory in PokerConfig.CONFIG['labels_per_subdivision'].keys():
            for subdivision in PokerConfig.CONFIG['labels_per_subdivision'][subcategory]:
                run_info.final_teams_validations_per_subcategory_[subcategory][subdivision] = []
                for team in older_teams:
                    if subcategory == 'opponent':
                        scores = team.extra_metrics_['opponents'][subdivision]
                    else:
                        scores = team.extra_metrics_['points'][subcategory][subdivision]
                    mean_score = numpy.mean(scores)
                    if not math.isnan(mean_score):
                        mean_score = round_value(mean_score)
                    run_info.final_teams_validations_per_subcategory_[subcategory][subdivision].append(mean_score)