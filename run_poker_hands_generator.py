import time
from SBB.environments.poker.hand_generator.poker_hand_generator import generate_poker_hands
from SBB.utils.helpers import round_value


if __name__ == "__main__":
    start_time = time.time()
    generate_poker_hands(from_seed=20000, to_seed=25000)
    elapsed_time = round_value((time.time() - start_time)/60.0)
    print("\nFinished, elapsed time: "+str(elapsed_time)+" mins")