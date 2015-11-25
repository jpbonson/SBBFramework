import yappi
import time
from SBB.environments.poker.poker_analysis import PokerAnalysis
from SBB.environments.poker.poker_opponents import (PokerAlwaysCallOpponent, PokerAlwaysRaiseOpponent, 
    PokerLooseAgressiveOpponent, PokerLoosePassiveOpponent, PokerTightAgressiveOpponent, PokerTightPassiveOpponent)
from SBB.utils.helpers import round_value


if __name__ == "__main__":
    yappi.start()
    start_time = time.time()
    PokerAnalysis().run(
        matches=1000, 
        balanced=False, 
        team_file="poker_analysis_files/run1/pareto_front/json/(4131-99).json", 
        opponent_type=PokerLooseAgressiveOpponent,
        generate_debug_files_per_match=True,
        generate_debug_files_per_players=True,
        debug_folder='poker_analysis_outputs/run1/',
        seed=1
    )
    elapsed_time = round_value((time.time() - start_time)/60.0)
    print("\nFinished, elapsed time: "+str(elapsed_time)+" mins")