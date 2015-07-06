import StringIO
import yappi
from SBB.sbb import SBB
from SBB.config import Config
from SBB.environments.poker.poker_environment import PokerEnvironment

if __name__ == "__main__":
    Config.check_parameters()
    yappi.start()
    SBB().run()
    s = StringIO.StringIO()
    yappi.get_func_stats().print_all(out=s)
    with open('code_profile_yappi.stats', 'w') as the_file:
        the_file.write(s.getvalue())