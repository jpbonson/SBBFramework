import os
from match_state import MatchState
from poker_config import PokerConfig
from ...config import Config

class PokerMatch():

    def __init__(self, team, opponent, point, mode, match_id):
        self.team = team
        self.opponent = opponent
        self.point = point
        self.mode = mode
        self.match_id = match_id

    def run(self):
        ### Setup framework
        if self.mode == Config.RESTRICTIONS['mode']['training']:
            is_training = True
        else:
            is_training = False

        if Config.USER['reinforcement_parameters']['debug']['output_path'] is None:
            Config.USER['reinforcement_parameters']['debug']['output_path'] = 'SBB/environments/poker/logs/'

        if Config.USER['reinforcement_parameters']['debug']['matches']:
            if not os.path.exists(Config.USER['reinforcement_parameters']['debug']['output_path']+"match_output/"):
                os.makedirs(Config.USER['reinforcement_parameters']['debug']['output_path']+'match_output/')

        debug_file_team = None
        debug_file_opponent = None
        if Config.USER['reinforcement_parameters']['debug']['players']:
            if not os.path.exists(Config.USER['reinforcement_parameters']['debug']['output_path']+"players/"):
                os.makedirs(Config.USER['reinforcement_parameters']['debug']['output_path']+'players/')
            path = Config.USER['reinforcement_parameters']['debug']['output_path']+'players/player_'
            debug_file_team = open(path+str(self.team.team_id_)+'_'+str(self.match_id)+'.log','w')
            debug_file_opponent = open(path+str(self.opponent.opponent_id)+'_'+str(self.match_id)+'.log','w')
        if Config.USER['reinforcement_parameters']['debug']['print']:
            print "Setting up matches..."

        opponent_use_inputs = None
        if self.opponent.opponent_id == "hall_of_fame":
            opponent_use_inputs = 'all'
        if self.opponent.opponent_id in PokerConfig.CONFIG['rule_based_opponents']:
            opponent_use_inputs = 'rule_based_opponent'

        if not is_training:
            self.team.extra_metrics_['played_last_hand'] = False

        self.opponent.initialize(self.point.seed_)
            
        ### Setup match
        if self.point.players['team']['position'] == 0:
            player_pos0 = self.team
            player_pos1 = self.opponent # dealer/button
            player_key_pos0 = 'team'
            player_key_pos1 = 'opponent'
        else:
            player_pos0 = self.opponent
            player_pos1 = self.team # dealer/button
            player_key_pos0 = 'opponent'
            player_key_pos1 = 'team'
        player_pos0_chips = 0.0
        player_pos1_chips = 0.0 # dealer/button
        pot = 0.0

        ### Apply blinds (forced bets made before the cards are dealt)
        # since it is a heads-up, the dealer posts the small blind, and the non-dealer places the big blind
        # The small blind is usually equal to half of the big blind. 
        # The big blind is equal to the minimum bet.
        big_blind = PokerConfig.CONFIG['small_bet']
        small_blind = big_blind/2.0
        player_pos0_chips -= big_blind
        pot += big_blind
        player_pos1_chips -= small_blind  # dealer/button
        pot += small_blind

        ### Starting match

        ### PREFLOP
        # The dealer acts first before the flop. After the flop, the dealer acts last.

        chips = 0 # TODO
        pos0_match_state = MatchState(self.point, player_key = player_key_pos0)
        pos1_match_state = MatchState(self.point, player_key = player_key_pos1)
        is_possible_to_act = True
        while is_possible_to_act:
            bet = small_blind
            inputs = pos1_match_state.inputs(pot, bet, chips) # if is opponent, call simplified_inputs
            print str(inputs)
            bet = 0 # TODO
            inputs = pos0_match_state.inputs(pot, bet, chips) # if is opponent, call simplified_inputs
            print str(inputs)
            break

        # rounds 0 e 1: bet = small_bet
        # rounds 2 e 3: bet = big_bet

        # t1 = threading.Thread(target=PokerPlayerExecution.execute_player, args=[team, opponent, point, sbb_port, is_training, True, 'all', match_id])
        # t2 = threading.Thread(target=PokerPlayerExecution.execute_player, args=[opponent, team, point, opponent_port, False, False, opponent_use_inputs, match_id])
        
        # raise only:
        # 0:rrrc/rrrrc/rrrrc/rrrrc:Js2c|5cTh/4c3hTs/4h/Qs:-240|240:sbb|opponent
        # folding at the start:
        # 0:f:Js6c|7d3c:5|-5:opponent|sbb
        # 0:rf:8s2c|Ah2h:-10|10:sbb|opponent

        print "WORKING ON IT!"

        raise SystemError

        # score = out.split("\n")[1]
        # score = score.replace("SCORE:", "")
        # splitted_score = score.split(":")
        # scores = splitted_score[0].split("|")
        # players = splitted_score[1].split("|")

        # if players[0] == 'sbb':
        #     sbb_position = 0
        #     opponent_position = 1
        # else:
        #     sbb_position = 1
        #     opponent_position = 0

        # normalized_value = self._normalize_winning(float(scores[sbb_position]))

        # PokerPlayerExecution.get_chips(team, opponent).append(normalized_value)
        # if opponent.opponent_id == "hall_of_fame":
        #     PokerPlayerExecution.get_chips(opponent, team).append(self._normalize_winning(float(scores[opponent_position])))

        # if not is_training:
        #     if mode == Config.RESTRICTIONS['mode']['validation']:
        #         self._update_team_extra_metrics_for_poker(team, point, normalized_value, 'validation')
        #         point.last_validation_opponent_id_ = opponent.opponent_id
        #         if team.extra_metrics_['played_last_hand']:
        #             team.extra_metrics_['hands_played_or_not_per_point'][point.point_id_] = 1.0
        #             if normalized_value > 0.5:
        #                 team.extra_metrics_['hands_won_or_lost_per_point'][point.point_id_] = 1.0
        #             else:
        #                 team.extra_metrics_['hands_won_or_lost_per_point'][point.point_id_] = 0.0
        #         else:
        #             team.extra_metrics_['hands_played_or_not_per_point'][point.point_id_] = 0.0
        #             team.extra_metrics_['hands_won_or_lost_per_point'][point.point_id_] = 0.0
        #     else:
        #         self._update_team_extra_metrics_for_poker(team, point, normalized_value, 'champion')

        # if Config.USER['reinforcement_parameters']['debug']['matches']:
        #     print "---"
        #     print "match: "+str(match_id)
        #     print "scores: "+str(scores)
        #     print "players: "+str(players)
        #     print "normalized_value: "+str(normalized_value)

        # point.teams_results_.append(normalized_value)

        # team.action_sequence_['coding1'].append(str(point.seed_))
        # team.action_sequence_['coding1'].append(str(point.position_))
        # team.action_sequence_['coding4'].append(str(point.seed_))
        # team.action_sequence_['coding4'].append(str(point.position_))

        # return normalized_value