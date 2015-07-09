import yappi
from SBB.sbb import SBB
from SBB.config import Config

# I don't know why, but the system is much slower without calling yappi first
# this 'workaround' is only necessary for the poker environment
if __name__ == "__main__":
    Config.check_parameters()
    yappi.start()
    SBB().run()