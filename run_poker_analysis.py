import time
from SBB.environments.poker.poker_analysis.poker_analysis import PokerAnalysis
from SBB.environments.poker.poker_opponents import (PokerAlwaysCallOpponent, PokerAlwaysRaiseOpponent, 
    PokerLooseAgressiveOpponent, PokerLoosePassiveOpponent, PokerTightAgressiveOpponent, PokerTightPassiveOpponent,
    PokerBayesianTesterOpponent)
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

    # pairs = list(itertools.combinations_with_replacement(range(1, 10), 2))
    # results = []
    # for alfa, beta in pairs:
    #     print str((alfa, beta))
    #     r = PokerAnalysis().run(
    #         matches=1000, 
    #         balanced=True, 
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
    PokerLooseAgressiveOpponent (unbalanced)
    first: (0.51484722222222212, (4, 4)) [team: 0.5206, good]
    second: (0.51055555555555554, (3, 4))
    third: (0.51008333333333333, (3, 3))

    PokerLooseAgressiveOpponent (balanced)
    first: (0.50589478367256147, (5, 5)) [team: 0.5074, good]
    second: (0.50415693471249035, (4, 4))
    third: (0.50382326771215658, (6, 6))

    ###

    PokerLoosePassiveOpponent (unbalanced)
    first: (0.52508333333333324, (2, 5)) [team: 0.53602, good]
    second: (0.52458333333333329, (3, 5))
    third: (0.52427777777777784, (2, 4))

    PokerLoosePassiveOpponent (balanced)
    first: (0.51525136247358472, (3, 6)) [team: 0.53518, good]
    second: (0.51519575130686246, (3, 5))
    third: (0.51455622288955627, (4, 6))

    ###

    PokerTightAgressiveOpponent (unbalanced)
    first: (0.51559722222222215, (1, 1)) [team: 0.5080, bad] ???
    second: (0.51229166666666659, (2, 2))
    third: (0.51065277777777773, (1, 2))

    PokerTightAgressiveOpponent (balanced)
    first: (0.49984706929151368, (1, 1)) [team: 0.4979, bad] ???
    second: (0.49915192970748518, (2, 2))
    third: (0.4980119007896785, (3, 3))

    ###

    PokerTightPassiveOpponent (unbalanced)
    first: (0.51559722222222215, (1, 1)) [team: 0.5145, bad] ???
    second: (0.51229166666666659, (2, 2))
    third: (0.51215277777777768, (1, 2))

    PokerTightPassiveOpponent (balanced)
    first: (0.49990268045823594, (1, 1)) [team: 0.5037, good] ???
    second: (0.49920754087420754, (2, 2))
    third: (0.49806751195640075, (3, 3))

    """