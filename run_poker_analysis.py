import time
from SBB.environments.poker.poker_analysis.poker_analysis import PokerAnalysis
from SBB.environments.poker.poker_opponents import (PokerAlwaysCallOpponent, PokerAlwaysRaiseOpponent, 
    PokerLooseAgressiveOpponent, PokerLoosePassiveOpponent, PokerTightAgressiveOpponent, PokerTightPassiveOpponent,
    PokerBayesianTesterOpponent, PokerBayesianOpponent)
from SBB.utils.helpers import round_value
import itertools

if __name__ == "__main__":
    start_time = time.time()
    # PokerAnalysis().run_for_all_opponents(
    #     matches=100, 
    #     balanced=True, 
    #     team_file="poker_analysis_files/best_team.json", 
    #     generate_debug_files_per_match=True,
    #     debug_folder='poker_analysis_outputs/best_team/',
    #     river_round_only = False,
    #     seed=1
    # )


    # pairs = list(itertools.combinations_with_replacement(range(0, 10), 2))
    # pairs = filter(lambda x: x[0] <= x[1], pairs)
    # results = []
    # for alfa, beta in pairs:
    #     print str((alfa, beta))
    #     r = PokerAnalysis().run(
    #         matches=1000, 
    #         balanced=True, 
    #         player1_file_or_opponent_type=PokerBayesianTesterOpponent,
    #         player2_file_or_opponent_type=PokerTightAgressiveOpponent,
    #         player1_is_sbb = True,
    #         player2_is_sbb = False,
    #         generate_debug_files_per_match=False,
    #         debug_folder='poker_analysis_outputs/blah/',
    #         river_round_only = False,
    #         seed=1,
    #         test_bayesian_alfa=alfa,
    #         test_bayesian_beta=beta,
    #     )
    #     results.append(r)
    # print "\nresults: "+str(results)+"\n"
    # max_value = max(results)
    # max_index = results.index(max_value)
    # print "first: "+str((results[max_index], pairs[max_index]))

    # results.pop(max_index)
    # pairs.pop(max_index)
    # max_value = max(results)
    # max_index = results.index(max_value)
    # print "second: "+str((results[max_index], pairs[max_index]))

    # results.pop(max_index)
    # pairs.pop(max_index)
    # max_value = max(results)
    # max_index = results.index(max_value)
    # print "third: "+str((results[max_index], pairs[max_index]))


    r = PokerAnalysis().run(
        matches=10000, 
        balanced=True, 

        player1_file_or_opponent_type="poker_analysis_files/best_team.json", 
        player2_file_or_opponent_type=PokerBayesianOpponent,

        # player1_file_or_opponent_type=PokerBayesianOpponent, 
        # player2_file_or_opponent_type=PokerTightPassiveOpponent,

        # player1_file_or_opponent_type="poker_analysis_files/best_team.json", 
        # player2_file_or_opponent_type=PokerTightPassiveOpponent,

        player1_is_sbb = True,
        player2_is_sbb = False,
        generate_debug_files_per_match=False,
        debug_folder='poker_analysis_outputs/blah/',
        river_round_only = False,
        seed=1,
        test_bayesian_alfa=None,
        test_bayesian_beta=None,
    )

    elapsed_time = round_value((time.time() - start_time)/60.0)
    print("\nFinished, elapsed time: "+str(elapsed_time)+" mins")

    """
    LA (balanced)
    team: 0.5021
    bayesian_paper: 0.5220
    bayesian_test: 

    LA (unbalanced)
    team: 0.5084
    bayesian_paper: 0.5174
    bayesian_test: 


    LP (balanced)
    team: 0.5155
    bayesian_paper: 0.5302
    bayesian_test: 

    LP (unbalanced)
    team: 0.5183
    bayesian_paper: 0.5245
    bayesian_test: 


    TA (balanced)
    team: 0.4855
    bayesian_paper: 0.4884
    bayesian_test: 

    TA (unbalanced)
    team: 0.5054
    bayesian_paper: 0.5048
    bayesian_test:


    TP (balanced)
    team: 0.4914
    bayesian_paper: 0.4902
    bayesian_test: 

    TP (unbalanced)
    team: 0.5083
    bayesian_paper: 0.5055
    bayesian_test: 
    """