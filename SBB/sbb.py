#!/usr/bin/env python
# encoding: utf-8
## vim:ts=4:et:nowrap

import random
import time
import os
import sys
import numpy
import operator
from collections import Counter
from run_info import RunInfo
from program import Program, reset_programs_ids
from team import Team, reset_teams_ids
from instruction import Instruction
from diversity_maintenance import DiversityMaintenance
from environments.classification_environment import ClassificationEnvironment
from environments.tictactoe.tictactoe_environment import TictactoeEnvironment
if os.name == 'posix':
    from environments.poker.poker_environment import PokerEnvironment
from selection import Selection
from utils.helpers import round_value, flatten
from config import Config

class SBB:
    """
    The main algorithm of SBB.
    """

    def __init__(self):
        self.current_generation_ = 0
        self.best_scores_per_runs_ = [] # used by tests
        if isinstance(Config.USER['advanced_training_parameters']['seed'], list):
            self.seeds_per_run_ = Config.USER['advanced_training_parameters']['seed']
        else:
            if not Config.USER['advanced_training_parameters']['seed']:
                Config.USER['advanced_training_parameters']['seed'] = random.randint(0, Config.RESTRICTIONS['max_seed'])
            random.seed(Config.USER['advanced_training_parameters']['seed'])
            self.seeds_per_run_ = []
            for index in range(Config.USER['training_parameters']['runs_total']):
                self.seeds_per_run_.append(random.randint(0, Config.RESTRICTIONS['max_seed']))
        Config.RESTRICTIONS['used_diversities'] = list(set(Config.USER['advanced_training_parameters']['diversity']['use_and_show'] + Config.USER['advanced_training_parameters']['diversity']['only_show']))
        Config.RESTRICTIONS['genotype_options']['total_registers'] = Config.RESTRICTIONS['genotype_options']['output_registers'] + Config.USER['advanced_training_parameters']['extra_registers']

    def run(self):
        print "\n### Starting pSBB"

        # initialize the environment and the selection algorithm
        self.environment = self._initialize_environment()
        self.selection = Selection(self.environment)

        overall_info = ""
        overall_info += "\n### CONFIG: "+str(Config.USER)+"\n"
        overall_info += self.environment.metrics()
        overall_info += "\nSeeds per run: "+str(self.seeds_per_run_)
        overall_info += "\nDiversities: "+str(Config.RESTRICTIONS['used_diversities'])
        print overall_info

        run_infos = []
        for run_id in range(Config.USER['training_parameters']['runs_total']):
            start_time = time.time()
            run_info = RunInfo(run_id+1, self.seeds_per_run_[run_id])
            print "\nStarting run: "+str(run_info.run_id)

            self._set_seed(run_info.seed)

            # randomly initialize populations
            self.current_generation_ = 0
            teams_population, programs_population = self._initialize_populations()
            
            self.environment.reset()
            while not self._stop_criterion():
                self.current_generation_ += 1
                
                if self.current_generation_ == 1 or self.current_generation_ % Config.USER['training_parameters']['validate_after_each_generation'] == 0:
                    validation = True
                else:
                    validation = False

                # selection
                teams_population, programs_population, pareto_front = self.selection.run(self.current_generation_, teams_population, programs_population, validation)

                # validation
                if not validation:
                    print ".",
                    sys.stdout.flush()
                    self._store_per_generation_metrics(run_info, teams_population)
                else:
                    best_team = self.environment.validate(self.current_generation_, teams_population)
                    self._store_per_generation_metrics(run_info, teams_population)
                    self._print_and_store_per_validation_metrics(run_info, best_team, teams_population, programs_population)

            # to ensure validation metrics exist for all teams in the hall of fame
            if Config.USER['task'] == 'reinforcement' and Config.USER['reinforcement_parameters']['hall_of_fame']['enabled']:
                print "Validating hall of fame:"
                self.environment.validate(self.current_generation_, self.environment.hall_of_fame())

            self._print_and_store_per_run_metrics(run_info, best_team, teams_population, pareto_front)
            run_info.elapsed_time = time.time() - start_time
            print("\nFinished run "+str(run_info.run_id)+", elapsed time: "+str(run_info.elapsed_time)+" secs")
            run_infos.append(run_info)
            sys.stdout.flush()
        
        # finalize execution (get final metrics, print to output, print to file)
        overall_info += self._generate_overall_metrics_output(run_infos)
        print overall_info
        sys.stdout.flush()

        if Config.RESTRICTIONS['write_output_files']:
            self.filepath_ = self._create_folder()
            self._write_output_files(run_infos, overall_info)
            self._save_teams_data_per_generation(run_infos)

    def _initialize_environment(self):
        if Config.USER['task'] == 'classification':
            return ClassificationEnvironment()
        if Config.USER['task'] == 'reinforcement':
            if Config.USER['reinforcement_parameters']['environment'] == 'tictactoe':
                return TictactoeEnvironment()
            if Config.USER['reinforcement_parameters']['environment'] == 'poker':
                return PokerEnvironment()
        raise ValueError("No environment exists for "+str(Config.USER['task']))

    def _set_seed(self, seed):
        random.seed(seed)
        numpy.random.seed(seed)

    def _create_folder(self):
        if not os.path.exists("outputs/"):
            os.makedirs("outputs/")
        localtime = time.localtime()
        pretty_localtime = str(localtime.tm_year)+"-"+str(localtime.tm_mon)+"-"+str(localtime.tm_mday)+"-"+str(localtime.tm_hour)+str(localtime.tm_min)+str(localtime.tm_sec)
        if Config.USER['task'] == 'classification':
            filename = Config.USER['classification_parameters']['dataset']
        else:
            filename = Config.USER['reinforcement_parameters']['environment']
        filepath = "outputs/"+str(filename)+"_"+pretty_localtime+"/"
        os.makedirs(filepath)
        return filepath

    def _initialize_populations(self):
        """
        Initialize a population of teams with ['team_size']['min'] unique random programs with distinct actions.
        Then randomly add already created programs to the teams.
        """
        if Config.USER['training_parameters']['team_size']['min'] > Config.RESTRICTIONS['total_actions']:
            raise ValueError("The team minimum size is lower than the total number of actions, it is not possible to initialize a distinct set of actions per team!")
        
        # randomly initialize teams with the minimum size
        reset_teams_ids()
        reset_programs_ids()
        teams_population = []
        programs_population = []
        for t in range(Config.USER['training_parameters']['populations']['teams']):
            available_actions = range(Config.RESTRICTIONS['total_actions'])
            programs = []
            for index in range(Config.USER['training_parameters']['team_size']['min']):
                program = self._initialize_random_program(available_actions)
                available_actions.remove(program.action)
                programs.append(program)
            team = Team(self.current_generation_, programs)
            teams_population.append(team)
            programs_population += programs

        # randomly add more already created programs to the teams
        if Config.USER['advanced_training_parameters']['run_initialization_step2']:
            programs_range = Config.USER['training_parameters']['team_size']['max'] - Config.USER['training_parameters']['team_size']['min']
            for team in teams_population:
                programs_to_add = random.randrange(0, programs_range+1)
                for index in range(programs_to_add):
                    program = random.choice(programs_population)
                    if program not in team.programs:
                        team._add_program(program)

        return teams_population, programs_population

    def _initialize_random_program(self, available_actions):
        instructions = []
        total_instructions = random.randrange(Config.USER['training_parameters']['program_size']['min'], Config.USER['training_parameters']['program_size']['max']+1)
        for i in range(total_instructions):
            instructions.append(Instruction())
        action = random.choice(available_actions)
        program = Program(self.current_generation_, instructions, action)
        return program

    def _stop_criterion(self):
        if self.current_generation_ == Config.USER['training_parameters']['generations_total']:
            return True
        return False

    def _print_and_store_per_validation_metrics(self, run_info, best_team, teams_population, programs_population):
        print "\n\n>>>>> Generation: "+str(self.current_generation_)+", run: "+str(run_info.run_id)
        run_info.train_score_per_validation.append(best_team.fitness_)
        run_info.test_score_per_validation.append(best_team.score_testset_)
        if Config.USER['task'] == 'classification':
            run_info.recall_per_validation.append(best_team.extra_metrics_['recall_per_action'])
        print("\n### Best Team Metrics: "+best_team.metrics()+"\n")

        older_teams = [team for team in teams_population if team.generation != self.current_generation_]

        DiversityMaintenance.calculate_diversities(older_teams, self.environment.point_population())
        diversity_means = {}
        for diversity in Config.RESTRICTIONS['used_diversities']:
            diversity_means[diversity] = round_value(numpy.mean([t.diversity_[diversity] for t in older_teams]))

        fitness_score_mean = round_value(numpy.mean([team.fitness_ for team in older_teams]))

        if Config.USER['task'] == 'reinforcement':
            validation_score_mean = round_value(numpy.mean([team.extra_metrics_['validation_score'] for team in older_teams]))
            opponent_means = {}
            for key in older_teams[0].extra_metrics_['validation_opponents']:
                opponent_means[key] = round_value(numpy.mean([t.extra_metrics_['validation_opponents'][key] for t in older_teams]))    
            if 'hall_of_fame' in best_team.extra_metrics_['champion_opponents']:
                opponent_means['hall_of_fame(champion)'] = best_team.extra_metrics_['champion_opponents']['hall_of_fame']
            run_info.global_validation_score_per_validation.append(validation_score_mean)
            run_info.global_opponent_results_per_validation.append(opponent_means)               
            print "score (validation): "+str(best_team.extra_metrics_['validation_score'])+" (global: "+str(validation_score_mean)+")"
            for key in best_team.extra_metrics_['validation_opponents']:
                print key+" (validation): "+str(best_team.extra_metrics_['validation_opponents'][key])+" (global: "+str(opponent_means[key])+")"
        if Config.USER['task'] == 'classification':
            validation_score_mean = round_value(numpy.mean([team.score_testset_ for team in older_teams]))
            run_info.global_validation_score_per_validation.append(validation_score_mean)

        print
        run_info.global_diversity_per_validation.append(diversity_means)
        for key in best_team.diversity_:
            print str(key)+": "+str(best_team.diversity_[key])+" (global: "+str(diversity_means[key])+")"

        print "\n### Global Metrics:"

        run_info.global_fitness_score_per_validation.append(fitness_score_mean)
        print "\nfitness (global): "+str(fitness_score_mean)

        actions_distribution = Counter([p.action for p in programs_population])
        print "\nactions distribution: "+str(actions_distribution)
        actions_distribution_array = []
        for action in range(Config.RESTRICTIONS['total_actions']):
            if action in actions_distribution:
                actions_distribution_array.append(actions_distribution[action])
            else:
                actions_distribution_array.append(0)
        run_info.actions_distribution_per_validation.append(actions_distribution_array)

        inputs_distribution = Counter()
        for team in older_teams:
            inputs_distribution.update(team._inputs_distribution())
        print "\ninputs distribution (global): "+str(inputs_distribution)
        inputs_distribution_array = []
        for value in range(Config.RESTRICTIONS['total_inputs']):
            if value in inputs_distribution:
                inputs_distribution_array.append(inputs_distribution[value])
            else:
                inputs_distribution_array.append(0)
        run_info.inputs_distribution_per_validation.append(inputs_distribution_array)

        print
        print "Global Fitness (last 10 gen.): "+str(run_info.global_fitness_per_generation[-10:])
        
        if Config.USER['task'] == 'reinforcement':
            print "Opponent Type (last 10 gen.): "+str(run_info.opponent_type_per_generation[-10:])
        
        if len(Config.RESTRICTIONS['used_diversities']) > 0:
            print "Global Diversity (last 10 gen.):"
            for diversity in Config.RESTRICTIONS['used_diversities']:
                print "- "+str(diversity)+": "+str(run_info.global_diversity_per_generation[diversity][-10:])
        if len(Config.RESTRICTIONS['used_diversities']) > 1:
            print "Diversity Type (last 10 gen.): "+str(run_info.novelty_type_per_generation[-10:])

        if Config.USER['task'] == 'reinforcement' and Config.USER['reinforcement_parameters']['environment'] == 'poker':
            self.environment.calculate_poker_metrics_per_validation(run_info)
            print
            print "Point Population Distribution per Validation (last gen.):"
            for attribute in run_info.point_population_distribution_per_validation:
                temp = []
                for key in run_info.point_population_distribution_per_validation[attribute]:
                    temp.append(str(key)+": "+str(run_info.point_population_distribution_per_validation[attribute][key][-1]))
                print "- "+str(attribute)+" = "+", ".join(temp)
            print
            print "Validation Population Distribution per Validation: "+str(run_info.validation_population_distribution_per_validation)
            print "Global Point Results per Validation: "
            for attribute in run_info.global_result_per_validation:
                temp = []
                for key in run_info.global_result_per_validation[attribute]:
                    temp.append(str(key)+": "+str(run_info.global_result_per_validation[attribute][key][-1]))
                print "- "+str(attribute)+" = "+", ".join(temp)
            print
            print "Champion Population Distribution per Validation: "+str(run_info.champion_population_distribution_per_validation)
            
        if Config.USER['task'] == 'reinforcement' and Config.USER['reinforcement_parameters']['hall_of_fame']['enabled']:
            run_info.hall_of_fame_per_validation.append([p.__repr__() for p in self.environment.hall_of_fame()])
            print "\nHall of Fame: "+str(run_info.hall_of_fame_per_validation[-1])
        print "\n<<<<< Generation: "+str(self.current_generation_)+", run: "+str(run_info.run_id)

    def _store_per_generation_metrics(self, run_info, teams_population):
        older_teams = [team for team in teams_population if team.generation != self.current_generation_]
        generation_info = []
        for team in older_teams:
            team_info = []
            team_info.append(round_value(team.fitness_, round_decimals_to = 3))
            team_info.append(round_value(team.score_testset_, round_decimals_to = 3))
            for diversity in Config.RESTRICTIONS['used_diversities']:
                if diversity in team.diversity_:
                    value = round_value(team.diversity_[diversity], round_decimals_to = 3)
                else:
                    value = 0.0
                team_info.append(value)
            generation_info.append(team_info)
        run_info.info_per_team_per_generation.append(generation_info)
        run_info.global_fitness_per_generation.append(round_value(numpy.mean([team.fitness_ for team in older_teams]), 3))
        for diversity in Config.RESTRICTIONS['used_diversities']:
            run_info.global_diversity_per_generation[diversity].append(round_value(numpy.mean([t.diversity_[diversity] for t in older_teams]), 3))
        if len(Config.RESTRICTIONS['used_diversities']) > 1 and self.selection.previous_diversity_:
            run_info.novelty_type_per_generation.append(Config.RESTRICTIONS['used_diversities'].index(self.selection.previous_diversity_))
        if Config.USER['task'] == 'reinforcement':
            run_info.opponent_type_per_generation.append(self.environment.opponent_population_.keys().index(self.environment.current_opponent_type_))
        if Config.USER['task'] == 'reinforcement' and Config.USER['reinforcement_parameters']['environment'] == 'poker':
            self.environment.calculate_poker_metrics_per_generation(run_info, self.current_generation_)

    def _print_and_store_per_run_metrics(self, run_info, best_team, teams_population, pareto_front):
        print("\n########## "+str(run_info.run_id)+" Run's best team: "+best_team.metrics())
        run_info.best_team = best_team
        for team in teams_population:
            if team.generation != self.current_generation_:
                run_info.teams_in_last_generation.append(team)
        run_info.pareto_front_in_last_generation = pareto_front
        run_info.hall_of_fame_in_last_generation = self.environment.hall_of_fame()
        if Config.USER['task'] == 'reinforcement':
            individual_performance, accumulative_performance, worst_points_info = self._calculate_accumulative_performance(teams_population)
            run_info.individual_performance_in_last_generation = individual_performance
            run_info.accumulative_performance_in_last_generation = accumulative_performance
            run_info.worst_points_in_last_generation = worst_points_info

    def _calculate_accumulative_performance(self, teams_population):
        older_teams = [team for team in teams_population if team.generation != self.current_generation_]
        sorted_teams = sorted(older_teams, key=lambda team: team.extra_metrics_['validation_score'], reverse = True) # better ones first
        individual_performance = []
        accumulative_performance = []
        best_results_per_point = dict(sorted_teams[0].results_per_points_for_validation_)
        for team in sorted_teams:
            total = 0.0
            for key, item in team.results_per_points_for_validation_.iteritems():
                total += item
                if item > best_results_per_point[key]:
                    best_results_per_point[key] = item
            individual_performance.append(total)
            accumulative_performance.append(sum(best_results_per_point.values()))
        worst_points = sorted(best_results_per_point.items(), key=operator.itemgetter(1), reverse = False)
        worst_points_ids = [point[0] for point in worst_points[:Config.USER['reinforcement_parameters']['validation_population']/10]]
        validation_population = self.environment.validation_population()
        worst_points_info = [str(point) for point in validation_population if point.point_id_ in worst_points_ids]
        return individual_performance, accumulative_performance, worst_points_info

    def _generate_overall_metrics_output(self, run_infos):       
        msg = "\n\n\n#################### OVERALL RESULTS ####################"
        msg += "\n\n\n##### BEST TEAM METRICS"
        score_per_run = []
        for run in run_infos:
            score_per_run.append(round_value(run.best_team.score_testset_))
        self.best_scores_per_runs_ = score_per_run
        msg += "\n\nBest Team Validation Score per Run: "+str(score_per_run)
        msg += "\nmean: "+str(round_value(numpy.mean(score_per_run)))
        msg += "\nstd. deviation: "+str(round_value(numpy.std(score_per_run)))
        scores = [run.best_team.score_testset_ for run in run_infos]
        best_run = run_infos[scores.index(max(scores))]
        msg += "\nbest run: "+str(best_run.run_id)

        score_means, score_stds = self._process_scores([run.train_score_per_validation for run in run_infos])
        msg += "\n\nBest Team Train Score per Validation across Runs:"
        msg += "\nmean: "+str(score_means)
        msg += "\nstd. deviation: "+str(score_stds)

        score_means, score_stds = self._process_scores([run.test_score_per_validation for run in run_infos])
        msg += "\n\nBest Team Validation Score per Validation across Runs:"
        msg += "\nmean: "+str(score_means)
        msg += "\nstd. deviation: "+str(score_stds)

        msg += "\n\n\n##### GLOBAL METRICS"
        final_scores = [run.global_validation_score_per_validation[-1] for run in run_infos]
        msg += "\n\nGlobal Validation Score per Run: "+str(final_scores)
        msg += "\nmean: "+str(round_value(numpy.mean(final_scores)))
        msg += "\nstd. deviation: "+str(round_value(numpy.std(final_scores)))
        best_run = run_infos[final_scores.index(max(final_scores))]
        msg += "\nbest run: "+str(best_run.run_id)

        score_means, score_stds = self._process_scores([run.global_fitness_score_per_validation for run in run_infos])
        msg += "\n\nGlobal Train Score per Validation across Runs:"
        msg += "\nmean: "+str(score_means)
        msg += "\nstd. deviation: "+str(score_stds)

        score_means, score_stds = self._process_scores([run.global_validation_score_per_validation for run in run_infos])
        msg += "\n\nGlobal Validation Score per Validation across Runs:"
        msg += "\nmean: "+str(score_means)
        msg += "\nstd. deviation: "+str(score_stds)

        for diversity in Config.RESTRICTIONS['used_diversities']:
            array = [[generation[diversity] for generation in run.global_diversity_per_validation] for run in run_infos]
            score_means, score_stds = self._process_scores(array)
            msg += "\n\nMean Diversity per Validation across Runs ("+str(diversity)+"):"
            msg += "\nmean: "+str(score_means)
            msg += "\nstd. deviation: "+str(score_stds)

        elapseds_per_run = [run.elapsed_time for run in run_infos]
        msg += "\n\nFinished execution, total elapsed time: "+str(round_value(sum(elapseds_per_run)))+" secs "
        msg += "(mean: "+str(round_value(numpy.mean(elapseds_per_run)))+", std: "+str(round_value(numpy.std(elapseds_per_run)))+")"
        return msg

    def _process_scores(self, score_per_generation_per_run):
        score_means = []
        score_stds = []
        for index in range(len(score_per_generation_per_run[0])):
            column = [row[index] for row in score_per_generation_per_run]
            score_means.append(round_value(numpy.mean(column)))
            score_stds.append(round_value(numpy.std(column)))
        return score_means, score_stds

    def _write_output_files(self, run_infos, overall_info):
        with open(self.filepath_+"metrics_overall.txt", "w") as text_file:
            text_file.write(overall_info)
        for run in run_infos:
            path = self.filepath_+"run"+str(run.run_id)+"/"
            os.makedirs(path)
            with open(path+"metrics.txt", "w") as text_file:
                text_file.write(str(run))
            with open(path+"best_team.txt", "w") as text_file:
                text_file.write(str(run.best_team))
            with open(path+"best_team.json", "w") as text_file:
                text_file.write(run.best_team.json())
            self._save_teams(run.teams_in_last_generation, path+"last_generation_teams/")
            self._save_teams(run.pareto_front_in_last_generation, path+"pareto_front/")
            self._save_teams(run.hall_of_fame_in_last_generation, path+"hall_of_fame/")
        print "\n### Files saved at "+self.filepath_+"\n"

    def _save_teams_data_per_generation(self, run_infos):
        for run_info in run_infos:
            path = self.filepath_+"run"+str(run_info.run_id)+"/metrics_per_generation/"
            os.makedirs(path)
            for generation_index, generation_info in enumerate(run_info.info_per_team_per_generation):
                filename = str(generation_index+1)+".gen"
                with open(path+filename, "w") as text_file:
                    for team_info in generation_info:
                        text_file.write(" ".join([str(info) for info in team_info])+"\n")     

    def _save_teams(self, teams, path):
        if len(teams) > 0:
            os.makedirs(path)
            json_path = path+"json/"
            os.makedirs(json_path)
            for team in teams:
                with open(path+team.__repr__()+".txt", "w") as text_file:
                    text_file.write(str(team))
                with open(json_path+team.__repr__()+".json", "w") as text_file:
                    text_file.write(team.json())