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
        matches=100, 
        balanced=False, 
        team_file="poker_analysis_files/json/(3902-94).json", 
        opponent_type=PokerLooseAgressiveOpponent,
        generate_debug_files=True,
        debug_folder='poker_analysis_outputs/',
        seed=1
    )
    elapsed_time = round_value((time.time() - start_time)/60.0)
    print("\nFinished, elapsed time: "+str(elapsed_time)+" mins")