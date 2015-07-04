from SBB.sbb import SBB
from SBB.config import Config
from SBB.environments.poker.poker_environment import PokerEnvironment

if __name__ == "__main__":
    Config.check_parameters()
    SBB().run()