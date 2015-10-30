from SBB.sbb import SBB
from SBB.config import Config

if __name__ == "__main__":
    Config.check_parameters()
    SBB().run()