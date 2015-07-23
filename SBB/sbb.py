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
from environments.classification_environment import ClassificationEnvironment
from environments.tictactoe.tictactoe_environment import TictactoeEnvironment
if os.name == 'posix':
    from environments.poker.poker_environment import PokerEnvironment
from selection import Selection
from utils.helpers import round_value
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

    def run(self):
        print "\n### Starting pSBB"

        # 1. Initialize environment and the selection algorithm
        environment = self._initialize_environment()
        selection = Selection(environment)

        overall_info = ""
        overall_info += "\n### CONFIG: "+str(Config.USER)+"\n"
        overall_info += environment.metrics()
        overall_info += "\nSeeds per run: "+str(self.seeds_per_run_)
        print overall_info

        run_infos = []
        for run_id in range(Config.USER['training_parameters']['runs_total']):
            start_time = time.time()
            run_info = RunInfo(run_id+1, self.seeds_per_run_[run_id])
            print "\nStarting run: "+str(run_info.run_id)

            self._set_seed(run_info.seed)

            # 2. Randomly initialize populations
            self.current_generation_ = 0
            teams_population, programs_population = self._initialize_populations()
            
            environment.reset()
            while not self._stop_criterion():
                self.current_generation_ += 1
                
                if self.current_generation_ == 1 or self.current_generation_ % Config.USER['training_parameters']['validate_after_each_generation'] == 0:
                    validation = True
                else:
                    validation = False

                # 3. Selection
                teams_population, programs_population, pareto_front, diversity_means = selection.run(self.current_generation_, teams_population, programs_population, validation)

                # validation
                if not validation:
                    print ".",
                    sys.stdout.flush()
                else:
                    print "\n\n>>>>> Executing generation: "+str(self.current_generation_)+", run: "+str(run_info.run_id)
                    best_team = environment.validate(self.current_generation_, teams_population)

                    # store metrics
                    run_info.train_score_per_generation.append(best_team.fitness_)
                    run_info.test_score_per_generation.append(best_team.score_testset_)
                    run_info.diversity_per_generation.append(diversity_means)
                    if Config.USER['task'] == 'classification':
                        run_info.recall_per_generation.append(best_team.extra_metrics_['recall_per_action'])

                    # print metrics
                    print("\nbest team: "+best_team.metrics()+"\n")
                    for key in best_team.diversity_:
                        print str(key)+": "+str(best_team.diversity_[key])+" (global mean: "+str(diversity_means[key])+")"
                    actions_distribution = Counter([p.action for p in programs_population])
                    print "\nactions distribution: "+str(actions_distribution)+"\n"

            # store and print metrics per run
            print("\n########## "+str(run_info.run_id)+" Run's best team: "+best_team.metrics())
            run_info.elapsed_time = time.time() - start_time
            run_info.best_team = best_team
            run_info.actions_distribution_in_last_generation = actions_distribution
            run_info.inputs_distribution_in_last_generation = Counter()
            for team in teams_population:
                if team.generation != self.current_generation_:
                    run_info.teams_in_last_generation.append(team)
                    run_info.inputs_distribution_in_last_generation.update(team._inputs_distribution())
            run_info.pareto_front_in_last_generation = pareto_front
            run_info.hall_of_fame_in_last_generation = environment.hall_of_fame()
            if Config.USER['task'] == 'reinforcement':
                individual_performance, accumulative_performance, worst_points_info = self._calculate_accumulative_performance(environment, teams_population)
                run_info.individual_performance_in_last_generation = individual_performance
                run_info.accumulative_performance_in_last_generation = accumulative_performance
                run_info.worst_points_in_last_generation = worst_points_info
            print("\nFinished run "+str(run_info.run_id)+", elapsed time: "+str(run_info.elapsed_time)+" secs")
            run_infos.append(run_info)
            sys.stdout.flush()
        
        # 4. Finalize execution (get final metrics, print to output, print to file)
        overall_info += self._generate_overall_metrics_output(run_infos)
        print overall_info
        sys.stdout.flush()

        # to ensure validation metrics for all teams in the hall of fame
        if Config.USER['task'] == 'reinforcement' and Config.USER['reinforcement_parameters']['hall_of_fame']['enabled']:
            environment.validate(self.current_generation_, run_info.hall_of_fame_in_last_generation)

        if Config.RESTRICTIONS['write_output_files']:
            self._write_output_files(run_infos, overall_info)

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

    def _calculate_accumulative_performance(self, environment, teams_population):
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
        validation_population = environment.validation_population()
        worst_points_info = [str(point) for point in validation_population if point.point_id in worst_points_ids]
        return individual_performance, accumulative_performance, worst_points_info

    def _generate_overall_metrics_output(self, run_infos):       
        msg = "\n\n\n#################### OVERALL RESULTS ####################"
        score_per_run = []
        for run in run_infos:
            score_per_run.append(round_value(run.best_team.score_testset_))
        self.best_scores_per_runs_ = score_per_run
        msg += "\n\nTest Score per Run: "+str(score_per_run)
        msg += "\nmean: "+str(round_value(numpy.mean(score_per_run)))
        msg += "\nstd. deviation: "+str(round_value(numpy.std(score_per_run)))
        scores = [run.best_team.score_testset_ for run in run_infos]
        best_run = run_infos[scores.index(max(scores))]
        msg += "\nbest run: "+str(best_run.run_id)

        train_score_per_generations_per_runs = [run.train_score_per_generation for run in run_infos]
        score_means, score_stds = self._process_scores(train_score_per_generations_per_runs)
        msg += "\n\nTrain Score per Generation across Runs:"
        msg += "\nmean: "+str(score_means)
        msg += "\nstd. deviation: "+str(score_stds)

        test_score_per_generations_per_runs = [run.test_score_per_generation for run in run_infos]
        score_means, score_stds = self._process_scores(test_score_per_generations_per_runs)
        msg += "\n\nTest Score per Generation across Runs:"
        msg += "\nmean: "+str(score_means)
        msg += "\nstd. deviation: "+str(score_stds)

        diversities = set(Config.USER['advanced_training_parameters']['diversity']['use_and_show'] + Config.USER['advanced_training_parameters']['diversity']['only_show'])
        for diversity in diversities:
            array = [[generation[diversity] for generation in run.diversity_per_generation] for run in run_infos]
            score_means, score_stds = self._process_scores(array)
            msg += "\n\nMean Diversity per Generation across Runs ("+str(diversity)+"):"
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
        if not os.path.exists("outputs/"):
            os.makedirs("outputs/")
        localtime = time.localtime()
        pretty_localtime = str(localtime.tm_year)+"-"+str(localtime.tm_mon)+"-"+str(localtime.tm_mday)+"-"+str(localtime.tm_hour)+str(localtime.tm_min)+str(localtime.tm_sec)
        if Config.USER['task'] == 'classification':
            filename = Config.USER['classification_parameters']['dataset']
        else:
            filename = Config.USER['reinforcement_parameters']['environment']
        filepath = "outputs/"+str(filename)+"_"+pretty_localtime
        os.makedirs(filepath)
        with open(filepath+"/metrics_overall.txt", "w") as text_file:
            text_file.write(overall_info)
        for run in run_infos:
            path = filepath+"/run"+str(run.run_id)+"/"
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
        print "\n### Files saved at "+filepath+"\n"

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