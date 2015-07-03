import cProfile, pstats, StringIO
from SBB.sbb import SBB
from SBB.config import Config
from SBB.environments.poker.poker_environment import PokerEnvironment

if __name__ == "__main__":
    pr = cProfile.Profile()
    pr.run('SBB().run()')
    s = StringIO.StringIO()
    sortby = 'cumulative'
    ps = pstats.Stats(pr, stream=s).sort_stats(sortby)
    ps.print_stats()
    with open('code_profile.stats', 'w') as the_file:
        the_file.write(s.getvalue())
    s = StringIO.StringIO()
    sortby = 'time'
    ps = pstats.Stats(pr, stream=s).sort_stats(sortby)
    ps.print_stats()
    with open('code_profile_time.stats', 'w') as the_file:
        the_file.write(s.getvalue())