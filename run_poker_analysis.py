import time
from SBB.environments.poker.poker_analysis.poker_analysis import PokerAnalysis
from SBB.environments.poker.poker_opponents import (PokerAlwaysCallOpponent, PokerAlwaysRaiseOpponent, 
    PokerLooseAgressiveOpponent, PokerLoosePassiveOpponent, PokerTightAgressiveOpponent, PokerTightPassiveOpponent)
from SBB.utils.helpers import round_value

if __name__ == "__main__":
    start_time = time.time()
    # PokerAnalysis().run_for_all_opponents(
    #     matches=300, 
    #     balanced=False, 
    #     team_file="poker_analysis_files/run1/pareto_front/json/(4131-99).json", 
    #     generate_debug_files_per_match=True,
    #     debug_folder='poker_analysis_outputs/run1/',
    #     seed=1
    # )
    PokerAnalysis().run(
        matches=10, 
        balanced=False, 
        team_file="poker_analysis_files/run1/pareto_front/json/(4131-99).json", 
        opponent_type=PokerAlwaysCallOpponent,
        generate_debug_files_per_match=False,
        debug_folder='poker_analysis_outputs/run1/',
        seed=1
    )
    elapsed_time = round_value((time.time() - start_time)/60.0)
    print("\nFinished, elapsed time: "+str(elapsed_time)+" mins")