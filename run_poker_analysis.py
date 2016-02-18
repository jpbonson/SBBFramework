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


    pairs = list(itertools.combinations_with_replacement(range(0, 10), 2))
    pairs = filter(lambda x: x[0] <= x[1], pairs)
    results = []
    for alfa, beta in pairs:
        print str((alfa, beta))
        r = PokerAnalysis().run(
            matches=1000, 
            balanced=False, 
            player1_file_or_opponent_type=PokerBayesianTesterOpponent,
            player2_file_or_opponent_type=PokerTightPassiveOpponent,
            player1_is_sbb = True,
            player2_is_sbb = False,
            generate_debug_files_per_match=False,
            debug_folder='poker_analysis_outputs/blah/',
            river_round_only = False,
            seed=1,
            test_bayesian_alfa=alfa,
            test_bayesian_beta=beta,
        )
        results.append(r)
    print "\nresults: "+str(results)+"\n"
    max_value = max(results)
    max_index = results.index(max_value)
    print "first: "+str((results[max_index], pairs[max_index]))

    results.pop(max_index)
    pairs.pop(max_index)
    max_value = max(results)
    max_index = results.index(max_value)
    print "second: "+str((results[max_index], pairs[max_index]))

    results.pop(max_index)
    pairs.pop(max_index)
    max_value = max(results)
    max_index = results.index(max_value)
    print "third: "+str((results[max_index], pairs[max_index]))


    # r = PokerAnalysis().run(
    #     matches=1000, 
    #     balanced=False, 

    #     # player1_file_or_opponent_type="poker_analysis_files/best_team.json", 
    #     # player2_file_or_opponent_type=PokerBayesianOpponent,

    #     player1_file_or_opponent_type=PokerBayesianOpponent, 
    #     player2_file_or_opponent_type=PokerTightPassiveOpponent,

    #     # player1_file_or_opponent_type="poker_analysis_files/best_team.json", 
    #     # player2_file_or_opponent_type=PokerTightPassiveOpponent,

    #     player1_is_sbb = True,
    #     player2_is_sbb = False,
    #     generate_debug_files_per_match=False,
    #     debug_folder='poker_analysis_outputs/blah/',
    #     river_round_only = False,
    #     seed=1,
    #     test_bayesian_alfa=None,
    #     test_bayesian_beta=None,
    # )

    elapsed_time = round_value((time.time() - start_time)/60.0)
    print("\nFinished, elapsed time: "+str(elapsed_time)+" mins")

    """ (4 bets)
    total = [sum([x[0] for x in r])/4.0, sum([x[1] for x in r])/4.0, sum([x[2] for x in r])/4.0]

    LA: LA/LP/TA/TP
    ['c', 'r', 'f']
    r = [
    [0.4816035145524437, 0.4814662273476112, 0.03693025809994509],
    [0.3661795928562508, 0.6113400774322468, 0.022480329711502434],
    [0.47613762486126526, 0.44006659267480575, 0.08379578246392896],
    [0.3988618727366787, 0.5344024831867563, 0.06673564407656493],
    ]
    total: [0.43, 0.517, 0.053]

    LP
    r = [
    [0.7873828692094497, 0.1767190180810347, 0.03589811270951564],
    [0.6581555518226104, 0.3114396102805308, 0.030404837896858727],
    [0.7699680511182109, 0.16892971246006389, 0.06110223642172524],
    [0.6970377019748654, 0.24461400359066426, 0.05834829443447038],
    ]
    [0.728, 0.225, 0.047]


    TA
    r = [
    [0.36879432624113473, 0.2789598108747045, 0.35224586288416077],
    [0.459552495697074, 0.3363166953528399, 0.20413080895008606],
    [0.2524271844660194, 0.21143473570658036, 0.5361380798274002],
    [0.34684684684684686, 0.2531531531531532, 0.4],
    ]
    [0.357, 0.270, 0.373]


    TP
    r = [
    [0.5705607476635514, 0.07757009345794393, 0.3518691588785047],
    [0.6404809619238477, 0.12104208416833667, 0.23847695390781562],
    [0.4816472694717995, 0.06535362578334826, 0.4529991047448523],
    [0.5414551607445008, 0.08037225042301184, 0.37817258883248733],
    ]
    [0.559, 0.086, 0.355]

    """

    """ (3 bets)
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