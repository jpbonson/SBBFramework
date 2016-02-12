import time
from SBB.environments.poker.poker_analysis.poker_analysis import PokerAnalysis
from SBB.environments.poker.poker_opponents import (PokerAlwaysCallOpponent, PokerAlwaysRaiseOpponent, 
    PokerLooseAgressiveOpponent, PokerLoosePassiveOpponent, PokerTightAgressiveOpponent, PokerTightPassiveOpponent,
    PokerBayesianTesterOpponent)
from SBB.utils.helpers import round_value

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
    PokerAnalysis().run(
        matches=1000, 
        balanced=True, 
        player1_file_or_opponent_type="poker_analysis_files/best_team.json", 
        # player1_file_or_opponent_type=PokerBayesianTesterOpponent,
        player2_file_or_opponent_type=PokerLooseAgressiveOpponent,
        player1_is_sbb = True,
        player2_is_sbb = False,
        generate_debug_files_per_match=False,
        debug_folder='poker_analysis_outputs/blah/',
        river_round_only = False,
        seed=1
    )
    elapsed_time = round_value((time.time() - start_time)/60.0)
    print("\nFinished, elapsed time: "+str(elapsed_time)+" mins")