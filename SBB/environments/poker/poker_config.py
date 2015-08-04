from opponent_model import OpponentModel
from match_state import MatchState

class PokerConfig():
    """
    
    """

    ACTION_MAPPING = {0: 'f', 1: 'c', 2: 'r'}
    INPUTS = MatchState.INPUTS+['chips']+OpponentModel.INPUTS
    RANKS = ['2', '3', '4', '5', '6', '7', '8', '9', 'T', 'J', 'Q', 'K', 'A']
    SUITS = ['s', 'd', 'h', 'c']
    HAND_STRENGHT_MEMORY = None
    HAND_PPOTENTIAL_MEMORY = None
    HAND_NPOTENTIAL_MEMORY = None
    CONFIG = {
        'acpc_path': "SBB/environments/poker/ACPC/",
        'available_ports': [],
        'small_bet': 10,
        'big_bet': 20,
        'positions': 2,
        'total_labels': 1, # TODO: temp
    }