import yappi
from SBB.sbb import SBB
from SBB.config import Config

if __name__ == "__main__":
    Config.check_parameters()
    if Config.USER['task'] == 'reinforcement' and Config.USER['reinforcement_parameters']['environment'] == 'poker':
        # The system is much slower without calling yappi first, it is
        # probably due to otimizations it does to the process management.
        # This 'workaround' is only necessary for the poker environment.
        yappi.start()
    SBB().run()