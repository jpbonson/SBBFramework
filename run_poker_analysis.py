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
    #         balanced=False, 
    #         player1_file_or_opponent_type=PokerBayesianTesterOpponent,
    #         player2_file_or_opponent_type=PokerTightPassiveOpponent,
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
        matches=1000, 
        balanced=True, 

        # player1_file_or_opponent_type="poker_analysis_files/best_team.json", 
        # player2_file_or_opponent_type=PokerBayesianOpponent,

        # player1_file_or_opponent_type=PokerBayesianOpponent, 
        # player2_file_or_opponent_type=PokerTightPassiveOpponent,

        player1_file_or_opponent_type="poker_analysis_files/best_team.json", 
        player2_file_or_opponent_type=PokerTightPassiveOpponent,

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
    team: 0.5074
    bayesian_paper: 0.
    bayesian_test: 0.5248

    LA (unbalanced)
    team: 0.
    bayesian_paper: 0.
    bayesian_test: 


    LP (balanced)
    team: 0.5351
    bayesian_paper: 0.
    bayesian_test: 0.5445

    LP (unbalanced)
    team: 0.
    bayesian_paper: 0.
    bayesian_test: 


    TA (balanced)
    team: 0.4979
    bayesian_paper: 0.5009
    bayesian_test: 0.

    TA (unbalanced)
    team: 0.
    bayesian_paper: 0.
    bayesian_test:


    TP (balanced)
    team: 0.5037
    bayesian_paper: 0.5010
    bayesian_test: 0.

    TP (unbalanced)
    team: 0.
    bayesian_paper: 0.
    bayesian_test: 
    """

    """
    LA
    c: 0.51
    r: 0.43
    f: 0.04

    c: 0.42
    r: 0.55
    f: 0.02

    c: 0.48
    r: 0.41
    f: 0.09

    c: 0.43
    r: 0.48
    f: 0.07

    c: 51+42+48+43=0.46
    r: 43+55+41+48=0.49
    f: 4+2+9+7=0.05


    LP
    c: 0.79
    r: 0.16
    f: 0.04

    c: 0.69
    r: 0.27
    f: 0.03

    c: 0.77
    r: 0.15
    f: 0.06

    c: 0.72
    r: 0.21
    f: 0.06

    c: 79+69+77+72=0.75
    r: 16+27+15+21=0.20
    f: 4+3+6+6=0.05


    TA

    c: 0.38
    r: 0.22
    f: 0.38

    c: 0.49
    r: 0.27
    f: 0.22

    c: 0.25
    r: 0.18
    f: 0.56

    c: 0.36
    r: 0.21
    f: 0.42

    c: 38+49+25+36=0.37
    r: 22+27+18+21=0.23
    f: 38+22+56+42=0.40


    TP

    c: 0.54
    r: 0.06
    f: 0.39

    c: 0.64
    r: 0.09
    f: 0.25

    c: 0.46
    r: 0.05
    f: 0.48

    c: 0.54
    r: 0.06
    f: 0.38

    c: 54+64+46+54=0.55
    r: 6+9+5+6=0.07
    f: 39+25+48+38=0.38

    """