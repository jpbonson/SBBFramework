import os
from match_state import MatchState
from poker_config import PokerConfig
from opponent_model import OpponentModel
from ...core.diversity_maintenance import DiversityMaintenance
from ...utils.helpers import round_value
from ...config import Config

class PokerMatch():

    def __init__(self, team, opponent, point, mode, match_id):
        self.team = team
        self.opponent = opponent
        self.point = point
        self.mode = mode
        if mode == Config.RESTRICTIONS['mode']['training']:
            self.is_training = True
        else:
            self.is_training = False
        self.match_id = match_id
        self.opponent_indeces = {
            0: 1,
            1: 0,
        }
        self.players_info = {
            0: {
                'player': None,
                'match_state': None,
                'key': None,
                'chips': 0.0,
                'folded': False,
            },
            1: { # dealer/button
                'player': None,
                'match_state': None,
                'key': None,
                'chips': 0.0,
                'folded': False,
            }
        }
        self.pot = 0.0
        self._setup_debug_files()

    def _setup_debug_files(self):
        if Config.USER['debug']['output_path'] is None:
            Config.USER['debug']['output_path'] = 'SBB/environments/poker/logs/'

        self.debug_file = None
        if Config.USER['debug']['enabled']:
            path = Config.USER['debug']['output_path']+'matches_output/'
            if not os.path.exists(path):
                os.makedirs(path)
            filename = self.mode+"_"+str(self.match_id)+"_"+str(self.team.__repr__())
            self.debug_file = open(path+filename+'.log','w')

    def run(self):
        ### Setup helpers
        if not self.is_training:
            self.team.extra_metrics_['played_last_hand'] = True

        self.team.action_sequence_['encoding_custom_info_per_match'].append(str(self.point.seed_))
        self.team.action_sequence_['encoding_custom_info_per_match'].append(str(self.point.players['team']['position']))

        self.opponent.initialize(self.point.seed_)
            
        ### Setup match
        if self.point.players['team']['position'] == 0:
            self.players_info[0]['player'] = self.team
            self.players_info[0]['match_state'] = MatchState(self.point, player_key = 'team')
            self.players_info[0]['id'] = self.team.__repr__()
            self.players_info[0]['key'] = 'team'
            self.players_info[1]['player'] = self.opponent
            self.players_info[1]['match_state'] = MatchState(self.point, player_key = 'opponent')
            self.players_info[1]['id'] = self.opponent.opponent_id
            self.players_info[1]['key'] = 'opponent'
            sbb_position = 0
            opponent_position = 1
        else:
            self.players_info[1]['player'] = self.team
            self.players_info[1]['match_state'] = MatchState(self.point, player_key = 'team')
            self.players_info[1]['id'] = self.team.__repr__()
            self.players_info[1]['key'] = 'team'
            self.players_info[0]['player'] = self.opponent
            self.players_info[0]['match_state'] = MatchState(self.point, player_key = 'opponent')
            self.players_info[0]['id'] = self.opponent.opponent_id
            self.players_info[0]['key'] = 'opponent'
            sbb_position = 1
            opponent_position = 0

        if Config.USER['debug']['enabled']:
            self.debug_file.write("PokerSBB Game: Hold'em Limit\n")
            self.debug_file.write("Table '"+str(self.match_id)+"' 2-max Seat #2 is the button\n")
            m = "Seat 1: "+self.players_info[0]['id']+" ("+str(MatchState.maximum_winning())+" chips)"
            if sbb_position == 0:
                m += " [SBB]"
            self.debug_file.write(m+"\n")
            m = "Seat 2: "+self.players_info[1]['id']+" ("+str(MatchState.maximum_winning())+" chips)"
            if sbb_position == 1:
                m += " [SBB]"
            self.debug_file.write(m+"\n")

        ### Apply blinds (forced bets made before the cards are dealt)
        # since it is a heads-up, the dealer posts the small blind, and the non-dealer places the big blind
        # The small blind is usually equal to half of the big blind. 
        # The big blind is equal to the minimum bet.
        big_blind = PokerConfig.CONFIG['small_bet']
        small_blind = big_blind/2.0
        self.players_info[0]['chips'] -= big_blind
        self.pot += big_blind
        self.players_info[1]['chips'] -= small_blind  # dealer/button
        self.pot += small_blind
        if Config.USER['debug']['enabled']:
            self.debug_file.write(self.players_info[1]['id']+": posts small blind "+str(small_blind)+"\n")
            self.debug_file.write(self.players_info[0]['id']+": posts big blind "+str(big_blind)+"\n")

        ### Starting match

        self.rounds = [[], [], [], []]

        if Config.USER['debug']['enabled']:
            self.debug_file.write("*** HOLE CARDS ***\n")
        self.round_id = 0 # preflop
        result = self._run_poker_round(starter_player_index = 1, initial_bet = small_blind, default_bet = PokerConfig.CONFIG['small_bet'])
        if result == "next_round":
            if Config.USER['debug']['enabled']:
                self.debug_file.write("*** FLOP *** "+str(self.point.board_cards_[:3])+"\n")
            self.round_id = 1 # flop
            result = self._run_poker_round(starter_player_index = 0, initial_bet = 0.0, default_bet = PokerConfig.CONFIG['small_bet'])
        if result == "next_round":
            if Config.USER['debug']['enabled']:
                self.debug_file.write("*** TURN *** "+str(self.point.board_cards_[:4])+"\n")
            self.round_id = 2 # turn
            result = self._run_poker_round(starter_player_index = 0, initial_bet = 0.0, default_bet = PokerConfig.CONFIG['big_bet'])
        river_bet = 0.0
        river_default_bet = PokerConfig.CONFIG['big_bet']
        river_starter_player_index = 0

        if result == "next_round":
            if Config.USER['debug']['enabled']:
                self.debug_file.write("*** RIVER *** "+str(self.point.board_cards_)+"\n")
            self.round_id = 3 # river
            result = self._run_poker_round(starter_player_index = river_starter_player_index, initial_bet = river_bet, default_bet = river_default_bet)
        
        showdown_happened = False
        if result == "next_round": # showdown
            showdown_happened = True
            if Config.USER['debug']['enabled']:
                self.debug_file.write("*** SHOW DOWN ***\n")
                self.debug_file.write(self.players_info[0]['id']+": shows "+str(self.players_info[0]['match_state'].hole_cards)+" (HS: "+str(self.players_info[0]['match_state'].hand_strength[3])+")\n")
                self.debug_file.write(self.players_info[1]['id']+": shows "+str(self.players_info[1]['match_state'].hole_cards)+" (HS: "+str(self.players_info[1]['match_state'].hand_strength[3])+")\n")
            player0_hs = self.players_info[0]['match_state'].hand_strength[3]
            player1_hs = self.players_info[1]['match_state'].hand_strength[3]
            if player0_hs > player1_hs:
                self.players_info[0]['chips'] += self.pot
                if Config.USER['debug']['enabled']:
                    self.debug_file.write(self.players_info[0]['id']+" collected "+str(self.pot)+" from main pot\n")
                showdown_winner = 0
            elif player0_hs < player1_hs:
                self.players_info[1]['chips'] += self.pot
                if Config.USER['debug']['enabled']:
                    self.debug_file.write(self.players_info[1]['id']+" collected "+str(self.pot)+" from main pot\n")
                showdown_winner = 1
            else:
                self.players_info[0]['chips'] += self.pot/2.0
                self.players_info[1]['chips'] += self.pot/2.0
                if Config.USER['debug']['enabled']:
                    self.debug_file.write("Draw! The players shared "+str(self.pot)+" from main pot\n")
                showdown_winner = -1
        if result == "player_folded":
            if Config.USER['debug']['enabled']:
                if self.players_info[0]['folded']:
                    last_player = self.players_info[1]['id']
                else:
                    last_player = self.players_info[0]['id']
                self.debug_file.write(last_player+" collected "+str(self.pot)+" from pot\n")
                self.debug_file.write(last_player+": doesn't show hand\n")

        if Config.USER['debug']['enabled']:
            self.debug_file.write("*** SUMMARY ***\n")
            self.debug_file.write("Total pot "+str(self.pot)+" | Rake 0\n")
            self.debug_file.write("Board "+str(self.point.board_cards_)+"\n")
            if self.players_info[0]['folded']:
                status0 = "folded"
                status1 = "collected "+str(self.pot)
            elif self.players_info[1]['folded']:
                status0 = "collected "+str(self.pot)
                status1 = "folded"
            elif showdown_winner == 0:
                status0 = "showed and won "+str(self.pot)
                status1 = "showed and lost"
            elif showdown_winner == 1:
                status0 = "showed and lost"
                status1 = "showed and won "+str(self.pot)
            elif showdown_winner == -1:
                status0 = "showed and won "+str(self.pot/2.0)
                status1 = "showed and won "+str(self.pot/2.0)
            else:
                raise ValueError("Unrecognized game final status.")

            self.debug_file.write("Seat 1: "+self.players_info[0]['id']+" "+status0+"\n")
            self.debug_file.write("Seat 2: "+self.players_info[1]['id']+" "+status1+"\n")

            self.debug_file.write("\n\n### Point Information: "+str(self.point)+"\n")

        player_actions = self.players_info[sbb_position]['match_state'].actions
        opponent_actions = self.players_info[opponent_position]['match_state'].actions
        self._get_opponent_model_for_team().update_overall_agressiveness(self.round_id, player_actions, opponent_actions, self.point.label_, showdown_happened)
        if self.opponent.opponent_id == 'hall_of_fame':
            self._get_opponent_model_for_hall_of_fame().update_overall_agressiveness(self.round_id, opponent_actions, player_actions, self.point.label_, showdown_happened)

        if self.team.opponent_id == 'bayesian_opponent' or self.team.opponent_id == 'sbb_bayesian_opponent':
            self.team.update_opponent_actions(opponent_actions)
        if self.opponent.opponent_id == 'bayesian_opponent' or self.opponent.opponent_id == 'sbb_bayesian_opponent':
            self.opponent.update_opponent_actions(player_actions)

        if self.is_training:
            original_player_actions =  [PokerConfig.CONFIG['inverted_action_mapping'][a] for a in player_actions]
            if Config.USER['reinforcement_parameters']['environment_parameters']['weights_per_action']:
                bin_label = DiversityMaintenance.define_bin_for_actions(original_player_actions)
                self.team.action_sequence_['encoding_for_pattern_of_actions_per_match'].append(bin_label)

        sbb_chips = self.players_info[sbb_position]['chips']
        opponent_chips = self.players_info[opponent_position]['chips']

        normalized_value = self._normalize_winning(float(sbb_chips))

        if Config.USER['debug']['enabled']:
            self.debug_file.write("\n\n### Result Information: ")
            self.debug_file.write("\nmatch: "+str(self.match_id))
            self.debug_file.write("\nsbb_chips: "+str(sbb_chips))
            self.debug_file.write("\nopponent_chips: "+str(opponent_chips))
            self.debug_file.write("\nnormalized_value: "+str(normalized_value))

        self.point.teams_results_.append(normalized_value)

        self._get_chips_for_team().append(normalized_value)
        if self.opponent.opponent_id == "hall_of_fame":
            self._get_chips_for_hall_of_fame().append(self._normalize_winning(float(opponent_chips)))

        if Config.USER['debug']['enabled']:
            self.debug_file.close()

        return normalized_value

    def _run_poker_round(self, starter_player_index, initial_bet, default_bet):
        last_action = None
        current_index = starter_player_index
        bet = initial_bet
        last_action_was_a_bet = False
        while True:
            opponent_actions = self.players_info[self.opponent_indeces[current_index]]['match_state'].actions
            action = self._execute_player(self.players_info[current_index]['player'], 
                self.players_info[current_index]['match_state'], bet, opponent_actions, current_index)
            self.rounds[self.round_id].append(action)

            if action == 'f':
                if self.players_info[current_index]['key'] == 'team' and not self.is_training and self.round_id == 0:
                    self.players_info[current_index]['player'].extra_metrics_['played_last_hand'] = False
                if Config.USER['debug']['enabled']:
                    self.debug_file.write(self.players_info[current_index]['id']+": folds (pot: "+str(self.pot)+")\n")
                self.players_info[self.opponent_indeces[current_index]]['chips'] += self.pot
                self.players_info[current_index]['folded'] = True
                return "player_folded"
            elif action == 'c':
                self.players_info[current_index]['chips'] -= bet
                self.pot += bet
                if Config.USER['debug']['enabled']:
                    self.debug_file.write(self.players_info[current_index]['id']+": calls "+str(bet)+" (pot: "+str(self.pot)+")\n")
                bet = 0.0
                if last_action_was_a_bet:
                    return "next_round"
                else:
                    last_action_was_a_bet = True
            elif action == 'r':
                self.players_info[current_index]['chips'] -= bet
                self.pot += bet
                bet = default_bet
                self.players_info[current_index]['chips'] -= bet
                self.pot += bet
                if Config.USER['debug']['enabled']:
                    self.debug_file.write(self.players_info[current_index]['id']+": raises "+str(default_bet)+" (pot: "+str(self.pot)+")\n")
                last_action_was_a_bet = False
            else:
                raise ValueError("Invalid action.")

            current_index = self.opponent_indeces[current_index]

    def _valid_actions(self):
        valid = [0, 1]

        max_raises_overall = MatchState.MAX_BETS

        # check if can raise
        if self.round_id == 0:
            max_raises = max_raises_overall-1
        else:
            max_raises = max_raises_overall
        raises = 0
        for action in self.rounds[self.round_id]:
            if action == 'r':
                raises += 1
        if raises < max_raises: 
            valid.append(2)
        return valid

    def _execute_player(self, player, match_state, bet, opponent_actions, current_index):
        if match_state.player_key == 'team' and not player.opponent_id == 'bayesian_opponent' and not player.opponent_id == 'bayesian_tester':
            inputs = match_state.inputs_for_team(self.pot, bet, self._get_chips_for_team(), self.round_id)
            inputs += self._get_opponent_model_for_team().inputs(match_state.actions, opponent_actions)
        else:
            if player.opponent_id == 'hall_of_fame':
                inputs = match_state.inputs_for_team(self.pot, bet, self._get_chips_for_hall_of_fame(), self.round_id)
                inputs += self._get_opponent_model_for_hall_of_fame().inputs(match_state.actions, opponent_actions)
            else:
                inputs = match_state.inputs_for_rule_based_opponents(bet, self.round_id)

        if Config.USER['debug']['enabled']:
            if match_state.player_key == 'team' or self.opponent.opponent_id == 'hall_of_fame':
                self.debug_file.write("    >> registers: "+str([(p.program_id_, [round_value(r, 2) for r in p.general_registers]) for p in player.programs])+"\n")
            self.debug_file.write("    >> inputs: "+str(inputs)+"\n")
        action = player.execute(self.point.point_id_, inputs, self._valid_actions(), self.is_training)
        if Config.USER['debug']['enabled']:
            if match_state.player_key == 'team' or self.opponent.opponent_id == 'hall_of_fame':
                self.debug_file.write("    << program: "+str(player.last_selected_program_)+"\n")

        if action is None:
            action = 1

        if match_state.player_key == 'team' and self.is_training:
            player.action_sequence_['encoding_for_actions_per_match'].append(str(action))
        
        action = PokerConfig.CONFIG['action_mapping'][action]

        if match_state.player_key == 'team' and self.is_training:
            player.action_sequence_['encoding_custom_info_per_match'].append(str(DiversityMaintenance.define_bin_for_value(match_state.hand_strength[self.round_id], is_normalized = True)))
            player.action_sequence_['encoding_custom_info_per_match'].append(str(DiversityMaintenance.define_bin_for_value(match_state.effective_potential[self.round_id], is_normalized = True)))
            player.action_sequence_['encoding_custom_info_per_match'].append(str(action))

        match_state.actions.append(action)
        return action

    def _get_opponent_model_for_team(self):
        opponent_id = self.opponent.opponent_id
        if opponent_id not in self.team.opponent_model:
            self.team.opponent_model[opponent_id] = OpponentModel()
        return self.team.opponent_model[opponent_id]

    def _get_chips_for_team(self):
        opponent_id = self.opponent.opponent_id
        if opponent_id not in self.team.chips:
            self.team.chips[opponent_id] = []
        return self.team.chips[opponent_id]

    def _get_opponent_model_for_hall_of_fame(self):
        opponent_id = self.team.team_id_
        if opponent_id not in self.opponent.opponent_model:
            self.opponent.opponent_model[opponent_id] = OpponentModel()
        return self.opponent.opponent_model[opponent_id]

    def _get_chips_for_hall_of_fame(self):
        opponent_id = self.team.team_id_
        if opponent_id not in self.opponent.chips:
            self.opponent.chips[opponent_id] = []
        return self.opponent.chips[opponent_id]

    def _normalize_winning(self, value):
        max_winning = MatchState.maximum_winning()
        max_losing = -max_winning
        return (value - max_losing)/float(max_winning - max_losing)