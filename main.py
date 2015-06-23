from SBB.sbb import SBB
from SBB.config import Config
from SBB.environments.poker.poker_match import PokerMatch

if __name__ == "__main__":
    Config.check_parameters()
    SBB().run()
    # PokerMatch()._play_match()