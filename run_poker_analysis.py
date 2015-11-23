import yappi
from SBB.environments.poker.poker_analysis import PokerAnalysis

if __name__ == "__main__":
    yappi.start()
    # TODO: enable parameters
    PokerAnalysis().run()