import os
from match_state import MatchState
from poker_config import PokerConfig
from opponent_model import OpponentModel
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

        self.team.action_sequence_['coding4'].append(str(self.point.seed_))
        self.team.action_sequence_['coding4'].append(str(self.point.players['team']['position']))

        self.opponent.initialize(self.point.seed_)
            
        ### Setup match
        if self.point.players['team']['position'] == 0:
            player_pos0 = self.team
            player_pos1 = self.opponent # dealer/button
            player_key_pos0 = 'team'
            player_key_pos1 = 'opponent'
            sbb_position = 0
            opponent_position = 1
        else:
            player_pos0 = self.opponent
            player_pos1 = self.team # dealer/button
            player_key_pos0 = 'opponent'
            player_key_pos1 = 'team'
            sbb_position = 1
            opponent_position = 0
        player_pos0_chips = 0.0
        player_pos1_chips = 0.0 # dealer/button
        pot = 0.0

        ### Apply blinds (forced bets made before the cards are dealt)
        # since it is a heads-up, the dealer posts the small blind, and the non-dealer places the big blind
        # The small blind is usually equal to half of the big blind. 
        # The big blind is equal to the minimum bet.
        match_state_pos0 = MatchState(self.point, player_key = player_key_pos0)
        match_state_pos1 = MatchState(self.point, player_key = player_key_pos1)
        big_blind = PokerConfig.CONFIG['small_bet']
        small_blind = big_blind/2.0
        player_pos0_chips -= big_blind
        pot += big_blind
        player_pos1_chips -= small_blind  # dealer/button
        pot += small_blind

        ### Starting match

        ### PREFLOP
        # The dealer acts first before the flop. After the flop, the dealer acts last.

        is_possible_to_act = True
        self.round_id = 0 
        self.rounds = [[], [], [], []]
        last_action = None
        current_index = 1
        players_info = {
            0: {
                'player': player_pos0,
                'match_state': match_state_pos0,
                'chips': player_pos0_chips,
            },
            1: {
                'player': player_pos1,
                'match_state': match_state_pos1,
                'chips': player_pos1_chips,
            }
        }
        opponent_index = {
            0: 1,
            1: 0,
        }
        bet = small_blind
        cont = 0
        while is_possible_to_act:
            cont += 1
            opponent_actions = players_info[opponent_index[current_index]]['match_state'].actions
            action = self._execute_player(players_info[current_index]['player'], 
                players_info[current_index]['match_state'], pot, bet, is_training, opponent_actions)
            self.rounds[self.round_id].append(action)

            # TODO: action modifies match
            if action == 'f':
                players_info[opponent_index[current_index]]['chips'] += pot
                break
            elif action == 'c':
                pass
            elif action == 'r':
                pass
            else:
                raise ValueError("Invalid action.")

            current_index = opponent_index[current_index]

            if cont > 3:
                break

        # rounds 0 e 1: bet = small_bet
        # rounds 2 e 3: bet = big_bet
        # round 3: showdown

        # raise only:
        # 0:rrrc/rrrrc/rrrrc/rrrrc:Js2c|5cTh/4c3hTs/4h/Qs:-240|240:sbb|opponent
        # folding at the start:
        # 0:f:Js6c|7d3c:5|-5:opponent|sbb
        # 0:rf:8s2c|Ah2h:-10|10:sbb|opponent

        # update here for hall of fame (make these updates also for hall of fame)
        player_actions = players_info[opponent_index[sbb_position]]['match_state'].actions
        opponent_actions = players_info[opponent_index[opponent_position]]['match_state'].actions
        self._get_opponent_model_for_team().update_overall_agressiveness(self.round_id+1, player_actions, opponent_actions, self.point.label_)
        
        if is_training:
            points = OpponentModel.calculate_points(player_actions)
            hamming_label = self._quantitize_value(points)
            self.team.action_sequence_['coding3'].append(hamming_label)

        if Config.USER['reinforcement_parameters']['debug']['players']:
            debug_file_team.write("The end.\n\n")
            debug_file_opponent.write("The end.\n\n")
            if Config.USER['reinforcement_parameters']['debug']['print']:
                print "team: The end.\n"
                print "opponent: The end.\n"
            debug_file_team.close()
            debug_file_opponent.close()

        sbb_chips = players_info[sbb_position]['chips']
        opponent_chips = players_info[opponent_position]['chips']

        normalized_value = self._normalize_winning(float(sbb_chips))

        self._get_chips_for_team().append(normalized_value)
        # if opponent.opponent_id == "hall_of_fame": # update here for hall of fame
        #     self._get_chips_for_opponent().append(self._normalize_winning(float(opponent_chips)))

        if not is_training:
            if self.mode == Config.RESTRICTIONS['mode']['validation']:
                self._update_team_extra_metrics_for_poker(normalized_value, 'validation')
                self.point.last_validation_opponent_id_ = self.opponent.opponent_id
                if self.team.extra_metrics_['played_last_hand']:
                    self.team.extra_metrics_['hands_played_or_not_per_point'][self.point.point_id_] = 1.0
                    if normalized_value > 0.5:
                        self.team.extra_metrics_['hands_won_or_lost_per_point'][self.point.point_id_] = 1.0
                    else:
                        self.team.extra_metrics_['hands_won_or_lost_per_point'][self.point.point_id_] = 0.0
                else:
                    self.team.extra_metrics_['hands_played_or_not_per_point'][self.point.point_id_] = 0.0
                    self.team.extra_metrics_['hands_won_or_lost_per_point'][self.point.point_id_] = 0.0
            else:
                self._update_team_extra_metrics_for_poker(normalized_value, 'champion')

        if Config.USER['reinforcement_parameters']['debug']['print']:
            print "---"
            print "match: "+str(self.match_id)
            print "sbb_chips: "+str(sbb_chips)
            print "opponent_chips: "+str(opponent_chips)
            print "normalized_value: "+str(normalized_value)

        self.point.teams_results_.append(normalized_value)

        raise SystemError

        return normalized_value

    def _valid_actions(self):
        """
        
        """
        valid = [0, 1]

        # check if can raise
        if self.round_id == 0:
            max_raises = 3
        else:
            max_raises = 4
        raises = 0
        for action in self.rounds[self.round_id]:
            if action == 'r':
                raises += 1
        if raises < max_raises: 
            valid.append(2)
        return valid

    def _execute_player(self, player, match_state, pot, bet, is_training, opponent_actions):
        inputs = match_state.inputs(pot, bet, self.round_id)
        if match_state.player_key == 'team': # update here for hall of fame
            inputs += self._get_opponent_model_for_team().inputs(match_state.actions, opponent_actions)
        action = player.execute(self.point.point_id_, inputs, self._valid_actions(), is_training)

        if action is None:
            action = 1
        
        if match_state.player_key == 'team' and not is_training:
            if self.round_id > 0: # the player saw the flop
                player.extra_metrics_['played_last_hand'] = True
        if match_state.player_key == 'team' and is_training:
            player.action_sequence_['coding2'].append(str(action))

        action = PokerConfig.CONFIG['action_mapping'][action]

        if match_state.player_key == 'team' and is_training:
            player.action_sequence_['coding4'].append(str(self._quantitize_value(match_state.hand_strength[self.round_id], is_normalized = True)))
            player.action_sequence_['coding4'].append(str(self._quantitize_value(match_state.effective_potential[self.round_id], is_normalized = True)))
            player.action_sequence_['coding4'].append(str(action))

        match_state.actions.append(action)
        print str(inputs)
        print str(action)
        return action

    def _quantitize_value(value, is_normalized = False):
        if is_normalized:
            normalization_parameter = Config.RESTRICTIONS['multiply_normalization_by']
        else:
            normalization_parameter = 1.0
        if Config.RESTRICTIONS['diversity']['total_bins'] == 3:
            if value >= 0.0*normalization_parameter and value < 0.33*normalization_parameter:
                label = 0
            elif value >= 0.33*normalization_parameter and value < 0.66*normalization_parameter:
                label = 1
            else:
                label = 2
        else:
            raise ValueError("Invalid value for Config.RESTRICTIONS['diversity']['total_bins']")
        return label

    def _get_opponent_model_for_team(self):
        opponent_id = self.opponent.opponent_id # update here for hall of fame
        if opponent_id not in self.team.opponent_model:
            self.team.opponent_model[opponent_id] = OpponentModel()
        return self.team.opponent_model[opponent_id]

    def _get_chips_for_team(self):
        opponent_id = self.opponent.opponent_id # update here for hall of fame
        if opponent_id not in self.team.chips:
            self.team.chips[opponent_id] = []
        return self.team.chips[opponent_id]

    # @staticmethod
    # def _calculate_chips_input(player, opponent):
    #     chips = PokerPlayerExecution.get_chips(player, opponent)
    #     if len(chips) == 0:
    #         chips = 0.5
    #     else:
    #         chips = numpy.mean(chips)
    #     return chips

    def _normalize_winning(self, value):
        max_small_bet_turn_winning = PokerConfig.CONFIG['small_bet']*4
        max_big_bet_turn_winning = PokerConfig.CONFIG['big_bet']*4
        max_winning = max_small_bet_turn_winning*2 + max_big_bet_turn_winning*2
        max_losing = -max_winning
        return (value - max_losing)/float(max_winning - max_losing)

    def _update_team_extra_metrics_for_poker(self, normalized_value, mode_label):
        self.team.extra_metrics_['total_hands'][mode_label] += 1
        self.team.extra_metrics_['total_hands_per_point_type'][mode_label]['position'][self.point.players['team']['position']] += 1
        self.team.extra_metrics_['total_hands_per_point_type'][mode_label]['sbb_label'][self.point.label_] += 1
        self.team.extra_metrics_['total_hands_per_point_type'][mode_label]['sbb_sd'][self.point.sbb_sd_label_] += 1
        if self.team.extra_metrics_['played_last_hand']:
            self.team.extra_metrics_['hand_played'][mode_label] += 1
            self.team.extra_metrics_['hand_played_per_point_type'][mode_label]['position'][self.point.players['team']['position']] += 1
            self.team.extra_metrics_['hand_played_per_point_type'][mode_label]['sbb_label'][self.point.label_] += 1
            self.team.extra_metrics_['hand_played_per_point_type'][mode_label]['sbb_sd'][self.point.sbb_sd_label_] += 1
            if normalized_value > 0.5:
                self.team.extra_metrics_['won_hands'][mode_label] += 1
                self.team.extra_metrics_['won_hands_per_point_type'][mode_label]['position'][self.point.players['team']['position']] += 1
                self.team.extra_metrics_['won_hands_per_point_type'][mode_label]['sbb_label'][self.point.label_] += 1
                self.team.extra_metrics_['won_hands_per_point_type'][mode_label]['sbb_sd'][self.point.sbb_sd_label_] += 1