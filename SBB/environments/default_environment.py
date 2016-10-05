import abc
import numpy
from collections import Counter, defaultdict
from ..utils.helpers import round_value, flatten, round_array
from ..config import Config

def reset_points_ids():
    global next_point_id
    next_point_id = 0

def get_point_id():
    global next_point_id
    next_point_id += 1
    return next_point_id

class DefaultPoint(object):
    """
    Encapsulates a value from the environment as a point.
    """
    __metaclass__  = abc.ABCMeta

    def __init__(self):
        self.point_id_ = get_point_id()
        self.age_ = 0

    def __repr__(self): 
        return "("+str(self.point_id_)+")"

    def __str__(self): 
        return "("+str(self.point_id_)+")"

class DefaultEnvironment(object):
    """
    Abstract class for environments. All environments must implement these 
    methods to be able to work with SBB.
    """
    __metaclass__  = abc.ABCMeta

    @abc.abstractmethod
    def __init__(self):
        """
        Initialize the environment variables.
        """

    @abc.abstractmethod
    def point_population(self):
         """
         Return the point_population. If the Hall of Fame is being used, it will return 
         the point_population plus the hall_of_fame, since both were used during training.
         """

    @abc.abstractmethod
    def reset(self):
         """
         Method that is called at the beginning of each run by SBB, to reset the 
         variables that will be used by the generations.
         """

    @abc.abstractmethod
    def setup(self, teams_population):
         """
         Method that is called at the beginning of each generation by SBB, to set the 
         variables that will be used by the generationand remove the ones that are no 
         longer being used.
         """

    @abc.abstractmethod
    def evaluate_point_population(self, teams_population):
        """
        Evaluate the fitness of the point population, to define which points will be removed 
        or added in the next generation, when setup_point_population() is executed.
        """

    @abc.abstractmethod
    def evaluate_teams_population_for_training(self, teams_population):
        """
        Evaluate all the teams using the evaluate_team() method, and sets metrics. Used only 
        for training.
        """

    @abc.abstractmethod
    def evaluate_team(self, team, mode):
        """
        Evaluate the team using the environment inputs. May be executed in the training
        or the test mode.
        This method must set the attribute results_per_points of the team, if you intend to 
        use pareto.
        """

    @abc.abstractmethod
    def validate(self, current_generation, teams_population):
        """
        Return the best team for the teams_population using the validation set. It must 
        also set the team.score_testset_ and, if necessary, team.extra_metrics_
        """

    @abc.abstractmethod
    def metrics_for_team(self, team):
        """
        Generate a string with the metrics for the team specific of the environment.
        """

    @abc.abstractmethod
    def initialize_attributes_for_run_info(self, run_info):
        """
        Initialize the attributes in run_info, that will be the output at the end of the run.
        """

    @abc.abstractmethod
    def generate_output_for_attributes_for_run_info(self, run_info):
        """
        Generate an output of the attributes in run_info, to append it to the other results of the run.
        """

    @abc.abstractmethod
    def metrics(self):
        """
        Generate a string with the metrics for the environment. It is printed at the 
        start and at the end of the execution, and it is also saved in the output file.
        """

    def store_per_generation_metrics(self, run_info, teams_population, current_generation, previous_diversity):
        older_teams = [team for team in teams_population if team.generation != current_generation]
        mean_fitness = round_value(numpy.mean([team.fitness_ for team in older_teams]), 3)
        run_info.global_mean_fitness_per_generation_.append(mean_fitness)
        run_info.global_max_fitness_per_generation_.append(round_value(max([team.fitness_ for team in older_teams])))
        for diversity in Config.RESTRICTIONS['used_diversities']:
            run_info.global_diversity_per_generation_[diversity].append(round_value(numpy.mean([t.diversity_[diversity] for t in older_teams]), 3))
        if len(Config.RESTRICTIONS['used_diversities']) > 1 and previous_diversity:
            run_info.global_fitness_per_diversity_per_generation_[previous_diversity].append(mean_fitness)
            run_info.novelty_type_per_generation_.append(Config.RESTRICTIONS['used_diversities'].index(previous_diversity))
        if Config.USER['task'] == 'reinforcement':
            opponents = older_teams[0].extra_metrics_['training_opponents'].keys()
            for opponent in opponents:
                mean_fitness_per_opponent = round_value(numpy.mean([team.extra_metrics_['training_opponents'][opponent] for team in older_teams]), 3)
                run_info.global_fitness_per_opponent_per_generation_[opponent].append(mean_fitness_per_opponent)

    def print_and_store_per_validation_metrics(self, run_info, best_team, teams_population, programs_population, current_generation):
        print "\n\n>>>>> Generation: "+str(current_generation)+", run: "+str(run_info.run_id)
        run_info.train_score_per_validation_.append(best_team.fitness_)
        run_info.test_score_per_validation_.append(best_team.score_testset_)
        if Config.USER['task'] == 'classification':
            run_info.recall_per_validation_.append(best_team.extra_metrics_['recall_per_action'])
        print("\n### Best Team Metrics: "+best_team.metrics()+"\n")

        print "\n### Global Metrics:"

        older_teams = [team for team in teams_population if team.generation != current_generation]

        fitness_score_mean = round_value(numpy.mean([team.fitness_ for team in older_teams]))
        fitness_score_std = round_value(numpy.std([team.fitness_ for team in older_teams]))
        
        if Config.USER['task'] == 'reinforcement':
            validation_score_mean = round_value(numpy.mean([team.extra_metrics_['validation_score'] for team in older_teams]))
            opponent_means = {}
            for key in older_teams[0].extra_metrics_['validation_opponents']:
                opponent_means[key] = round_value(numpy.mean([t.extra_metrics_['validation_opponents'][key] for t in older_teams]))    
            if 'hall_of_fame' in best_team.extra_metrics_['champion_opponents']:
                opponent_means['hall_of_fame(champion)'] = best_team.extra_metrics_['champion_opponents']['hall_of_fame']
            run_info.global_mean_validation_score_per_validation_.append(validation_score_mean)
            run_info.global_max_validation_score_per_validation_.append(round_value(max([team.extra_metrics_['validation_score'] for team in older_teams])))
            run_info.global_opponent_results_per_validation_.append(opponent_means)               
            print "\nglobal validation score (mean): "+str(validation_score_mean)+"\n"
            run_info.final_teams_validations_ = [team.extra_metrics_['validation_score'] for team in older_teams]
        if Config.USER['task'] == 'classification':
            validation_score_mean = round_value(numpy.mean([team.score_testset_ for team in older_teams]))
            run_info.global_mean_validation_score_per_validation_.append(validation_score_mean)
            print "\nglobal validation score (mean): "+str(validation_score_mean)+"\n"

        for key in best_team.diversity_:
            run_info.global_diversity_per_validation_[key].append(run_info.global_diversity_per_generation_[key][-1])
            print str(key)+": "+str(best_team.diversity_[key])+" (global: "+str(run_info.global_diversity_per_generation_[key][-1])+")"

        print "\nfitness, mean (global): "+str(fitness_score_mean)
        print "\nfitness, std (global): "+str(fitness_score_std)

        actions_distribution = Counter([p.action for p in programs_population])
        print "\nactions distribution: "+str(actions_distribution)
        actions_distribution_array = []
        for action in range(Config.RESTRICTIONS['total_actions']):
            if action in actions_distribution:
                actions_distribution_array.append(actions_distribution[action])
            else:
                actions_distribution_array.append(0)
        run_info.actions_distribution_per_validation_.append(actions_distribution_array)

        inputs_distribution_per_instruction = Counter()
        inputs_distribution_per_team = Counter()
        for team in older_teams:
            inputs_distribution_per_instruction.update(team.inputs_distribution())
            inputs_distribution_per_team.update(list(team.inputs_distribution()))
        inputs_distribution_per_instruction_array = []
        inputs_distribution_per_team_array = []
        for value in range(Config.RESTRICTIONS['total_inputs']):
            if value in inputs_distribution_per_instruction:
                inputs_distribution_per_instruction_array.append(inputs_distribution_per_instruction[value])
            else:
                inputs_distribution_per_instruction_array.append(0)
            if value in inputs_distribution_per_team:
                inputs_distribution_per_team_array.append(inputs_distribution_per_team[value])
            else:
                inputs_distribution_per_team_array.append(0)
        print "inputs distribution (global, per program): "+str(inputs_distribution_per_instruction_array)
        print "inputs distribution (global, per team): "+str(inputs_distribution_per_team_array)
        run_info.inputs_distribution_per_instruction_per_validation_.append(inputs_distribution_per_instruction_array)
        run_info.inputs_distribution_per_team_per_validation_.append(inputs_distribution_per_team_array)

        print
        print "Global Fitness (last 10 gen.): "+str(run_info.global_mean_fitness_per_generation_[-10:])
               
        if len(Config.RESTRICTIONS['used_diversities']) > 0:
            print "Global Diversity (last 10 gen.):"
            for diversity in Config.RESTRICTIONS['used_diversities']:
                print "- "+str(diversity)+": "+str(run_info.global_diversity_per_generation_[diversity][-10:])
        if len(Config.RESTRICTIONS['used_diversities']) > 1:
            print "Diversity Type (last 10 gen.): "+str(run_info.novelty_type_per_generation_[-10:])

        if Config.USER['task'] == 'reinforcement' and Config.USER['reinforcement_parameters']['environment'] == 'poker':
            self.calculate_poker_metrics_per_validation(run_info)
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
            
        if Config.USER['task'] == 'reinforcement' and Config.USER['reinforcement_parameters']['hall_of_fame']['enabled']:
            run_info.hall_of_fame_per_validation_.append([p.__repr__() for p in self.hall_of_fame()])
            print "\nHall of Fame: "+str(run_info.hall_of_fame_per_validation_[-1])

        avg_team_size = round_value(numpy.mean([len(team.programs) for team in older_teams]))
        avg_program_with_intros_size = round_value(numpy.mean(flatten([[len(program.instructions) for program in team.programs] for team in older_teams])))
        avg_program_without_intros_size = round_value(numpy.mean(flatten([[len(program.instructions_without_introns_) for program in team.programs] for team in older_teams])))
        run_info.mean_team_size_per_validation_.append(avg_team_size)
        run_info.mean_program_size_with_introns_per_validation_.append(avg_program_with_intros_size)
        run_info.mean_program_size_without_introns_per_validation_.append(avg_program_without_intros_size)
        print "\nMean Team Sizes: "+str(run_info.mean_team_size_per_validation_[-10:])
        print "Mean Program Sizes (with introns): "+str(run_info.mean_program_size_with_introns_per_validation_[-10:])
        print "Mean Program Sizes (without introns): "+str(run_info.mean_program_size_without_introns_per_validation_[-10:])

        print "\n<<<<< Generation: "+str(current_generation)+", run: "+str(run_info.run_id)

    def store_per_run_metrics(self, run_info, best_team, teams_population, pareto_front, current_generation):
        # to ensure validation metrics exist for all teams in the hall of fame
        if Config.USER['task'] == 'reinforcement' and Config.USER['reinforcement_parameters']['hall_of_fame']['enabled']:
            print "Validating hall of fame..."
            self.validate(current_generation, self.hall_of_fame())

        run_info.best_team_ = best_team
        for team in teams_population:
            if team.generation != current_generation:
                run_info.teams_in_last_generation_.append(team)
        run_info.pareto_front_in_last_generation_ = pareto_front
        run_info.hall_of_fame_in_last_generation_ = self.hall_of_fame()
        if Config.USER['task'] == 'reinforcement':
            self.calculate_final_validation_metrics(run_info, teams_population, current_generation)

    def generate_overall_metrics_output(self, run_infos):       
        msg = "\n\n\n#################### OVERALL RESULTS ####################"

        score_means, score_stds = self._process_scores([run.global_mean_validation_score_per_validation_ for run in run_infos])
        msg += "\n\nGlobal Mean Validation Score per Validation:"
        msg += "\nmean: "+str(score_means)
        msg += "\nstd. deviation: "+str(score_stds)

        if Config.USER['task'] == 'reinforcement':
            score_means, score_stds = self._process_scores([run.global_max_validation_score_per_validation_ for run in run_infos])
            msg += "\n\nGlobal Max. Validation Score per Validation:"
            msg += "\nmean: "+str(score_means)
            msg += "\nstd. deviation: "+str(score_stds)

        msg += "\n\nGlobal Diversities per Validation:"
        for key in Config.RESTRICTIONS['used_diversities']:
            score_means, score_stds = self._process_scores([run.global_diversity_per_validation_[key] for run in run_infos])
            msg += "\n- "+str(key)+":"
            msg += "\n- mean: "+str(score_means)
            msg += "\n- std. deviation: "+str(score_stds)

        if Config.USER['task'] == 'reinforcement':
            msg += "\n\nGlobal Fitness per Opponent per Training:"
            for key in self.opponent_names_for_training_:
                score_means, score_stds = self._process_scores([run.global_fitness_per_opponent_per_generation_[key] for run in run_infos])
                msg += "\n- "+str(key)+":"
                msg += "\n- mean: "+str(round_array(score_means, 2))
                msg += "\n- std. deviation: "+str(round_array(score_stds, 2))
            for run_id, run in enumerate(run_infos):
                valid_names = [t.__repr__() for t in run.hall_of_fame_in_last_generation_]
                for key in run.global_fitness_per_opponent_per_generation_.keys():
                    if key in valid_names:
                        msg += "\n- run "+str(run_id+1)+", "+str(key)+": "+str(run.global_fitness_per_opponent_per_generation_[key])

        score_means, score_stds = self._process_scores([run.test_score_per_validation_ for run in run_infos])
        msg += "\n\nBest Team Validation Score per Validation (champion):"
        msg += "\nmean: "+str(score_means)
        msg += "\nstd. deviation: "+str(score_stds)

        score_means, score_stds = self._process_scores([run.global_mean_fitness_per_generation_ for run in run_infos])
        msg += "\n\nGlobal Mean Fitness Score per Training:"
        msg += "\nmean: "+str(round_array(score_means, 3))
        msg += "\nstd. deviation: "+str(round_array(score_stds, 3))

        score_means, score_stds = self._process_scores([run.global_max_fitness_per_generation_ for run in run_infos])
        msg += "\n\nGlobal Max. Fitness Score per Training:"
        msg += "\nmean: "+str(round_array(score_means, 3))
        msg += "\nstd. deviation: "+str(round_array(score_stds, 3))

        if Config.USER['task'] == 'reinforcement':
            msg += "\n\nFinal Teams Validations: "+str(flatten([round_array(run.final_teams_validations_, 3) for run in run_infos]))
        
        if not Config.USER['advanced_training_parameters']['second_layer']['enabled']:
            score_means, score_stds = self._process_scores([run.actions_distribution_per_validation_[-1] for run in run_infos])
            msg += "\n\nDistribution of Actions per Validation (last gen.):"
            msg += "\nmean: "+str(round_array(score_means, 2))
            msg += "\nstd. deviation: "+str(round_array(score_stds, 2))
        score_means, score_stds = self._process_scores([run.inputs_distribution_per_instruction_per_validation_[-1] for run in run_infos])
        msg += "\nDistribution of Inputs per Validation (per program) (last gen.):"
        msg += "\nmean: "+str(round_array(score_means, 2))
        msg += "\nstd. deviation: "+str(round_array(score_stds, 2))
        score_means, score_stds = self._process_scores([run.inputs_distribution_per_team_per_validation_[-1] for run in run_infos])
        msg += "\nDistribution of Inputs per Validation (per team) (last gen.):"
        msg += "\nmean: "+str(round_array(score_means, 2))
        msg += "\nstd. deviation: "+str(round_array(score_stds, 2))

        msg += "\n\nMean Team Sizes (last gen.): "+str(numpy.mean([run.mean_team_size_per_validation_[-1] for run in run_infos]))
        msg += "\nMean Program Sizes (with introns) (last gen.): "+str(numpy.mean([run.mean_program_size_with_introns_per_validation_[-1] for run in run_infos]))
        msg += "\nMean Program Sizes (without introns) (last gen.): "+str(numpy.mean([run.mean_program_size_without_introns_per_validation_[-1] for run in run_infos]))
        
        msg += "\n"
        if Config.USER['task'] == 'reinforcement':
            msg += self._generate_overall_metrics_output_for_acc_curves(run_infos)

        msg += "\n\n######"

        final_scores = [run.global_mean_validation_score_per_validation_[-1] for run in run_infos]
        msg += "\n\nGlobal Mean Validation Score per Validation per Run: "+str(final_scores)
        msg += "\nmean: "+str(round_value(numpy.mean(final_scores)))
        msg += "\nstd. deviation: "+str(round_value(numpy.std(final_scores)))
        best_run = run_infos[final_scores.index(max(final_scores))]
        msg += "\nbest run: "+str(best_run.run_id)

        best_scores_per_runs = []
        for run in run_infos:
            best_scores_per_runs.append(round_value(run.best_team_.score_testset_))
        msg += "\n\nBest Team Validation Score per Validation per Run (champion): "+str(best_scores_per_runs)
        msg += "\nmean: "+str(round_value(numpy.mean(best_scores_per_runs)))
        msg += "\nstd. deviation: "+str(round_value(numpy.std(best_scores_per_runs)))
        scores = [run.best_team_.score_testset_ for run in run_infos]
        best_run = run_infos[scores.index(max(scores))]
        msg += "\nbest run: "+str(best_run.run_id)

        msg += "\n\n######"

        elapseds_per_run = [run.elapsed_time_ for run in run_infos]
        msg += "\n\nFinished execution, total elapsed time: "+str(round_value(sum(elapseds_per_run)))+" mins "
        msg += "(mean: "+str(round_value(numpy.mean(elapseds_per_run)))+", std: "+str(round_value(numpy.std(elapseds_per_run)))+")"
        return msg, best_scores_per_runs

    def _process_scores(self, score_per_generation_per_run):
        score_means = []
        score_stds = []
        for index in range(len(score_per_generation_per_run[0])):
            column = [row[index] for row in score_per_generation_per_run]
            score_means.append(round_value(numpy.mean(column)))
            score_stds.append(round_value(numpy.std(column)))
        return score_means, score_stds

    def _generate_overall_metrics_output_for_acc_curves(self, run_infos):
        msg = ""
        metric = "score"
        msg += "\nOverall Accumulative Results ("+str(metric)+"):"
        score_means, score_stds = self._process_scores([run.individual_performance_in_last_generation_[metric] for run in run_infos])
        msg += "\n- Individual Team Performance:"
        msg += "\nmean: "+str(round_array(score_means, 3))
        msg += "\nstd. deviation: "+str(round_array(score_stds, 3))
        score_means, score_stds = self._process_scores([run.accumulative_performance_in_last_generation_[metric] for run in run_infos])
        msg += "\n- Accumulative Team Performance:"
        msg += "\nmean: "+str(round_array(score_means, 3))
        msg += "\nstd. deviation: "+str(round_array(score_stds, 3))
        msg += "\n\nAccumulative Results per Run ("+str(metric)+"):"
        msg += "\nindividual_values = ["
        for run in run_infos:
            msg += "\n"+str(run.individual_performance_in_last_generation_[metric])+","
        msg += "\n]"
        msg += "\nacc_values = ["
        for run in run_infos:
            msg += "\n"+str(run.accumulative_performance_in_last_generation_[metric])+","
        msg += "\n]"
        return msg


    def hall_of_fame(self):
        return []