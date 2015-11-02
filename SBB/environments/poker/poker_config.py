from ...config import Config

class PokerConfig():
    """
    
    """

    CONFIG = {
        'ranks': ['2', '3', '4', '5', '6', '7', '8', '9', 'T', 'J', 'Q', 'K', 'A'],
        'suits': ['s', 'd', 'h', 'c'],
        'inputs': [], # setup in poker environment
        'action_mapping': {0: 'f', 1: 'c', 2: 'r'},
        'acpc_path': "SBB/environments/poker/ACPC/",
        'available_ports': [],
        'small_bet': 10,
        'big_bet': 20,
        'positions': 2,
        'rule_based_opponents': ['loose_agressive', 'loose_passive', 'tight_agressive', 'tight_passive'],
        'point_cache_size': 50,
        'labels_per_subdivision': {
            'sbb_label': [0, 1, 2],
            'sbb_extra_label': [0, 1, 2],
            'opp_label': [0, 1, 2],
            'opp_extra_label': [0, 1, 2],
            'position': [0, 1],
            'sbb_sd': [0, 1, 2],
            'opponent': [], # setup in poker environment
        },
        'attributes_per_subdivision': {
            'sbb_label': lambda x: x.label_,
            'sbb_extra_label': lambda x: x.sbb_extra_label_,
            'opp_label': lambda x: x.opp_label_,
            'opp_extra_label': lambda x: x.opp_extra_label_,
            'position': lambda x: x.position_,
            'sbb_sd': lambda x: x.sbb_sd_label_,
            'opponent': lambda x: x.last_validation_opponent_id_,
        },
        'main_subcategories': ['sbb_label', 'opp_label', 'position', 'opponent'],
    }

    @staticmethod
    def get_hand_strength_label(value):
        if Config.USER['reinforcement_parameters']['poker']['balance_based_on'] == 'pstr_ostr':
            if value >= 8.0:
                return 0
            if value >= 5.0:
                return 1
            return 2
        else:
            if value >= 9.0:
                return 0
            if value >= 7.0:
                return 1
            if value >= 4.0:
                return 2
            return 3