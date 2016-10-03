from ...config import Config

class PokerConfig():
    """
    
    """

    CONFIG = {
        'ranks': ['2', '3', '4', '5', '6', '7', '8', '9', 'T', 'J', 'Q', 'K', 'A'],
        'suits': ['s', 'd', 'h', 'c'],
        'inputs': [], # setup in poker environment
        'action_mapping': {0: 'f', 1: 'c', 2: 'r'},
        'inverted_action_mapping': {'f': 0, 'c': 1, 'r': 2},
        'small_bet': 10,
        'big_bet': 20,
        'positions': 2,
        'rule_based_opponents': ['loose_agressive', 'loose_passive', 'tight_agressive', 'tight_passive'],
        'point_cache_size': 100,
        'labels_per_subdivision': {
            'sbb_label': [0, 1, 2, 3, 4, 5, 6, 7, 8],
            'position': [0, 1],
            'sbb_sd': [0, 1, 2],
            'opponent': [], # setup in poker environment
        },
        'attributes_per_subdivision': {
            'sbb_label': lambda x: x.label_,
            'position': lambda x: x.players['team']['position'],
            'sbb_sd': lambda x: x.sbb_sd_label_,
            'opponent': lambda x: x.last_validation_opponent_id_,
        },
        'label_mapping': {'00': 0, '01': 1, '02': 2, '10': 3, '11': 4, '12': 5, '20': 6, '21': 7, '22': 8},
    }

    @staticmethod
    def get_hand_strength_label(value):
        # 10/30/60
        if value >= 9.0:
            return 0
        if value >= 6.0:
            return 1
        return 2